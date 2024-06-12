from config import BASELINK
from fastapi import HTTPException, APIRouter
from models import Products  # Inventory
from Enum.enum_definations import ProductType

router = APIRouter()


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
        sizesAvailable = []

        if product.type == ProductType.JOGGERS or product.type == ProductType.PANTS:
            sizesAvailable = [
                {"32": True},
                {"34": True},
                {"36": True},
                {"38": True},
                {"40": True},
            ]
        else:
            sizesAvailable = [
                {"s": True},
                {"m": True},
                {"l": True},
                {"xl": True},
                {"xxl": True},
            ]

        # inventory = await Inventory.filter(product_id=product.id).prefetch_related(
        #     "size"
        # )
        # if inventory:
        #     for i in inventory:
        #         if i.quantity >= 1:
        #             response["sizesAvailable"].append(
        #                 {"size": i.size.size, "available": True}
        #             )
        #         else:
        #             response["sizesAvailable"].append(
        #                 {"size": i.size.size, "available": False}
        #             )
        response["sizesAvailable"] = sizesAvailable
        for image in product.images:
            response["images"].append(BASELINK + image.path)
        return response
    except HTTPException:
        raise
