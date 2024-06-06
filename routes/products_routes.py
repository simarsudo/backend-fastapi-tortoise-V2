from config import BASELINK
from fastapi import HTTPException, APIRouter
from models import Products

router = APIRouter()


@router.get("/pants")
def get_products(
    page: int = 1,
    per_page: int = 10,
):
    offset = (page - 1) * per_page
    try:
        products_data = Products.filter(type == "Pants").offset(offset).limit(per_page)
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except HTTPException:
        raise


@router.get("/shirt")
async def get_shirts(
    page: int = 1,
    per_page: int = 12,
):
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.filter(type="Shirt")
            .prefetch_related("images")
            .offset(offset)
            .limit(per_page)
            # .values()
        )
        products = []
        for product in products_data:
            images = await product.images.all()
            product_dict = dict(product)
            image = images[0].path
            product_dict["image"] = BASELINK + image
            product_dict.pop("type")
            product_dict.pop("description")
            products.append(product_dict)

        # Check if there are more products after the current page
        next_page_products = (
            await Products.filter(type="Shirt").offset(offset + per_page).count()
        )

        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")

        # Determine if there are more products for the next page
        has_next_page = next_page_products > 0

        return {"nextPage": has_next_page, "products": products}
    except HTTPException:
        raise


@router.get("/joggers")
def get_joggers():
    try:
        products_data = Products.filter(type == "Joggers")
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except HTTPException:
        raise
