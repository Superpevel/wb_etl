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
from time import sleep
import platform
from tasks.update_stats import update_stats
from tasks.update_stocks import update_stocks
from tasks.update_promo_stats import update_adv_stats
from tasks.update_adv_company import update_adv_company
from tasks.update_index import update_localization_index
from fastapi import BackgroundTasks
from crud.product_crud import product_crud
from api.api import router as api_router
from models import Product

load_dotenv()


database_uri = os.environ.get('DATABASE_URL')

sessionmaker = FastAPISessionMaker(database_uri)


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()
origins = ["*"]
app.include_router(api_router)

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

        


def update_orders(db: Session, date_from) -> None:
    print("ha")
    try:
        users = db.query(User).all()
        for user in users:
            orders = db.query(Order).filter(User.id==user.id).all()
            for order in orders:
                db.delete(order)
            db.commit()

            orders = requests.get(f"https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={date_from}", headers={
                'Authorization': user.token
            })

            repeat_index = 0
            while orders.status_code !=200:
                if repeat_index==5:
                    print(f"breaking date ")
                    break
                sleep(60)
                orders = requests.get(f"https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={date_from}", headers={
                    'Authorization': user.token
                })
                repeat_index+=1
            
            
            orders = orders.json()

            for order in orders:
                try:
                    exist_order = db.query(Order).filter(Order.gNumber==order['gNumber'], Order.srid==order['srid']).first()
                    if not exist_order:
                        nmId= order['nmId']
                        db_order = Order(**order)
                        db_order.user_id = user.id
                        # print(product_crud.id_product_by_wb_article(db, nmId), 'looking')
                    
                        prodcut = db.query(Product).filter(Product.wb_article==str(nmId)).first()
                        if prodcut:
                            db_order.product_id = prodcut.id
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

def update_key_word_stat(db: Session, from_time, to) -> None:
    try:
        users = db.query(User).all()
        orders = db.query(KeyWordsStats).all()
        for order in orders:
            db.delete(order) 
        db.commit()
    
        for user in users:
            promos_db: List[Promo] = db.query(Promo).filter(Promo.user_id==user.id).all()
            for promo_db in promos_db:
                keyword_stat = requests.get(f"https://advert-api.wildberries.ru/adv/v0/stats/keywords?advert_id={promo_db.advertId}&from={from_time}&to={to}", headers={
                    'Authorization': user.token
                })
                repeat_index = 0
                while keyword_stat.status_code !=200:
                    if repeat_index==5:
                        print(f"breaking date ")
                        break
                    sleep(60)
                    keyword_stat = requests.get(f"https://advert-api.wildberries.ru/adv/v0/stats/keywords?advert_id={promo_db.advertId}", headers={
                        'Authorization': user.token
                    })
                    repeat_index+=1

                keyword_stat = keyword_stat.json()
                for date_stat in keyword_stat['keywords']:
                    for key_word in date_stat['stats']:
                        # exist = db.query(KeyWordsStats).filter(KeyWordsStats.date==date_stat['date'], KeyWordsStats.user_id==user.id, KeyWordsStats.advert_id==promo_db.advertId, KeyWordsStats.keyword==key_word['keyword']).first()
                        # if exist:
                        #     logger.info("ALREADY EXISTS")
                        #     continue
                        db_ks = KeyWordsStats()
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
        

def update_everything():
    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=6)

    with sessionmaker.context_session() as db:
        try:
            print("STARTING!")
            update_adv_company(db=db) # add repeat
            print("FINISH PARSING ADV COMPANIES")
            update_adv_stats(db=db) # add repeat
            print("FINISH PARSING ADV STATS")
            update_stats(db=db) # add repeat 
            print("FINISH PARSING STATS")

            update_stocks(db=db) # add repeat
            print("FINISH PARSING STOCKS")

            update_orders(db, week_ago)
            print("FINISH PARSING ORDERS")

            update_key_word_stat(db=db, from_time=week_ago, to=today)
            print("FINISHED TASKS")
        except Exception as e:
            logger.error(f'ERROR adv {e}')



# @app.on_event("startup")
# @repeat_every(seconds=60*60*12)  # 1 hour
def update_everything_task() -> None:
    update_everything()


    
@app.get('/start_update')
def get_start_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_everything)
    return {"message": "Task sent in the background"}


@app.get('/localization_index')
def get_start_update():
    with sessionmaker.context_session() as db:
        update_localization_index(db)
    return {"message": "Task sent in the background"}



# def clear_stats(db: Session):
#     users = db.query(User).all()
#     for user in users:
#         base = datetime.datetime.today()
#         date_list = [(base - datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(1,10)]
#         for date in date_list:
#             existing_stats: List[Stats] = db.query(Stats).filter(func.date_trunc('day', Stats.date)==date, Stats.user_id==user.id).all()
#             for stat in existing_stats:
#                 dubs = db.query(Stats).filter(Stats.id !=stat.id, func.date_trunc('day', Stats.date)==func.date_trunc('day', stat.date), Stats.user_id==user.id, Stats.vendorCode==stat.vendorCode).all()
#                 print(dubs, "DUBS")
#                 if dubs:
#                     for dub in dubs:
#                         print("DUBLICATED!")
#                         db.delete(dub)
#                         db.commit()


# @app.on_event("startup")
# @repeat_every(seconds=60*60)  # 1 hour
# def clear_dubs_task() -> None:
#     with sessionmaker.context_session() as db:
#         try:
#             print("START")
#             clear_stats(db=db)
#             print("FINISHED!")
#         except Exception as e:
#             print('ERROR',e)
        
if __name__ == "__main__":
    # print( platform.platform())
    if 'macOS' in platform.platform():
        print("AS")
        uvicorn.run('main:app', host="0.0.0.0", port=8008, reload=True, debug=True)
    else:
        uvicorn.run('main:app', host="0.0.0.0", port=8008, reload=False, debug=False)



