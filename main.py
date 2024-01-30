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
import os
from dotenv import load_dotenv
from fastapi_utils.session import FastAPISessionMaker
from fastapi_utils.tasks import repeat_every
import requests 
from models import Order, Promo, PromoStats
import datetime
from dateutil.parser import parse
from sqlalchemy import Date, cast
from sqlalchemy.sql import func

load_dotenv()
database_uri = os.environ.get('DATABASE_URL')

sessionmaker = FastAPISessionMaker(database_uri)



load_dotenv()

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()
origins = ["*"]

@app.middleware('http')
def catch_exceptions_middleware(request: Request, call_next):
    try:
        return call_next(request)
    except Exception as e:
        logger.exception(e)
        return Response('Internal server error', status_code=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/secured', response_model=SecuredResponse)
def secured(user: User=Depends(get_user_secure)):
    return user.id

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


def update_adv_stats(db: Session) -> None:
    print("ha")
    try:
        users = db.query(User).all()
        for user in users:
            promos: List[Promo] = db.query(Promo).filter(Promo.user_id==user.id).all()
            body = []
            for promo in promos:
                if promo.status in [9,11]:
                    base = datetime.datetime.today()
                    date_list = [(base - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(30)]
                    body.append({
                        'id': promo.advertId,
                        "dates": date_list
                    })
            print(body)

            promo_stats = requests.post("https://advert-api.wb.ru/adv/v2/fullstats", 
                json=body,
                headers={
                'Authorization': user.token
            }).json()
            result = {}
            for stat in promo_stats:
                advert_id = stat['advertId']
                result.update({advert_id: {}})
                for day in stat['days']:
                    date = parse(day['date']).strftime('%Y-%m-%d')
                    result[advert_id].update({date: {}})
                    for app in day['apps']:
                        for nm in app['nm']:
                            if result[advert_id][date].get(nm['nmId']):
                                result[advert_id][date][nm['nmId']]['clicks']+= nm['clicks']
                                result[advert_id][date][nm['nmId']]['views']+= nm['views']
                                result[advert_id][date][nm['nmId']]['sum']+= nm['sum']
                            else:
                                 result[advert_id][date].update({nm['nmId']: {'clicks': nm['clicks'], 'sum': nm['sum'], 'views': nm['views']}})
            for advCom,dates in result.items():
                try:
                    for date, nms in dates.items():
                        try:
                            for nm, stats in nms.items():
                                pass
                                exist_stat = db.query(PromoStats).filter(PromoStats.date==date, PromoStats.nmId==int(nm)).first()
                                if exist_stat:
                                    print("stat exist!")
                                else:
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
        
# def update_adv_stats(db: Session) -> None:
#     try:
#         print("ALLO")
#         stat: PromoStats = db.query(PromoStats).first()
#         orders = db.query(func.sum(Order.priceWithDisc).label("TotalOrdersSum")).filter(cast(Order.date, Date)== stat.date).first()[0]
#         print(orders)
#         print(stat.date)

#     except Exception as e:
#         print(e)

def update_adv_company(db: Session) -> None:
    print("ha")
    try:
        users = db.query(User).all()
        for user in users:
            promos = requests.get("https://advert-api.wb.ru/adv/v1/promotion/count", headers={
                'Authorization': user.token
            }).json()
            for promo in promos['adverts']:
                try:

                    type = promo['type']
                    status = promo['status']
                    for promo_id in promo['advert_list']:
                        exist_promo = db.query(Promo).filter(Promo.advertId==promo_id['advertId']).first()
                        if exist_promo:
                            print("PROMO ALREADY EXISTS!")
                        else:
                            db_prom  = Promo(user_id=user.id, status=status, type=type, advertId=promo_id['advertId'])
                            db.add(db_prom)
                            db.commit()
                except Exception as e:
                    print(e)
            # print(orders[0])
            # print(user.token)
    except Exception as e:
        print(e)
        
    print("TOKEN")


def remove_expired_tokens(db: Session) -> None:
    print("ha")
    try:
        users = db.query(User).all()
        
        for user in users:
            orders = requests.get("https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom=2023-09-19", headers={
                'Authorization': user.token
            }).json()
            for order in orders:
                try:
                    print("WHy")
                    exist_order = db.query(Order).filter(Order.gNumber==order['gNumber'], Order.srid==order['srid']).first()
                    print("THE HELL!")
                    if not exist_order:
                        db_order = Order(**order)
                        print("ORDER CREATED!")
                        db_order.user_id = user.id
                        db.add(db_order)
                        db.commit()
                        print("ORDER SAVED!")
                    else:
                        print("order is alreade saved! " + order['gNumber'])
                except Exception as e:
                    print(e)
            # print(orders[0])
            # print(user.token)
    except Exception as e:
        print(e)
        
    print("TOKEN")
    """Pretend this function deletes expired tokens from the database"""

# @app.on_event("startup")
# @repeat_every(seconds=60*60)  # 1 hour
# def remove_expired_tokens_task() -> None:
#     with sessionmaker.context_session() as db:
#         remove_expired_tokens(db=db)

# @app.on_event("startup")
# @repeat_every(seconds=60)  # 1 hour
# def update_promo() -> None:
#     with sessionmaker.context_session() as db:
#         update_adv_company(db=db)

@app.on_event("startup")
@repeat_every(seconds=60)  # 1 hour
def update_promo() -> None:
    with sessionmaker.context_session() as db:
        update_adv_stats(db=db)


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8007, reload=True, debug=True)


