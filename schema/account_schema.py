from typing import Literal, List
from pydantic import BaseModel
from datetime import datetime
from .product_schema import WishlistSchema, CartSchema


class AddressSchema(BaseModel):
    id: int
    name: str
    address: str
    city: str
    state: str
    pinCode: str
    customer: int


class CustomerSchema(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    phone_no: str
    is_disabled: bool
    password_hash: str
    token: str
    registered_on: datetime
    last_login: datetime
    # addresses = List[AddressSchema]
    # cart_items = List[CartSchema]
    # wishlist_items = List[WishlistSchema]


class TokenOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"]


class CustomerSignUp(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    address: str
    city: str
    phone_no: str
    state: str
    pinCode: str
