from enum import Enum


class ProductType(Enum):
    SHIRTS = "Shirts"
    TSHIRTS = "TShirts"
    PANTS = "Pants"
    JOGGERS = "Joggers"


class OrderStatus(Enum):
    PACKING = "Packing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
