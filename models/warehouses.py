import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger, Boolean, TIMESTAMP, FLOAT
from db.db_conf import Base

load_dotenv()

class Warehouse(Base):

    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True, index=True)
    boxDeliveryAndStorageExpr = Column(String(800), nullable=False)
    boxDeliveryBase = Column(String(800), nullable=False)
    boxDeliveryLiter = Column(String(800), nullable=False)
    boxStorageBase =  Column(String(800), nullable=False)
    boxStorageLiter =  Column(String(800), nullable=False)
    warehouseName = Column(String(800), nullable=False)


    def __repr__(self):
        return '<Warehouse %r>' % self.id

