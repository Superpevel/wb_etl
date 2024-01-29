from typing import List
from fastapi import Depends
from logs.logs_config import LOGGING_CONFIG
import logging
from db.db_conf import get_db
from sqlalchemy.orm import Session
from models.user import User
from fastapi.exceptions import HTTPException
import jwt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def secure(token):
    decoded_token = jwt.decode(token, 'secret', algorithms='HS256', verify=False)
    return decoded_token

def get_user_secure(token: str = Depends(oauth2_scheme), db: Session=Depends(get_db)):  ## Get user from decoded token 
    try: 
        user_data = secure(token)
        user = db.query(User).filter(User.id==user_data['user_id']).first()
        if user:
            return user
        else:
            raise HTTPException(status_code=400, detail='invalid_user')
    except Exception as e:
        return HTTPException(status_code=400, detail='Not valid token')
