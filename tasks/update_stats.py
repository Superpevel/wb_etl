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
from models import Stats
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

async def update_stats(db: Session) -> None:
    try:
        users = db.query(User).all()
        for user in users:
            base = datetime.datetime.today()
            date_list = [(base - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(1, 15)]
            for date in date_list:
                start = f"{date} 0:00:00"
                end = f"{date} 23:59:59"
                print(start, end)
                existing_stat = db.query(Stats).filter(Stats.date==date).first()

                body = {
                    "timezone": "Europe/Moscow",
                    "period": {
                        "begin": start,
                        "end": end
                    },
                    "orderBy": {
                        "field": "ordersSumRub",
                        "mode": "asc"
                    },
                    "page": 1
                }
                stats = requests.post("https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail", headers={
                    'Authorization': user.token
                }, json=body)
                repeat_index = 0
                while stats.status_code !=200:
                    if repeat_index==5:
                        print(f"breaking date {date}")
                        break
                    print("REPATING Request")
                    await sleep(10)
                    stats = requests.post("https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail", headers={
                        'Authorization': user.token
                    }, json=body)
                    repeat_index+=1
                
                stats = stats.json()
                for card in stats['data']['cards']:
                    db_stat = Stats() if not existing_stat else existing_stat
                    db_stat.date = date
                    db_stat.nmId = card['nmID']
                    db_stat.vendorCode = card['vendorCode']
                    db_stat.brandName = card['brandName']


                    db_stat.openCardCount  = card['statistics']['selectedPeriod']['openCardCount']
                    db_stat.addToCartCount  = card['statistics']['selectedPeriod']['addToCartCount']
                    
                    db_stat.ordersCount  = card['statistics']['selectedPeriod']['ordersCount']
                    db_stat.ordersSumRub  = card['statistics']['selectedPeriod']['ordersSumRub']
                    db_stat.buyoutsCount  = card['statistics']['selectedPeriod']['buyoutsCount']
                    db_stat.avg_price_rub= card['statistics']['selectedPeriod']['avgPriceRub']
                    db_stat.buyoutsSumRub  = card['statistics']['selectedPeriod']['buyoutsSumRub']
                    db_stat.cancelCount  = card['statistics']['selectedPeriod']['cancelCount']
                    db_stat.cancelSumRub  = card['statistics']['selectedPeriod']['cancelSumRub']

                    db_stat.addToCartPercent  = card['statistics']['selectedPeriod']['conversions']['addToCartPercent']
                    db_stat.cartToOrderPercent  = card['statistics']['selectedPeriod']['conversions']['cartToOrderPercent']
                    db_stat.buyoutsPercent  = card['statistics']['selectedPeriod']['conversions']['buyoutsPercent']

                    db.add(db_stat)
                    db.commit()
                    logger.info(f"SAVING {date}")


    except Exception as e:
        logger.error(e)
        