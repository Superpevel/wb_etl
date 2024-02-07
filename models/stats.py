import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger, Boolean, TIMESTAMP, Float
from db.db_conf import Base

load_dotenv()

class Stats(Base):

    __tablename__ = 'stats'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(TIMESTAMP)
    nmId =  Column(Integer)
    vendorCode = Column(String)
    brandName = Column(String)
    openCardCount = Column(Integer)
    addToCartCount = Column(Integer)
    ordersCount = Column(Integer)
    ordersSumRub = Column(Float)
    buyoutsCount = Column(Integer)
    buyoutsSumRub = Column(Float)
    cancelCount = Column(Integer)
    cancelSumRub = Column(Float)
    addToCartPercent = Column(Float)
    cartToOrderPercent = Column(Float)
    buyoutsPercent = Column(Float)
    avg_price_rub = Column(Float)
    def __repr__(self):
        return '<Stats %r>' % self.id
