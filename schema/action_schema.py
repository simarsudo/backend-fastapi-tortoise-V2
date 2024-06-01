from pydantic import BaseModel
from typing import Literal


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
