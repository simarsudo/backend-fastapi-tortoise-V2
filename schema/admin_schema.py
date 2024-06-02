from typing import Literal
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_queryset_creator
from models import Products
from Enum.enum_definations import ProductType


class EmployeeSchema(BaseModel):
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


class NewEmployeeSchema(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    phone_no: str


class AllEmployeeOut(BaseModel):
    id: int
    username: str
    email: str
    fullName: str
    phone_no: str
    isDisabled: bool
    role: Literal["Staff", "Admin"]


class ChangEmployeeStatusIn(BaseModel):
    id: int
    status: bool


class ChangEmployeeStatusOut(BaseModel):
    detail: Literal["Employee status changed to {employee.is_disabled}"]


GetAllProducts = pydantic_queryset_creator(
    Products,
    exclude=(
        "description",
        "images",
        "cart_items",
        "wishlist_items",
        "inventory",
        "orders",
    ),
)


class AddProductIn(BaseModel):
    name: str
    price: int
    description: str
    type: ProductType


class AddProductOut(BaseModel):
    id: int


class AddProductImages(BaseModel):
    message: Literal["Images added"]


class UpdateTopWearInventoryIn(BaseModel):
    product_id: int
    s: int
    m: int
    l: int  # noqa: E741
    xl: int
    xxl: int


class UpdateTopWearInventoryOut(BaseModel):
    message: Literal["Inventory updated"]


class UpdateBottomwearInventoryIn(BaseModel):
    product_id: int
    size_32: int
    size_34: int
    size_36: int
    size_38: int
    size_40: int


class UpdateBottomwearInventoryOut(BaseModel):
    message: Literal["Inventory updated"]
