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
    door = db.query(Product).filter(Product.id==request.id).first()
    if not door:
        return HTTPException(status_code=400, detail={'error': 'no such door'})
    delattr(request,'id')
    for var,value in vars(request).items():
        print(var, value)
        if value or value is False or value==0:
            setattr(door, var, value)
    db.add(door)
    db.commit()
    db.refresh(door)
    return door

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

@unit_router.get('')
def unit_product(limit=100,skip=0,db: Session = Depends(get_db)):

    result = []
    products: List[Product] = product_crud.get_multi(db,skip=0)
    for product in products:
        try:
            commision=product.wb_price*product.commision_percentage/100
            fee = product.wb_price*product.tax_fee_percentage/100
            profit = product.wb_price - product.cost_price - fee - commision - product.logistics_fee
            margin = profit/product.wb_price*100
            rent = profit/product.cost_price*100
        except Exception:
            commision,fee,profit,rent, margin =0,0,0,0,0

        unit = UnitProduct(
            id=product.id, 
            supply_article=product.supply_article,
            wb_article=product.wb_article, barcode=product.barcode, 
            cost_price=product.cost_price, 
            wb_price=product.fake_wb_price*(100-product.discount)/100,
            logistics_fee=product.logistics_fee, 
            commision=commision,
            profit=profit,
            fee=fee,
            margin=margin,
            rent=rent,

            fake_wb_price=product.fake_wb_price,
            discount=product.discount
        )
        result.append(unit)
    return result


class ShipProduct(BaseModel):
    id: Optional[int]
    supply_article:  Optional[str]
    wb_article: Optional[str]
    barcode: Optional[str]
    demand: Optional[int]
    warehouse_amount: Optional[int]
    wb_warehouse_amount: Optional[int]
    shipping_amount: Optional[int]
    production_amount: Optional[int]

    wb_warehouse_last: Optional[float]
    total_last: Optional[float]
    total_amount: Optional[int]
    plan_pallet: Optional[int]

    wb_warehouse_after_supply_mono_or_box: str
    wb_warehouse_last_after_mono_or_box: str

# @unit_router.get('/shipping')
# def ship_product(limit=100,skip=0,db: Session = Depends(get_db)):
#     wb_warehouse_last,total_last,total_amount  ='0','0','0'
#     wb_warehouse_last_after_mono_or_box= '0'
#     wb_warehouse_last_supply_mono_or_box='0'
#     result = []
#     products: List[Product] = product_crud.get_multi(db,skip=0)
#     for product in products:

#         try:
#             wb_warehouse_last = round(product.wb_warehouse_amount/product.demand, 2) # in weeks
#             total_last = round((product.production_amount+ product.wb_warehouse_amount + product.shipping_amount + product.warehouse_amount)/product.demand*7/30, 2)
#             total_amount = product.wb_warehouse_amount + product.shipping_amount + product.warehouse_amount + product.production_amount
#             print(total_amount)
#         except Exception as e:
#             pass
    
#         try:

#             wb_warehouse_last_after_mono = product.plan_pallet*product.mono_items
#             wb_warehouse_last_after_box = product.plan_pallet*product.box_items

#             wb_warehouse_last_after_mono_or_box = f'{round((wb_warehouse_last_after_mono+product.wb_warehouse_amount)/product.demand,2)}/{round((wb_warehouse_last_after_box+product.wb_warehouse_amount)/product.demand, 2)}'
#             wb_warehouse_last_supply_mono_or_box = f'{wb_warehouse_last_after_mono}/{wb_warehouse_last_after_box}'
#         except Exception:
#             pass


#         unit = ShipProduct(
#             id=product.id, 
#             supply_article=product.supply_article,
#             wb_article=product.wb_article, 
#             barcode=product.barcode, 
#             demand=product.demand,
#             wb_warehouse_amount=product.wb_warehouse_amount,
#             warehouse_amount=product.warehouse_amount,
#             shipping_amount=product.shipping_amount,
#             production_amount=product.production_amount,
#             plan_pallet=product.plan_pallet,
#             wb_warehouse_last=wb_warehouse_last,
#             wb_warehouse_last_after_mono_or_box=wb_warehouse_last_after_mono_or_box,
#             wb_warehouse_after_supply_mono_or_box=wb_warehouse_last_supply_mono_or_box,
#             total_last=total_last,
#             total_amount=total_amount
#         )
#         result.append(unit)
#     return result

@unit_router.get('/update_info')
def update_info(limit=100,skip=0,db: Session = Depends(get_db)):
    users = db.query(User).all()
    for user in users:
        # token = user.token
        headers = {
            'accept': 'application/json',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1OTM5ODYxNCwiaWQiOiIwMTk1Zjg3Yi1iZmM2LTdkMGQtYTQyMS01MzM2ZjliOTA3Y2QiLCJpaWQiOjg1Mzc5MDI0LCJvaWQiOjEzODI0MzIsInMiOjc5MzQsInNpZCI6IjljYzdjMTZhLTQxNmEtNDdmZS1iNzJkLWQ4OTBlMGI2MmE3MyIsInQiOmZhbHNlLCJ1aWQiOjg1Mzc5MDI0fQ.KqEcP8O2Ehp6Cd2qwJzmI71IbMsOQVahzyQgbEMfgJ3batC9nsWdXYh8yTJI5VcQnoQbMzbfPVO5OIKCMO6ytQ',
            'content-type': 'application/json',
            'origin': 'https://dev.wildberries.ru',
            'priority': 'u=1, i',
            'referer': 'https://dev.wildberries.ru/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }

        # params = {
        #     'locale': 'ru',
        # }

        # json_data = {
        #     'settings': {
        #         'cursor': {
        #             'limit': 100,
        #         },
        #         'filter': {
        #             'withPhoto': -1,
        #         },
        #     },
        # }

        # rs = requests.post(
        #     'https://content-api.wildberries.ru/content/v2/get/cards/list',
        #     params=params,
        #     headers=headers,
        #     json=json_data,
        # )

        # # print(rs)
    
        # result = rs.json()
        
        # # print(result)
        # # return
        # for card in result['cards']:
        #     product = db.query(Product).filter(Product.wb_article==str(card['nmID']), Product.supply_article==str(card['vendorCode'])).first()
        #     if not product:
        #         product = Product(
        #             supply_article=str(card['vendorCode']),
        #             wb_article=str(card['nmID']),
        #             barcode=str(card['sizes'][0]['skus'][0]),
        #             # image_url= str(card['photos'][0]),
        #         )
        #         db.add(product)
        #         db.commit()
        #         db.refresh(product)
        #     else:
        #         product_crud.update(db, db_obj=product,  obj_in={
        #             'supply_article': str(card['vendorCode']),
        #             'wb_article': str(card['nmID']),
        #             'barcode': str(card['sizes'][0]['skus'][0]),
        #             # 'image_url': str(card['photos'][0]),
        #         })

        today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        d = datetime.timedelta(days=7)
        week_ago = (datetime.datetime.today()-d).strftime('%Y-%m-%d %H:%M:%S')
        body_2 = {  
            "timezone": "Europe/Moscow",
            "period": {
                "begin": week_ago,
                "end": today
            },
            "orderBy": {
                "field": "ordersSumRub",
                "mode": "asc"
            },
            "page": 1
        }
        rs = requests.post(url='https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail',
                        headers=headers,
                        json=body_2
        )
        result = rs.json()
        for card in result['data']['cards']:
            product = db.query(Product).filter(Product.wb_article==str(card['nmID']), Product.supply_article==str(card['vendorCode'])).first()
            if not product:
                logger.info(f"NO PRODUCT {card}")
                continue

            product_crud.update(db, db_obj=product,  obj_in={
                'demand': card['statistics']['selectedPeriod']['ordersCount'],
                'wb_warehouse_amount': card['stocks']['stocksWb'],
            })

        rs = requests.get(url='https://discounts-prices-api.wildberries.ru/api/v2/list/goods/size/nm',
                        headers=headers,
        )

        result = rs.json()

        for card in result:
            product = db.query(Product).filter(Product.wb_article==str(card['nmId'])).first()
            if not product:
                logger.info(f"NO PRODUCT {card}")
                continue

            product_crud.update(db, db_obj=product,  obj_in={
                'fake_wb_price': card['price'],
                'discount': card['discount'],
                'wb_price': card['price']*(100-card['discount'])/100,
            })

class MarginTargetModel(BaseModel):
    target: int

def count_margin(product: Product, discount):
    wb_price = round(product.fake_wb_price*(100-discount)/100, 2)
    commision=wb_price*product.commision_percentage/100
    fee = wb_price*product.tax_fee_percentage/100
    profit = wb_price - product.cost_price - fee - commision - product.logistics_fee
    margin = profit/wb_price*100  
    return margin

@unit_router.post('/margin_target')
def margin_target(request: MarginTargetModel,db: Session = Depends(get_db)):
    products: List[Product]= db.query(Product).all()
    for product in products:

        discount = 0
        margin = 0
        if count_margin(product,discount) < request.target:
            continue # update discount = 0

        i = 0
        while count_margin(product,discount)>request.target:
            if discount == 100:
                break            
            discount +=1
            i+=1
        
        if discount==0:
            product_crud.update(db, db_obj=product, obj_in={
                'discount': 0,
                'wb_price': product.fake_wb_price
            })
        else:
            print(product.fake_wb_price*(100-discount-1)/100)
            product_crud.update(db, db_obj=product, obj_in={
                'discount': discount-1,
                'wb_price': round(product.fake_wb_price*(100-discount-1)/100, 2)
            })
    
        
        # print(wb_price)
        # wb_price= ['price']*(100-card['discount'])/100,