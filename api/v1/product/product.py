import logging.config
from typing import List
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, Response, Depends, Header,APIRouter
from fastapi.responses import JSONResponse
from db.db_conf import get_db
from schemas.request_schemas.ping_schema import PingRequest
from models.product import Product
from sqlalchemy.orm import Session
from models.user import User
import logging
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from pydantic import BaseModel
from fastapi.exceptions import HTTPException
from typing import Optional, List
from crud.product_crud import product_crud 
from dotenv import load_dotenv
import os
import requests
import datetime
from tasks.update_product import update_products_task
from models import *
from sqlalchemy.sql import func, desc
from models.warehouses import Warehouse
from models.product import Product
from typing import List
from sqlalchemy.sql import func
from auth.auth import get_userdata_secure


load_dotenv()

logger = logging.getLogger(__name__)

# @app.post('/ping')
# def ping(request: PingRequest, db:Session=Depends(get_db)):
#     logger.info(f"ping {request.text}")
#     ping = Ping(text=request.text)
#     db.add(ping)
#     db.commit()
#     return True

class ProductCreate(BaseModel):
    supply_article: Optional[str]
    wb_article: Optional[str]
    barcode: Optional[str]
    cost_price: Optional[float]
    mono_items: Optional[int]
    box_items: Optional[int]
    demand: Optional[int]
    warehouse_amount: Optional[int]
    shipping_amount: Optional[int]
    production_amount: Optional[int]
    wb_warehouse_amount: Optional[int]
    commision_percentage: Optional[int]
    logistics_fee: Optional[float]
    tax_fee_percentage: Optional[float]
    wb_price: Optional[float]
    fake_wb_price: Optional[float]
    discount: Optional[float]

    plan_pallet: Optional[int]
    image_url: Optional[str]
    

class ProductPatch(BaseModel):
    id: int
    supply_article: Optional[str]
    wb_article: Optional[str]
    wb_price: Optional[float]
    barcode: Optional[str]
    cost_price: Optional[float]
    mono_items: Optional[int]
    box_items: Optional[int]
    demand: Optional[int]
    warehouse_amount: Optional[int]
    shipping_amount: Optional[int]
    production_amount: Optional[int]
    wb_warehouse_amount: Optional[int]
    plan_pallet: Optional[int]
    commision_percentage: Optional[int]
    logistics_fee: Optional[float]
    tax_fee_percentage: Optional[float] 

class ProductModel(ProductCreate):
    id: int

    class Config:
        orm_mode = True


router = SQLAlchemyCRUDRouter(
    schema=ProductModel,
    create_schema=ProductCreate,
    db_model=Product,
    db=get_db,
    prefix='product'
)



@router.patch('')
def patch_product(request: ProductPatch, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id==request.id).first()
    if not product:
        return HTTPException(status_code=400, detail={'error': 'no such product'})
    delattr(request,'id')
    for var,value in vars(request).items():
        print(var, value)
        if value or value is False or value==0:
            setattr(product, var, value)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

class UnitProduct(BaseModel):
    id: int
    supply_article: str
    wb_article: str
    barcode: str
    cost_price: Optional[float]
    wb_price: Optional[float]
    logistics_fee: Optional[int]
    commision: Optional[int]
    fee: Optional[int]
    profit: Optional[float]
    margin: Optional[int]
    rent: Optional[int]
    plan_pallet: Optional[int]=0


    fake_wb_price: Optional[float]
    discount: Optional[float]


unit_router = APIRouter(
    prefix="/unit",
    tags=["unit"],
    responses={404: {"description": "Not found"}},
)

# @unit_router.get('')
# def unit_product(limit=100,skip=0,db: Session = Depends(get_db)):

#     result = []
#     products: List[Product] = product_crud.get_multi(db,skip=0)
#     for product in products:
#         try:
#             commision=product.wb_price*product.commision_percentage/100
#             fee = product.wb_price*product.tax_fee_percentage/100
#             profit = product.wb_price - product.cost_price - fee - commision - product.logistics_fee
#             margin = profit/product.wb_price*100
#             rent = profit/product.cost_price*100
#         except Exception:
#             commision,fee,profit,rent, margin =0,0,0,0,0

#         unit = UnitProduct(
#             id=product.id, 
#             supply_article=product.supply_article,
#             wb_article=product.wb_article, barcode=product.barcode, 
#             cost_price=product.cost_price, 
#             wb_price=product.fake_wb_price*(100-product.discount)/100,
#             logistics_fee=product.logistics_fee, 
#             commision=commision,
#             profit=profit,
#             fee=fee,
#             margin=margin,
#             rent=rent,

#             fake_wb_price=product.fake_wb_price,
#             discount=product.discount
#         )
#         result.append(unit)
#     return result





@unit_router.get('/update_product_info')
def update_info(db: Session = Depends(get_db)):
    update_products_task(db)

class MarginTargetModel(BaseModel):
    nmId: str = '200263560'
    sold_item: int

class SetPriceModel(BaseModel):
    nmId: str = '251666784'
    price: int

def count_margin(product: Product, discount):
    wb_price = round(product.fake_wb_price*(100-discount)/100, 2)
    commision=wb_price*product.commision_percentage/100
    fee = wb_price*product.tax_fee_percentage/100
    profit = wb_price - product.cost_price - fee - commision - product.logistics_fee
    margin = profit/wb_price*100  
    return margin

    
def count_storage(item: Product, db: Session):
    whs = db.query(Stocks).filter(Stocks.nmId==item.wb_article).all()
    storage_sum = 0 
    for w in whs:
        warehouse_tariff: Warehouse = db.query(Warehouse).filter(Warehouse.warehouseName==w.warehouseName).first()
        if warehouse_tariff:
            storage_sum_one = float(warehouse_tariff.boxStorageBase.replace(',','.'))+ (item.volume-1)*float(warehouse_tariff.boxStorageLiter.replace(',','.'))

            warehouses_total_storage = storage_sum_one*w.quantity

            storage_sum+=warehouses_total_storage
    
    return storage_sum
        

def count_delivery(item: Product, warehouse: Warehouse):
    logists_cost  = float(warehouse.boxDeliveryBase.replace(',','.')) + (item.volume-1)*float(warehouse.boxDeliveryLiter.replace(',','.'))
    return logists_cost

def count_full_delivery_cost(delivery_cost,buyoutsPercent):
    backwards_cost = 50
    return delivery_cost + backwards_cost * (1 - buyoutsPercent / 100)

fee =0.07
    
def calculate_margin(nmId,sold_items: int, db: Session):
    item_warehouse = db.query(Stocks).filter(Stocks.nmId==nmId).order_by(desc(Stocks.quantity)).limit(1).first()
    
    item: Product = db.query(Product).filter(Product.wb_article==nmId).first()

    storage_sum = count_storage(item, db)

    warehouse_tariff = db.query(Warehouse).filter(Warehouse.warehouseName==item_warehouse.warehouseName).first()

    delivery_cost = count_delivery(item, warehouse_tariff)
    buyoutsPercent = db.query(Stats).filter(Stats.nmId==nmId).order_by(desc(Stats.date)).limit(1).first()
    
    if not buyoutsPercent:
        buyoutsPercent=0.9
    else:
        if buyoutsPercent.buyoutsPercent < 70:
            avg = db.query(func.avg(Stats.buyoutsPercent).label('average')).filter(Stats.nmId==nmId).first()
            buyoutsPercent = avg.average
        else:
            buyoutsPercent = buyoutsPercent.buyoutsPercent
        
            
    full_delivery_cost = 0

    full_delivery_cost = count_full_delivery_cost(delivery_cost,buyoutsPercent)


    promo_stats: PromoStats = db.query(PromoStats).filter(PromoStats.nmId==nmId).order_by(desc(PromoStats.date)).limit(1).first()
 
    promo_cost = promo_stats.sum if promo_stats else 0 

    profit_on_one = item.wb_price  - item.cost_price - full_delivery_cost - (item.cost_price*item.commision_percentage) - item.wb_price*fee
    
    profit_total = profit_on_one*sold_items

    profit =  profit_total - storage_sum - promo_cost 


    margin = profit/(item.wb_price*sold_items)

    return round(profit, 2), round(margin,2)*100

@unit_router.post('/count_margin')
def margin_target(request: MarginTargetModel,db: Session = Depends(get_db)):
    margin, profit = calculate_margin(request.nmId, request.sold_item, db)
    return margin, profit



@unit_router.post('/set_price')
def margin_target(request: SetPriceModel,user: User=Depends(get_userdata_secure),db: Session = Depends(get_db)):
    # margin, profit = calculate_margin(request.nmId, request.sold_item, db)
    price = request.price*2
    discount = 50
    # result =  requests.post("https://discounts-prices-api.wildberries.ru/api/v2/upload/task",headers={
    #     'Authorization': user.token
    # }, json={"data": [{"nmID": int(request.nmId), "price": price, "discount": discount}]})
    # print(result.json())
    # return result.json()

    return price, discount


