from tortoise import fields, models

from .abstract_models import UserAbstractModel


class Customer(UserAbstractModel):
    addresses = fields.ReverseRelation["Address"]
    cart_items = fields.ReverseRelation["Cart"]  # type: ignore
    wishlist_items = fields.ReverseRelation["Wishlist"]  # type: ignore

    class Meta:
        table = "customer"


class Employee(UserAbstractModel):
    is_superuser = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)
    is_staff = fields.BooleanField(default=False)
    # role = fields.ForeignKeyField("models.Role", related_name="role")

    class Meta:
        table = "employee"


class Address(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    address = fields.CharField(max_length=100)
    city = fields.CharField(max_length=20)
    state = fields.CharField(max_length=20)
    pinCode = fields.CharField(max_length=10)
    customer = fields.ForeignKeyField("models.Customer", related_name="addresses")

    class Meta:
        table = "address"
