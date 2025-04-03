from crud.crud_base import CRUDBase
from models import Product
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.db_conf import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ProductCrud(CRUDBase):
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).order_by(Product.id.desc()).offset(skip).limit(limit).all()
    pass

    def id_product_by_wb_article(self, db: Session, wb_article):
        product = db.query(self.model).filter(Product.wb_article==wb_article).first()
        return None if not product else product.id


product_crud = ProductCrud(Product)