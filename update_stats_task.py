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
import platform
from tasks.update_stats import update_stats
import asyncio
load_dotenv()

database_uri = os.environ.get('DATABASE_URL')

sessionmaker = FastAPISessionMaker(database_uri)


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


async def update_stats_task() -> None:
    try:
        with sessionmaker.context_session() as db:
            print("START updating stats")
            await update_stats(db=db)
    except Exception as e:
        print(e, "ERROR")

async def main():
    asyncio.ensure_future(update_stats_task()) 
    print('Do some actions 1')
    # await asyncio.sleep(5)
    # print('Do some actions 2')

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # await update_stats_task()