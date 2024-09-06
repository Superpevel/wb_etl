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
from models import Stats, PromoStats, Promo, Order
from dateutil import parser
logging.config.dictConfig(LOGGING_CONFIG)
from sqlalchemy.sql import func
from sqlalchemy import Date, cast

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)

def update_adv_stats(db: Session, days=10) -> None:
    try:
        users = db.query(User).all()
        p_stats =  db.query(PromoStats).all()
        for p_stat in p_stats:
            db.delete(p_stat)
        db.commit()
        print("1")
        for user in users:
            promos: List[Promo] = db.query(Promo).filter(Promo.user_id==user.id).all()
            body = []
            if not promos:
                continue
            for promo in promos:
                if promo.status in [9,11]:
                    base = datetime.datetime.today()
                    date_list = [(base - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(days)]
                    body.append({
                        'id': promo.advertId,
                        "dates": date_list
                    })

            promo_stats = requests.post("https://advert-api.wb.ru/adv/v2/fullstats", 
                json=body,
                headers={
                'Authorization': user.token
            })

            repeat_index = 0
            while promo_stats.status_code !=200:
                if repeat_index==5:
                    print(f"breaking")
                    break
                sleep(60)
                promo_stats = requests.post("https://advert-api.wb.ru/adv/v2/fullstats", 
                    json=body,
                    headers={
                    'Authorization': user.token
                })
                repeat_index+=1
    
            promo_stats = promo_stats.json()
            result = {}
    
            for stat in promo_stats:
                advert_id = stat['advertId']
                if not result.get(advert_id):
                    result.update({advert_id: {}})
                for day in stat['days']:
                    if advert_id==18866487:
                        print(date)
                        print(stat['days'])
                    date = parser.parse(day['date']).strftime('%Y-%m-%d')
                    result[advert_id].update({date: {}})
                    for app in day['apps']:
                        for nm in app['nm']:
                            if result[advert_id][date].get(nm['nmId']):
                                result[advert_id][date][nm['nmId']]['clicks']+= nm['clicks']
                                result[advert_id][date][nm['nmId']]['views']+= nm['views']
                                result[advert_id][date][nm['nmId']]['sum']+= nm['sum']
                            else:
                                 result[advert_id][date].update({nm['nmId']: {'clicks': nm['clicks'], 'sum': nm['sum'], 'views': nm['views']}})
            with open('result.json', 'w') as file:
                file.write(json.dumps(result))
            print("3")
            # return
            # # print(result)
            for advCom,dates in result.items():
                try:
                    for date, nms in dates.items():
                        try:
                            for nm, stats in nms.items():
                                # pass
                                # exist_stat: PromoStats = db.query(PromoStats).filter(PromoStats.date==date, PromoStats.nmId==int(nm), PromoStats.nmId==int(nm)).first() ## add advert 
                                # if exist_stat:
                                #     logger(f"stat exist! {exist_stat.date} {exist_stat.nmId}")
                                try:
                                    db_stat = PromoStats()
                                    db_stat.advert_id=advCom
                                    db_stat.clicks=stats['clicks']
                                    db_stat.sum=stats['sum']
                                    db_stat.views=stats['views']
                                    db_stat.nmId=int(nm)    
                                    db_stat.date=date
                                    db_stat.user_id=user.id
                                    orders = db.query(func.sum(Order.priceWithDisc).label("TotalOrdersSum")).filter(cast(Order.date, Date)== db_stat.date).first()
                                    db_stat.date_order_sum = round(orders[0], 2) if orders and orders[0] else None
                                    db_stat.drr =  round(db_stat.sum/db_stat.date_order_sum*100,2) if db_stat.date_order_sum else None
                                    logger.info(f"ADD PROMO STAT {user.id} {advCom}")
                                    db.add(db_stat)
                                    db.commit()
                                except Exception as e:
                                    print(e, 'level 3')
                        except Exception as e:
                            print(e, 'level2')
                            pass
                except Exception as e:
                    print(e, 'level 1')

    except Exception as e:
        print(e)

