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
from auth.auth import get_user_secure
from schemas.response_schemas.secured import SecuredResponse
import json
from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi_utils.session import FastAPISessionMaker
import requests 
import datetime
from asyncio import sleep
from models import Stats, Stocks

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def update_stocks(db: Session) -> None:
    try:
        print("HM")
        users = db.query(User).all()
        print(1)
        for user in users:
            stocks = requests.get("https://statistics-api.wildberries.ru/api/v1/supplier/stocks?dateFrom=2023-12-10", headers={
                'Authorization': user.token
            })
            repeat_index = 0
            while stocks.status_code !=200:
                if repeat_index==3:
                    break
                sleep(60)
                stocks = requests.get("https://statistics-api.wildberries.ru/api/v1/supplier/stocks?dateFrom=2023-12-10", headers={
                    'Authorization': user.token
                })
                repeat_index+=1
            stocks = stocks.json()
            for stock in stocks:
                existing_stock: Stocks =  db.query(Stocks).filter(Stocks.warehouseName==stock['warehouseName'], Stocks.nmId==stock['nmId']).first()
                if existing_stock:
                    logger.info(f"UPDATING {existing_stock.id}")
                db_stock = existing_stock if existing_stock else Stocks()
                db_stock.lastChangeDate = stock['lastChangeDate']
                db_stock.warehouseName = stock['warehouseName']
                db_stock.supplierArticle = stock['supplierArticle']
                db_stock.nmId = stock['nmId']
                db_stock.barcode = stock['barcode']
                db_stock.quantity = stock['quantity']
                db_stock.inWayToClient = stock['inWayToClient']
                db_stock.inWayFromClient = stock['inWayFromClient']
                db_stock.quantityFull = stock['quantityFull']
                db_stock.techSize = stock['techSize']
                db_stock.Price = stock['Price']
                db_stock.Discount = stock['Discount']
                db_stock.isSupply = stock['isSupply']
                db_stock.isRealization = stock['isRealization']
                db_stock.SCCode = stock['SCCode']
                db_stock.user_id = user.id
                logger.info("saving stock")
                db.add(db_stock)
                db.commit()
                # print("SAVED")

    except Exception as e:
        print(e)
        logger.error(e)
        