

import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, BigInteger, Boolean, TIMESTAMP, Float
from db.db_conf import Base
from sqlalchemy.orm import relationship

load_dotenv()

class Competitor(Base):

    __tablename__ = 'competitor'

    id = Column(Integer, primary_key=True, index=True)
    competitor_nmID =  Column(String)
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product", backref="competitors")




    def __repr__(self):
        return '<Competitor %r>' % self.id


class CompetitorPrices(Base):

    __tablename__ = 'competitor_prices'

    id = Column(Integer, primary_key=True, index=True)
    # competitor_nmID =  Column(String)
    competitor_id = Column(Integer, ForeignKey('competitor.id'))
    competitor = relationship("Competitor", backref="prices")
    date = Column(TIMESTAMP)
    price = Column(Integer)


    def __repr__(self):
        return '<CompetitorPrices %r>' % self.id