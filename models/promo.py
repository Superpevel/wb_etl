import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger, Boolean, TIMESTAMP, Float
from sqlalchemy.orm import relationship

from db.db_conf import Base

load_dotenv()

class Promo(Base):

    __tablename__ = 'promo'

    advertId = Column(Integer, primary_key=True)
    type =  Column(Integer)
    status = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_name = Column(String)

    promo_stats = relationship("PromoStats", cascade="all,delete", backref="parent")
    key_words_stats = relationship("KeyWordsStats", cascade="all,delete", backref="parent")

    def __repr__(self):
        return '<Promo %r>' % self.advertId

class PromoStats(Base):

    __tablename__ = 'promo_stats'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(TIMESTAMP)
    clicks = Column(Integer)
    ctr = Column(Integer)
    cpc = Column(Integer)
    views = Column(Integer)
    nmId =  Column(Integer)
    sum =  Column(Float)
    date_order_sum = Column(Float)
    drr = Column(Float)
    advert_id = Column(Integer, ForeignKey("promo.advertId"))
    user_id = Column(Integer, ForeignKey("users.id"))

    def __repr__(self):
        return '<PromoStats %r>' % self.id

class KeyWordsStats(Base):
    __tablename__ = 'key_words_stats'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(TIMESTAMP)
    keyword = Column(String)
    views = Column(Integer)
    clicks = Column(Integer)
    ctr = Column(Integer)
    sum =  Column(Float)
    advert_id = Column(Integer, ForeignKey("promo.advertId"))
    user_id = Column(Integer, ForeignKey("users.id"))

    def __repr__(self):
        return '<PromoStats %r>' % self.id