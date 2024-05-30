from fastapi import Depends, HTTPException, APIRouter
from core.schema.products_schema import ProductReturnSchema
from core.db_connection import get_db_session
from sqlalchemy.orm import Session
from core.models.products_model import Products

router = APIRouter()


@router.get("/pants", response_model=list[ProductReturnSchema])
def get_products(db: Session = Depends(get_db_session)):
    try:
        products_data = db.query(Products).where(Products.type == "Pants").all()
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500)


@router.get("/shirt", response_model=list[ProductReturnSchema])
def get_shirts(db: Session = Depends(get_db_session)):
    try:
        products_data = db.query(Products).where(Products.type == "Shirt").all()
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500)


@router.get("/joggers", response_model=list[ProductReturnSchema])
def get_joggers(db: Session = Depends(get_db_session)):
    try:
        products_data = db.query(Products).where(Products.type == "Joggers").all()
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500)
