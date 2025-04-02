import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger, Boolean, TIMESTAMP, Float
from db.db_conf import Base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from typing import List


load_dotenv()

class Product(Base):

    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    supply_article = Column(String)
    wb_article = Column(String)
    barcode = Column(String)
    cost_price = Column(Float, nullable=True, default=0)
    wb_price = Column(Float, nullable=True)
    fake_wb_price = Column(Float)
    discount = Column(Float)

    commision_percentage = Column(Integer, default=19)
    logistics_fee = Column(Float, default=70)
    tax_fee_percentage =  Column(Float, default=1)

    mono_items = Column(Integer, nullable=True)
    box_items = Column(Integer, nullable=True)
    demand = Column(Integer, nullable=True, default=0)
    warehouse_amount = Column(Integer, default=0)
    shipping_amount = Column(Integer, default=0)
    production_amount = Column(Integer, default=0)
    wb_warehouse_amount = Column(Integer, default=0)

    plan_pallet = Column(Integer)

    image_url = Column(String)


    def __repr__(self):
        return '<Product %r>' % self.id