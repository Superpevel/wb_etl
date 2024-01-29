import logging.config
from typing import List
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, Response, Depends, Header
from fastapi.responses import JSONResponse
from db.db_conf import get_db
from schemas.request_schemas.ping_schema import PingRequest
from models.ping import Ping
from sqlalchemy.orm import Session
from models.user import User
import logging

logger = logging.getLogger(__name__)

@app.post('/ping')
def ping(request: PingRequest, db:Session=Depends(get_db)):
    logger.info(f"ping {request.text}")
    ping = Ping(text=request.text)
    db.add(ping)
    db.commit()
    return True
