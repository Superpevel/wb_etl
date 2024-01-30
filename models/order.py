import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger, Boolean, TIMESTAMP, Float
from db.db_conf import Base

load_dotenv()

class Order(Base):

    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(TIMESTAMP)
    lastChangeDate = Column(TIMESTAMP)
    warehouseName = Column(String)
    countryName = Column(String)
    oblastOkrugName = Column(String)
    regionName = Column(String)
    supplierArticle = Column(String(), nullable=False)
    nmId = Column(Integer)
    barcode = Column(String(), nullable=False)
    category = Column(String(), nullable=False)
    subject =  Column(String(), nullable=False)
    brand = Column(String(), nullable=False)
    techSize = Column(String(), nullable=False)
    incomeID = Column(Integer)
    isSupply = Column(Boolean)
    isRealization = Column(Boolean)
    totalPrice = Column(Float)
    discountPercent = Column(Float)
    spp = Column(Integer)
    finishedPrice = Column(Float)
    priceWithDisc = Column(Float)
    isCancel = Column(Boolean)
    cancelDate = Column(TIMESTAMP)
    orderType =  Column(String())
    sticker = Column(String())
    gNumber =  Column(String())
    srid = Column(String())
    user_id = Column(Integer, ForeignKey("users.id"))

    def __repr__(self):
        return '<Order %r>' % self.id
