from config import BASELINK
from fastapi import HTTPException, APIRouter
from models import Products
from Enum.enum_definations import ProductType

router = APIRouter()


@router.get("")
async def get_products(
    page: int = 1,
    per_page: int = 16,
):
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.all()
            .prefetch_related("images")
            .offset(offset)
            .limit(per_page)
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
            await Products.filter(type="Shirts").offset(offset + per_page).count()
        )

        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")

        # Determine if there are more products for the next page
        has_next_page = next_page_products > 0

        return {"nextPage": has_next_page, "products": products}
    except HTTPException:
        raise


@router.get("/pants")
async def get_pants(
    page: int = 1,
    per_page: int = 16,
):
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.filter(type=ProductType.PANTS)
            .prefetch_related("images")
            .offset(offset)
            .limit(per_page)
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
            await Products.filter(type=ProductType.PANTS)
            .offset(offset + per_page)
            .count()
        )

        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")

        # Determine if there are more products for the next page
        has_next_page = next_page_products > 0

        return {"nextPage": has_next_page, "products": products}
    except HTTPException:
        raise


@router.get("/shirts")
async def get_shirts(
    page: int = 1,
    per_page: int = 16,
):
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.filter(type=ProductType.SHIRTS)
            .prefetch_related("images")
            .offset(offset)
            .limit(per_page)
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
            await Products.filter(type=ProductType.SHIRTS)
            .offset(offset + per_page)
            .count()
        )

        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")

        # Determine if there are more products for the next page
        has_next_page = next_page_products > 0

        return {"nextPage": has_next_page, "products": products}
    except HTTPException:
        raise


@router.get("/tshirts")
async def get_tshirts(
    page: int = 1,
    per_page: int = 16,
):
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.filter(type=ProductType.TSHIRTS)
            .prefetch_related("images")
            .offset(offset)
            .limit(per_page)
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
            await Products.filter(type=ProductType.TSHIRTS)
            .offset(offset + per_page)
            .count()
        )

        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")

        # Determine if there are more products for the next page
        has_next_page = next_page_products > 0

        return {"nextPage": has_next_page, "products": products}
    except HTTPException:
        raise


@router.get("/joggers")
async def get_joggers(
    page: int = 1,
    per_page: int = 16,
):
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.filter(type=ProductType.JOGGERS)
            .prefetch_related("images")
            .offset(offset)
            .limit(per_page)
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
            await Products.filter(type=ProductType.JOGGERS)
            .offset(offset + per_page)
            .count()
        )

        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")

        # Determine if there are more products for the next page
        has_next_page = next_page_products > 0

        return {"nextPage": has_next_page, "products": products}
    except HTTPException:
        raise
