from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal
from tortoise.contrib.pydantic import pydantic_model_creator
from models.product_models import Images, Products


class AddToWishlistOut(BaseModel):
    success: Literal["Product added to wishlist"]


class AddToCartOut(BaseModel):
    success: Literal["Product added to cart"]


class IsInWishlistOut(BaseModel):
    success: Literal["Item in wishlist"]


class GetWishlistOut(BaseModel):
    pass


class RemoveWishlistItemOut(BaseModel):
    success: Literal["Item removed from wishlist successfully"]


class MoveToCartIn(BaseModel):
    slug: str
    qty: int
    size: Literal["s", "m", "l", "xl", "xxl", "32", "34", "36", "38", "40"]


class MoveToCartOut(BaseModel):
    success: Literal["Item moved to cart"]


class UpdateCartItemQtyIn(BaseModel):
    id: int
    qty: int
    size: Literal["s", "m", "l", "xl", "xxl", "32", "34", "36", "38", "40"]


class UpdateCartItemSizeIn(BaseModel):
    id: int
    qty: int
    size: Literal["s", "m", "l", "xl", "xxl", "32", "34", "36", "38", "40"]
    prevSize: Literal["s", "m", "l", "xl", "xxl", "32", "34", "36", "38", "40"]


class NewAddressUserAddressIn(BaseModel):
    name: str
    address: str
    city: str
    state: str
    pinCode: str
    phone_no: str = Field(
        pattern=r"^\d{10}$", description="Phone Number number must be exactly 10 digits"
    )


class PaymentDetailsIn(BaseModel):
    cardNumber: str = Field(
        pattern=r"^\d{16}$", description="Credit card number must be exactly 16 digits"
    )
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=datetime.now().year - 1, le=2050)
    cvv: int = Field(ge=0, le=999)
    name: str = Field(min_length=3, max_length=50)


OrderItemsOut = pydantic_model_creator(
    Products,
    name="Product",
    exclude=("slug", "description"),
)

OrderImageOut = pydantic_model_creator(
    Images,
)
