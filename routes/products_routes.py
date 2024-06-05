from fastapi import HTTPException, APIRouter
from models import Products
# from core.schema.products_schema import ProductReturnSchema

router = APIRouter()


@router.get("/pants")
def get_products():
    try:
        products_data = Products.filter(type == "Pants")
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except HTTPException:
        raise
    # except Exception as e:
    #     raise HTTPException(status_code=500)


@router.get("/shirt")
async def get_shirts():
    try:
        products_data = await Products.filter(type="Shirt")
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except HTTPException:
        raise
    # except Exception as e:
    #     raise HTTPException(status_code=500)


@router.get("/joggers")
def get_joggers():
    try:
        products_data = Products.filter(type == "Joggers")
        if not products_data:
            raise HTTPException(status_code=404, detail="No products found")
        return products_data
    except HTTPException:
        raise
    # except Exception as e:
    #     raise HTTPException(status_code=500)
