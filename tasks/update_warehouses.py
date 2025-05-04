import logging.config
from typing import List
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, Response, Depends, Header
from fastapi.responses import JSONResponse
from db.db_conf import get_db
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.user import User
import jwt
from logs.logs_config import LOGGING_CONFIG
import logging
from schemas.response_schemas.secured import SecuredResponse
import json
from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi_utils.session import FastAPISessionMaker
import requests 
import datetime
from asyncio import sleep
from models import Stats, Stocks, Product
from models.warehouses import Warehouse

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def update_warehouses(db: Session) -> None:
    user = db.query(User).first()
    now = datetime.datetime.today().strftime('%Y-%m-%d')

    whs = db.query(Warehouse).all()
    for  wh in whs:
        db.delete(wh)
        db.commit()
        
    warehouses = requests.get(f"https://common-api.wildberries.ru/api/v1/tariffs/box?date={now}", 
        headers={
        'Authorization': user.token
    }).json()

    for w in warehouses['response']['data']['warehouseList']:
        warehouse = Warehouse()
        warehouse.boxDeliveryAndStorageExpr = w['boxDeliveryAndStorageExpr']
        warehouse.boxDeliveryBase =  w['boxDeliveryBase']
        warehouse.boxDeliveryLiter =  w['boxDeliveryLiter']
        warehouse.boxStorageBase =  w['boxStorageBase']
        warehouse.boxStorageLiter =  w['boxStorageLiter']
        warehouse.warehouseName =  w['warehouseName']

        db.add(warehouse)
        db.commit()