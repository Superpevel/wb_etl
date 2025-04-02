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
from crud.competitors import competitor_crud 
from dotenv import load_dotenv
import os
import requests
import datetime
from models import Competitor
load_dotenv()

logger = logging.getLogger(__name__)

# @app.post('/ping')
# def ping(request: PingRequest, db:Session=Depends(get_db)):
#     logger.info(f"ping {request.text}")
#     ping = Ping(text=request.text)
#     db.add(ping)
#     db.commit()
#     return True

class CompetitorCreate(BaseModel):
    product_id: Optional[str]
    competitor_nmID: Optional[str]
    # supply_article: Optional[str]
    # wb_article: Optional[str]
    # barcode: Optional[str]
    # cost_price: Optional[float]
    # mono_items: Optional[int]
    # box_items: Optional[int]
    # demand: Optional[int]
    # warehouse_amount: Optional[int]
    # shipping_amount: Optional[int]
    # production_amount: Optional[int]
    # wb_warehouse_amount: Optional[int]
    # commision_percentage: Optional[int]
    # logistics_fee: Optional[float]
    # tax_fee_percentage: Optional[float]
    # wb_price: Optional[float]
    # fake_wb_price: Optional[float]
    # discount: Optional[float]

    # plan_pallet: Optional[int]
    # image_url: Optional[str]
    


class CompetitorModel(CompetitorCreate):
    id: int

    class Config:
        orm_mode = True


competitors_router = SQLAlchemyCRUDRouter(
    schema=CompetitorModel,
    create_schema=CompetitorCreate,
    db_model=Competitor,
    db=get_db,
    prefix='competitor'
)

