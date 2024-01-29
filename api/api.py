from fastapi import APIRouter
from auth.auth import get_user_secure
import logging
from fastapi import FastAPI, Query, Request, Response, Depends, Header
import logging
from db.db_conf import get_db
from sqlalchemy.orm import Session
from models import *
from schemas.request_schemas.card_request import UserRegister,UserLogin
from models.user import User
import jwt

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)

@app.post('/register')
def register(request: UserRegister, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.login==request.login).first()
    if user:
        return {'error': 'user is already registred'}
    obj: User = db.query(User).order_by(User.id.desc()).first()
    id = obj.id + 1
    encoded_jwt = jwt.encode({"login": request.login, 'password': request.password, 'user_id': id}, "secret", algorithm="HS256")
    user = User(login=request.login, email=request.email, password=request.password, token=encoded_jwt)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post('/login')
def login(request: UserLogin, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.login==request.login,User.password==request.password).first()
    if not user:
        return {'error': 'No such user'}
    else:
        return user