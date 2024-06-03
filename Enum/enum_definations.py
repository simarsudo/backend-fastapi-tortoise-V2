from enum import Enum


class ProductType(Enum):
    SHIRT = "Shirt"
    PANTS = "Pants"
    JOGGERS = "Joggers"


class OrderStatus(Enum):
    PACKING = "Packing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
