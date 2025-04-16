import logging.config
from typing import List
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, Response, Depends, Header,APIRouter
from fastapi.responses import JSONResponse
from db.db_conf import get_db
from schemas.request_schemas.ping_schema import PingRequest
from models.product import Product
from sqlalchemy.orm import Session
from models.user import User
import logging
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from pydantic import BaseModel
from fastapi.exceptions import HTTPException
from typing import Optional, List
from crud.competitors import competitor_crud 
from dotenv import load_dotenv
import os
import requests
import datetime
from models import Competitor
from tasks.update_concurents_prices import update_prices_history
load_dotenv()

logger = logging.getLogger(__name__)



competitor_parse_router = APIRouter(
    prefix="/competitor_parse",
    tags=["competitor_parse"],
    responses={404: {"description": "Not found"}},
)


@competitor_parse_router.get('/')
def start_parsing(db: Session=Depends(get_db)):
    products = db.query(Product).all()

    for product in products:
        competitors: List[Competitor] = db.query(Competitor).filter(Competitor.product_id==product.id).all()
        if not competitors:
            continue
        # print(competitors)
        update_prices_history(db, product, competitors)


