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
import os
from dotenv import load_dotenv

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def secure(token):
    print(token)
    decoded_token = jwt.decode(token, os.environ.get("TOKEN_KEY"), algorithms='HS256', verify=False)
    print("HRE>")
    print(decoded_token)
    # this is often used on the client side to encode the user's email address or other properties
    return decoded_token

def get_userdata_secure(token: str = Depends(oauth2_scheme), db: Session=Depends(get_db)):
    try: 
        print("Hello?")
        user_data = secure(token)
        user = db.query(User).filter(User.id==user_data['user']).first()
        if user:
            return user
        else:
            raise HTTPException(status_code=400, detail='invalid_user')
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail='Not valid token')
