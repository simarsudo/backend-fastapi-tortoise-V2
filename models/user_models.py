from tortoise import fields, models


class Customer(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    full_name = fields.CharField(max_length=50, null=True)
    hashed_password = fields.CharField(max_length=128, null=True)
    token = fields.CharField(max_length=128, null=True)
    registered_on = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(auto_now=True)
    addresses = fields.ReverseRelation["Address"]

    class PydanticMeta:
        exclude = ["hashed_password"]


class Address(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    address = fields.CharField(max_length=100)
    city = fields.CharField(max_length=20)
    state = fields.CharField(max_length=20)
    pinCode = fields.CharField(max_length=10)
    customer = fields.ForeignKeyField("models.Customer", related_name="addresses")


class Employee(models.Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=20, unique=True, null=False)
    email = fields.CharField(max_length=50, unique=True, null=False)
    full_name = fields.CharField(max_length=50)
    phone_no = fields.CharField(max_length=10, null=False)
    is_disabled = fields.BooleanField(default=False, null=False)
    hashed_password = fields.CharField(max_length=150, null=False)
    token = fields.CharField(max_length=200, null=True)
    registered_on = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(auto_now=True)
    is_superuser = fields.BooleanField(default=False)
    is_admin = fields.BooleanField(default=False)
    is_staff = fields.BooleanField(default=False)
    # role = fields.ForeignKeyField("models.Role", related_name="role")
