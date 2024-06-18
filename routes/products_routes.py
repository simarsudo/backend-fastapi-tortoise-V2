from typing import Literal
from config import BASELINK
from fastapi import HTTPException, APIRouter
from models import Products
from Enum.enum_definations import ProductType

router = APIRouter()


@router.get("")
async def get_products():
    LIIMIT = 7
    try:
        shirts = (
            await Products.filter(type=ProductType.SHIRTS)
            .limit(LIIMIT)
            .prefetch_related("images")
        )
        tshirts = (
            await Products.filter(type=ProductType.TSHIRTS)
            .limit(LIIMIT)
            .prefetch_related("images")
        )
        pants = (
            await Products.filter(type=ProductType.PANTS)
            .limit(LIIMIT)
            .prefetch_related("images")
        )
        joggers = (
            await Products.filter(type=ProductType.JOGGERS)
            .limit(LIIMIT)
            .prefetch_related("images")
        )

        res_shirts = []
        for product in shirts:
            images = await product.images.all()
            shirt_dict = dict(product)
            image = images[0].path
            shirt_dict["image"] = BASELINK + image
            shirt_dict.pop("type")
            shirt_dict.pop("description")
            res_shirts.append(shirt_dict)

        res_tshirts = []
        for product in tshirts:
            images = await product.images.all()
            shirt_dict = dict(product)
            image = images[0].path
            shirt_dict["image"] = BASELINK + image
            shirt_dict.pop("type")
            shirt_dict.pop("description")
            res_tshirts.append(shirt_dict)

        res_pants = []
        for product in pants:
            images = await product.images.all()
            pant_dict = dict(product)
            image = images[0].path
            pant_dict["image"] = BASELINK + image
            pant_dict.pop("type")
            pant_dict.pop("description")
            res_pants.append(pant_dict)

        res_joggers = []
        for product in joggers:
            images = await product.images.all()
            joggers_dict = dict(product)
            image = images[0].path
            joggers_dict["image"] = BASELINK + image
            joggers_dict.pop("type")
            joggers_dict.pop("description")
            res_joggers.append(joggers_dict)

        return {
            "shirts": res_shirts,
            "tshirts": res_tshirts,
            "pants": res_pants,
            "joggers": res_joggers,
        }
    except HTTPException:
        raise


@router.get("/pants")
async def get_pants(
    page: int = 1, per_page: int = 16, price_sort: Literal["a", "d"] = "a"
):
    sort = "price"
    if price_sort == "d":
        sort = "-price"
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
            .order_by(sort)
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
    page: int = 1, per_page: int = 16, price_sort: Literal["a", "d"] = "a"
):
    sort = "price"
    if price_sort == "d":
        sort = "-price"
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.filter(type=ProductType.SHIRTS)
            .order_by(sort)
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
    page: int = 1, per_page: int = 16, price_sort: Literal["a", "d"] = "a"
):
    sort = "price"
    if price_sort == "d":
        sort = "-price"
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.filter(type=ProductType.TSHIRTS)
            .order_by(sort)
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
    page: int = 1, per_page: int = 16, price_sort: Literal["a", "d"] = "a"
):
    sort = "price"
    if price_sort == "d":
        sort = "-price"
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="Page cannont be less than 0")
        if per_page < 1:
            raise HTTPException(status_code=400, detail="Item count be less than 0")
        offset = (page - 1) * per_page
        # Get the products for the current page
        products_data = (
            await Products.filter(type=ProductType.JOGGERS)
            .order_by(sort)
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
