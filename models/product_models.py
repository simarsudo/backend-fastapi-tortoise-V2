from tortoise import fields, models
from Enum.enum_definations import ProductType
from .validators import validate_json_address


class Products(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50, null=False)
    slug = fields.CharField(max_length=100, null=False)
    price = fields.IntField(null=False)
    description = fields.TextField()
    type = fields.CharEnumField(ProductType, max_length=20)

    images = fields.ReverseRelation["Images"]
    cart_items = fields.ReverseRelation["Cart"]
    wishlist_items = fields.ReverseRelation["Wishlist"]
    inventory = fields.ReverseRelation["Inventory"]
    orders = fields.ReverseRelation["Orders"]

    def __repr__(self):
        return (
            f"Products: id={self.id}, name={self.name}"
            f"price={self.price}, description={self.description}, type={self.type}"
        )

    class Meta:
        table = "products"


class Images(models.Model):
    id = fields.IntField(primary_key=True)
    path = fields.CharField(max_length=100, db_index=True, null=False)

    product = fields.ForeignKeyField("models.Products", related_name="images")

    def __repr__(self):
        return f"{self.product} {self.path}"

    class Meta:
        table = "images"


class Cart(models.Model):
    id = fields.IntField(primary_key=True)
    qty = fields.IntField(null=False)

    product = fields.ForeignKeyField(
        "models.Products", related_name="cart_item", null=False
    )
    customer = fields.ForeignKeyField(
        "models.Customer", related_name="customer", null=False
    )
    size = fields.ForeignKeyField("models.Sizes", related_name="sizes")

    def __repr__(self):
        return f"Product ID:{self.product_id}, Customer_id: {self.customer}, Size: {self.size}, Quantity: {self.qty}"

    class Meta:
        table = "cart"


class Sizes(models.Model):
    id = fields.IntField(primary_key=True)
    size = fields.CharField(max_length=5, unique=True, null=False)

    cart_item_size = fields.ReverseRelation["Cart"]
    inventory = fields.ReverseRelation["Inventory"]

    def __repr__(self):
        return f"Size: {self.size}"

    class Meta:
        table = "sizes"


class Wishlist(models.Model):
    id = fields.IntField(primary_key=True, db_index=True)

    product = fields.ForeignKeyField("models.Products", null=False)
    customer = fields.ForeignKeyField("models.Customer", null=False)

    def __repr__(self):
        return f"Product ID: {self.product_id}, Customer: {self.customer_id}"

    class Meta:
        table = "wishlist"
        unique_together = ("product", "customer")


class Inventory(models.Model):
    id = fields.IntField(primary_key=True)
    quantity = fields.IntField(null=False)

    product = fields.ForeignKeyField("models.Products", null=False)
    size = fields.ForeignKeyField("models.Sizes", null=False)

    def __repr__(self):
        return f"{self.size}: {self.quantity}"

    class Meta:
        table = "inventory"


class PaymentDetails(models.Model):
    id = fields.IntField(primary_key=True)
    card_number = fields.CharField(max_length=16, null=False)
    card_holder_name = fields.CharField(max_length=50, null=False)
    month = fields.CharField(max_length=2, null=False)
    year = fields.CharField(max_length=4, null=False)
    cvv = fields.CharField(max_length=3, null=False)
    billing_address = fields.JSONField(null=False)

    order = fields.OneToOneField(
        "models.Orders", related_name="payment_details", null=False
    )

    def __repr__(self):
        return f"{self.card_number} {self.card_holder_name} {self.month} {self.year} {self.cvv} {self.billing_address}"

    class Meta:
        table = "payment_details"

    async def save(self, *args, **kwargs):
        validate_json_address(self.billing_address)
        await super().save(*args, **kwargs)


class Orders(models.Model):
    id = fields.IntField(primary_key=True)
    order_id = fields.UUIDField()
    delivery_address = fields.JSONField(null=False)
    customer = fields.ForeignKeyField("models.Customer", null=False)
    products = fields.ManyToManyField("models.Products", related_name="orders")
    payment_detail = fields.ReverseRelation["PaymentDetails"]

    def __repr__(self):
        return f"{self.order_id}"

    class Meta:
        table = "orders"

    async def save(self, *args, **kwargs):
        validate_json_address(self.delivery_address)
        await super().save(*args, **kwargs)
