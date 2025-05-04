from fastapi import APIRouter
import logging
from fastapi import FastAPI, Query, Request, Response, Depends, Header
import logging
from db.db_conf import get_db
from sqlalchemy.orm import Session
from models import *
from schemas.request_schemas.card_request import UserRegister,UserLogin
from models.user import User
import jwt
from api.v1.product.product import router as product_router, unit_router
from api.v1.competitors.competitors_crud import competitors_router
from api.v1.competitors.competitors_parse import competitor_parse_router
from api.v1.model.model import router as model_router

from auth.auth import get_userdata_secure
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["api"],
    responses={404: {"description": "Not found"}},
)


router.include_router(unit_router)
router.include_router(product_router)
router.include_router(competitors_router)
router.include_router(competitor_parse_router)

router.include_router(model_router)


@router.post('/register')
def register(request: UserRegister, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.login==request.login).first()
    if user:
        return {'error': 'user is already registred'}
    obj: User = db.query(User).order_by(User.id.desc()).first()
    id = obj.id + 1
    # encoded_jwt = jwt.encode({"login": request.login, 'password': request.password, 'user_id': id}, "secret", algorithm="HS256")
    user = User(login=request.login, email=request.email, password=request.password, token=request.token)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put('/user')
def edit_user(request: UserRegister,user: User=Depends(get_userdata_secure), db: Session=Depends(get_db)):

    if request.login:
        user.login = request.login
    if request.password:
        user.password = request.password
    
    if request.email:
        user.email = request.email
    
    if request.token:
        user.token = request.token
    
    db.add(user)
    db.commit()
    return user
    
@router.post('/login')
def login(request: UserLogin, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.login==request.login,User.password==request.password).first()
    if not user:
        return {'error': 'No such user'}
    else:
        return user
    

