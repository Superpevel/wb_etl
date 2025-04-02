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
from models import Stats, PromoStats, Promo, Order
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def update_adv_company(db: Session) -> None:
    try:
        promos_exits = db.query(Promo).all()
        for p in promos_exits:
            print(p)
            db.delete(p)
        db.commit()
        users = db.query(User).all()


        for user in users:

            promos = requests.get("https://advert-api.wb.ru/adv/v1/promotion/count", headers={
                'Authorization': user.token
            })

            repeat_index = 0
            while promos.status_code !=200:
                if repeat_index==5:
                    print(f"breaking")
                    break
                print("sleeping ")
                sleep(60)
                promos = requests.get("https://advert-api.wb.ru/adv/v1/promotion/count", headers={
                    'Authorization': user.token
                })
                repeat_index+=1
    
            # print("HOW?")
            # print(promos.status_code)
            promos = promos.json()

            # print("")
            # print(promos)
            # return
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
                    print(e, user.id, promo)

            promos_db = db.query(Promo).filter(Promo.user_id==user.id).all()
            promo_ids_chunks = chunks([ promo.advertId for promo in promos_db ], 49)
            for promo_ids in promo_ids_chunks:
                promo_info = requests.post("https://advert-api.wb.ru/adv/v1/promotion/adverts", headers={
                    'Authorization': user.token
                }, json=promo_ids)

                promo_info = promo_info.json()
                print(promo_info)
                for info in promo_info:
                    exist: Promo = db.query(Promo).filter(Promo.advertId==info['advertId']).first()
                    exist.company_name = info['name']
                    db.add(exist)
                    db.commit()
                    logger.info(f"UPDATED! promo name {exist.company_name}")
                
    except Exception as e:
        logger.error(f"Company error {e}")