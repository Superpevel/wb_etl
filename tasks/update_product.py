from models.user import User
import jwt
from logs.logs_config import LOGGING_CONFIG
import logging
from schemas.response_schemas.secured import SecuredResponse
import json
from fastapi import FastAPI
from sqlalchemy.orm import Session
import requests
from crud.product_crud import product_crud
import datetime
from models import Product
import logging.config
from fastapi import FastAPI, Query, Request, Response, Depends, Header
from db.db_conf import get_db
from sqlalchemy.orm import Session
from models.user import User
import jwt
from logs.logs_config import LOGGING_CONFIG
import logging
import json
from sqlalchemy.orm import Session
import requests 
import datetime
from time import sleep
from models import Stats, PromoStats, Promo, Order, Product
from dateutil import parser
logging.config.dictConfig(LOGGING_CONFIG)
from sqlalchemy.sql import func
from sqlalchemy import Date, cast

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)

def update_products_task(db: Session):
    users = db.query(User).all()
    for user in users:
        # # token = user.token
        headers = {
            'accept': 'application/json',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'authorization': 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1OTM5ODYxNCwiaWQiOiIwMTk1Zjg3Yi1iZmM2LTdkMGQtYTQyMS01MzM2ZjliOTA3Y2QiLCJpaWQiOjg1Mzc5MDI0LCJvaWQiOjEzODI0MzIsInMiOjc5MzQsInNpZCI6IjljYzdjMTZhLTQxNmEtNDdmZS1iNzJkLWQ4OTBlMGI2MmE3MyIsInQiOmZhbHNlLCJ1aWQiOjg1Mzc5MDI0fQ.KqEcP8O2Ehp6Cd2qwJzmI71IbMsOQVahzyQgbEMfgJ3batC9nsWdXYh8yTJI5VcQnoQbMzbfPVO5OIKCMO6ytQ',
            'content-type': 'application/json',
            'origin': 'https://dev.wildberries.ru',
            'priority': 'u=1, i',
            'referer': 'https://dev.wildberries.ru/',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }

        # params = {
        #     'locale': 'ru',
        # }

        # json_data = {
        #     'settings': {
        #         'cursor': {
        #             'limit': 100,
        #         },
        #         'filter': {
        #             'withPhoto': -1,
        #         },
        #     },
        # }

        # rs = requests.post(
        #     'https://content-api.wildberries.ru/content/v2/get/cards/list',
        #     params=params,
        #     headers=headers,
        #     json=json_data,
        # )

        # # print(rs)

        # result = rs.json()
        
        # # print(result)
        # # return
        # for card in result['cards']:
        #     try:
        #         product = db.query(Product).filter(Product.wb_article==str(card['nmID']), Product.supply_article==str(card['vendorCode'])).first()
        #         if not product:
        #             product = Product(
        #                 supply_article=str(card['vendorCode']),
        #                 wb_article=str(card['nmID']),
        #                 barcode=str(card['sizes'][0]['skus'][0]),
        #                 width =  card['dimensions']['width'],
        #                 length= card['dimensions']['length'],
        #                 height = card['dimensions']['height'],
        #                 # image_url= str(card['photos'][0]),
        #             )
        #             db.add(product)
        #             db.commit()
        #             db.refresh(product)
        #         else:
        #             product_crud.update(db, db_obj=product,  obj_in={
        #                 'supply_article': str(card['vendorCode']),
        #                 'wb_article': str(card['nmID']),
        #                 'barcode': str(card['sizes'][0]['skus'][0]),
        #                 'width':  card['dimensions']['width'],
        #                 'length': card['dimensions']['length'],
        #                 'height': card['dimensions']['height'],

        #                 # 'image_url': str(card['photos'][0]),
        #             })
        #     except Exception as e:
        #         print(e)

        # today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        # d = datetime.timedelta(days=7)
        # week_ago = (datetime.datetime.today()-d).strftime('%Y-%m-%d %H:%M:%S')
        # body_2 = {  
        #     "timezone": "Europe/Moscow",
        #     "period": {
        #         "begin": week_ago,
        #         "end": today
        #     },
        #     "orderBy": {
        #         "field": "ordersSumRub",
        #         "mode": "asc"
        #     },
        #     "page": 1
        # }
        # rs = requests.post(url='https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail',
        #                 headers=headers,
        #                 json=body_2
        # )
        # result = rs.json()
        # for card in result['data']['cards']:
        #     product = db.query(Product).filter(Product.wb_article==str(card['nmID']), Product.supply_article==str(card['vendorCode'])).first()
        #     if not product:
        #         logger.info(f"NO PRODUCT {card}")
        #         continue

        #     product_crud.update(db, db_obj=product,  obj_in={
        #         'demand': card['statistics']['selectedPeriod']['ordersCount'],
        #         'wb_warehouse_amount': card['stocks']['stocksWb'],
        #     })



        headers={
            'Authorization': user.token
        }
        params = {
            'limit': 1000,
            'offset': 0
        }
        rs = requests.get(url='https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter',
                        headers=headers,params=params
        )

        result = rs.json()
        print(result)
        try:
            for card in result['data']['listGoods']:
                print(card)
                product = db.query(Product).filter(Product.wb_article==str(card['nmID'])).first()
                if not product:
                    print("NO")
                    logger.info(f"NO PRODUCT {card}")
                    continue
                print("YES!")
                product_crud.update(db, db_obj=product,  obj_in={
                    'fake_wb_price': card['sizes'][0]['price'],
                    'discount': card['discount'],
                    'wb_price':card['sizes'][0]['price']*(100-card['discount'])/100,
                })
        except Exception as e:
            print(e)
                