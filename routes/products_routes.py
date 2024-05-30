from fastapi import Depends, HTTPException, APIRouter
from core.schema.products_schema import ProductReturnSchema
from core.models.products_model import Products, Inventory, Image
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.db_connection import get_db_session

router = APIRouter()


@router.get("/", response_model=list[ProductReturnSchema])
def get_products(db: Session = Depends(get_db_session)):
    try:
        products_data = db.query(Products).all()
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.get("/{slug}")
def get_product(slug: str, db: Session = Depends(get_db_session)):
    try:
        product = db.query(Products).filter(Products.slug == slug).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        response = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "type": product.type,
            "images": [],
            "sizesAvailable": [],
        }

        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).all()
        if inventory:
            for i in inventory:
                if i.quantity >= 1:
                    response["sizesAvailable"].append(
                        {"size": i.size.size, "available": True}
                    )
                else:
                    response["sizesAvailable"].append(
                        {"size": i.size.size, "available": False}
                    )
        images = db.query(Image).filter(Image.product_id == product.id).all()
        if images:
            for image in images:
                response["images"].append("http://127.0.0.1:8000/" + image.image_path)
        # Todo create dynamic link for static
        return response
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise
