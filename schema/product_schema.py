from Enum.enum_definations import ProductType


class SizeSchema:
    id: int
    size: str


class CartSchema:
    id: int
    qty: int
    customer: int
    product: int
    size: int


class ProductSchema:
    id: int
    name: str
    slug: str
    price: int
    description: str
    type: ProductType


class WishlistSchema:
    id: str
    products: ProductSchema
