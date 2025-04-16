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
from time import sleep
from models import Stats
logging.config.dictConfig(LOGGING_CONFIG)
from sqlalchemy.sql import func
from models import Product

logger = logging.getLogger(__name__)

def update_stats(db: Session, days=365) -> None:
    try:
        users = db.query(User).all()

        stats_exist = db.query(Stats).all()
        for stat_exist in stats_exist:
            db.delete(stat_exist)
        db.commit()

        for user in users:
            base = datetime.datetime.today()
            date_list = [(base - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(1,days)]
            for date in date_list:
                start = f"{date} 0:00:00"
                end = f"{date} 23:59:59"

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
                stats = requests.post("https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail", headers={
                    'Authorization': user.token
                }, json=body)

                repeat_index = 0
                while stats.status_code !=200:
                    if repeat_index==5:
                        print(f"breaking date {date}")
                        break
                    print("SLEEPING..." )
                    print(stats.json())
                    sleep(60)
                    stats = requests.post("https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail", headers={
                        'Authorization': user.token
                    }, json=body)
                    repeat_index+=1
                    print("SLEEPING...")
                
                stats = stats.json()
                i = 0
                for card in stats['data']['cards']:
                    # existing_stat = db.query(Stats).filter(func.date_trunc('day', Stats.date)==func.date_trunc('day', date), Stats.user_id==user.id, Stats.nmId==card['nmID']).first()
                    db_stat = Stats()
                    # if existing_stat:
                    #     print("STAT EXISTS")
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
                    db_stat.user_id = user.id

                    prodcut = db.query(Product).filter(Product.wb_article==str(card['nmID'])).first()
                    db_stat.product_id = prodcut.id if prodcut else None
                    db.add(db_stat)
                    db.commit()
                    i+=1
                    print(i)
                print("SAVED I")

                    # logger.info(f"SAVING {date}")
        print("SAVED")   

    except Exception as e:
        print(e, "ERROR HERE!")
        logger.error(e)
        