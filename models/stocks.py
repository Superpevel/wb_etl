import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger, Boolean, TIMESTAMP, Float
from db.db_conf import Base

load_dotenv()

class Stocks(Base):

    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True, index=True)
    lastChangeDate = Column(TIMESTAMP)
    warehouseName = Column(String)
    supplierArticle = Column(String)
    nmId =  Column(Integer)
    barcode = Column(String)
    quantity = Column(Integer)
    inWayToClient = Column(Integer)
    inWayFromClient = Column(Integer)
    quantityFull =  Column(Integer)
    techSize = Column(String)
    Price = Column(Float)
    Discount = Column(Float)
    isSupply = Column(Boolean)
    isRealization = Column(Boolean)
    SCCode = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))


    def __repr__(self):
        return '<Stocks %r>' % self.id
