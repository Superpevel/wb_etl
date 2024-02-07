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
from models import Order, Promo, PromoStats, Stats, Stocks, KeyWordsStats
import datetime
from dateutil.parser import parse
from sqlalchemy import Date, cast
from sqlalchemy.sql import func
from asyncio import sleep
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
    try:
        users = db.query(User).all()
        for user in users:
            promos: List[Promo] = db.query(Promo).filter(Promo.user_id==user.id).all()
            body = []
            for promo in promos:
                if promo.status in [9,11]:
                    base = datetime.datetime.today()
                    date_list = [(base - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(90)]
                    body.append({
                        'id': promo.advertId,
                        "dates": date_list
                    })

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
                                exist_stat: PromoStats = db.query(PromoStats).filter(PromoStats.date==date, PromoStats.nmId==int(nm)).first()
                                # if exist_stat:
                                #     logger(f"stat exist! {exist_stat.date} {exist_stat.nmId}")
                                try:
                                    db_stat = PromoStats() if not exist_stat else exist_stat
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
                                    logger.info("ADD PROMO STAT")
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
                            print("ADD PROMO")
                            db.add(db_prom)
                            db.commit()
                except Exception as e:
                    print(e)

            promos_db = db.query(Promo).filter(Promo.user_id==user.id).all()
            promo_ids = [ promo.advertId for promo in promos_db ]
            promo_info = requests.post("https://advert-api.wb.ru/adv/v1/promotion/adverts", headers={
                'Authorization': user.token
            }, json=promo_ids)

            promo_info = promo_info.json()
            
            for info in promo_info:
                exist = db.query(Promo).filter(Promo.advertId==info['advertId']).first()
                exist.company_name = info['name']
                db.add(exist)
                db.commit()
                logger.info(f"UPDATED! promo name {exist.company_name}")
                
    except Exception as e:
        logger.error(f"Company error {e}")
        


def update_orders(db: Session) -> None:
    print("ha")
    try:
        users = db.query(User).all()
        
        for user in users:
            orders = requests.get("https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom=2023-09-19", headers={
                'Authorization': user.token
            }).json()
            for order in orders:
                try:
                    exist_order = db.query(Order).filter(Order.gNumber==order['gNumber'], Order.srid==order['srid']).first()
                    if not exist_order:
                        db_order = Order(**order)
                        db_order.user_id = user.id
                        db.add(db_order)
                        db.commit()
                        logger.info("ORDER SAVED!")
                    else:
                        logger.info("order is alreade saved! " + order['gNumber'])
                except Exception as e:
                    logger.error(e)
            # print(orders[0])
            # print(user.token)
    except Exception as e:
        logger.error(e)
        
    print("TOKEN")
    """Pretend this function deletes expired tokens from the database"""

def update_stats(db: Session) -> None:
    try:
        users = db.query(User).all()
        for user in users:
            base = datetime.datetime.today()
            date_list = [(base - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(1, 30)]
            for date in date_list:
                start = f"{date} 0:00:00"
                end = f"{date} 23:59:59"
                print(start, end)
                existing_stat = db.query(Stats).filter(Stats.date==date).first()
                if existing_stat:
                    print(f"Already exists {date}")
                else:
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
                        if repeat_index==3:
                            print(f"breaking date {date}")
                            break
                        print("REPATING Request")
                        sleep(10)
                        stats = requests.post("https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail", headers={
                            'Authorization': user.token
                        }, json=body)
                        repeat_index+=1
                    
                    stats = stats.json()
                    for card in stats['data']['cards']:
                        db_stat = Stats()
                        db_stat.date = date
                        db_stat.nmId = card['nmID']
                        db_stat.vendorCode = card['vendorCode']
                        db_stat.brandName = card['brandName']


                        db_stat.openCardCount  = card['statistics']['selectedPeriod']['openCardCount']
                        db_stat.addToCartCount  = card['statistics']['selectedPeriod']['addToCartCount']
                        
                        db_stat.ordersCount  = card['statistics']['selectedPeriod']['ordersCount']
                        db_stat.ordersSumRub  = card['statistics']['selectedPeriod']['ordersSumRub']
                        db_stat.buyoutsCount  = card['statistics']['selectedPeriod']['buyoutsCount']

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
        

def update_key_word_stat(db: Session) -> None:
    try:
        users = db.query(User).all()
        for user in users:
            promos_db: List[Promo] = db.query(Promo).filter(Promo.user_id==user.id).all()
            for promo_db in promos_db:
                keyword_stat = requests.get(f"https://advert-api.wb.ru/adv/v2/auto/daily-words?id={promo_db.advertId}", headers={
                    'Authorization': user.token
                })

                keyword_stat = keyword_stat.json()

                for date_stat in keyword_stat:
                    for key_word in date_stat['stat']:
                        exist = db.query(KeyWordsStats).filter(KeyWordsStats.date==date_stat['date'], KeyWordsStats.user_id==user.id, KeyWordsStats.advert_id==promo_db.advertId, KeyWordsStats.keyword==key_word['keyword']).first()
                        # if exist:
                        #     logger.info("ALREADY EXISTS")
                        #     continue
                        db_ks = KeyWordsStats() if not exist else exist
                        db_ks.advert_id = promo_db.advertId
                        db_ks.keyword = key_word['keyword']
                        db_ks.clicks = key_word['clicks']
                        db_ks.views = key_word['views']
                        db_ks.ctr = key_word['ctr']
                        db_ks.sum = key_word['sum']
                        db_ks.date = date_stat['date']
                        db.add(db_ks)
                        db.commit()
                        logger.info(f"ADD NEW KEY WORD STAT {db_ks.date} {db_ks.advert_id}")
    except Exception as e:
        print(e, 'some error here!')
        

def update_stocks(db: Session) -> None:
    try:
        users = db.query(User).all()
        for user in users:
            stocks = requests.get("https://statistics-api.wildberries.ru/api/v1/supplier/stocks?dateFrom=2023-12-10", headers={
                'Authorization': user.token
            })
            repeat_index = 0
            while stocks.status_code !=200:
                if repeat_index==3:
                    break
                sleep(10)
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
                logger.info("saving stock")
                db.add(db_stock)
                db.commit()
                # print("SAVED")

    except Exception as e:
        logger.error(e)
        


@app.on_event("startup")
@repeat_every(seconds=60*60*3)  # 1 hour
def update_adv_company_task() -> None:
    with sessionmaker.context_session() as db:
        try:
            update_adv_company(db=db)
        except Exception as e:
            logger.error(f'ERROR adv {e}')


@app.on_event("startup")
@repeat_every(seconds=60*60*12+60*5)  # 1 hour
def update_promo_stats_task() -> None:
    with sessionmaker.context_session() as db:
        try:
            print("START UPDATING STATS")
            update_adv_stats(db=db)
        except Exception as e:
            print('error',e)


@app.on_event("startup")
@repeat_every(seconds=60*60*4)  # 1 hour
def update_stats_task() -> None:
    try:
        with sessionmaker.context_session() as db:
            update_stats(db=db)
    except Exception as e:
        print(e, "ERROR")

@app.on_event("startup")
@repeat_every(seconds=60*60*4)  # 1 hour
def update_stats_task() -> None:
    try:
        with sessionmaker.context_session() as db:
            update_stocks(db=db)
    except Exception as e:
        print(e)


@app.on_event("startup")
@repeat_every(seconds=60*60*5)  # 1 hour
def update_orders_task() -> None:
    try:
        with sessionmaker.context_session() as db:
            update_orders(db=db)
    except Exception as e:
        print(e)



@app.on_event("startup")
@repeat_every(seconds=60*60*6)  # 1 hour
def update_adv_work_stat_task() -> None:
    with sessionmaker.context_session() as db:
        try:
            update_key_word_stat(db=db)
        except Exception as e:
            print('ERROR',e)


if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8007, reload=True, debug=True)


