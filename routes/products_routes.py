from config import BASELINK
from fastapi import HTTPException, APIRouter
from models import Products, Inventory

router = APIRouter()


# @router.get("/", response_model=list[ProductReturnSchema])
# def get_products():
#     try:
#         products_data = db.query(Products).all()
#         if not products_data:
#             raise HTTPException(status_code=404, detail="No products found")
#         return products_data
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500)
#     except HTTPException:
#         raise


@router.get("/{slug}")
async def get_product(slug: str):
    try:
        product = await Products.get_or_none(slug=slug).prefetch_related("images")
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

        inventory = await Inventory.filter(product_id=product.id).prefetch_related(
            "size"
        )
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
        for image in product.images:
            response["images"].append(BASELINK + image.path)
        return response
    except HTTPException:
        raise
