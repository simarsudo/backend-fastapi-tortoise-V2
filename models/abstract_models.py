from tortoise import fields, models


class UserAbstractModel(models.Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=20, unique=True, null=False)
    email = fields.CharField(max_length=50, unique=True, null=False)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    phone_no = fields.CharField(max_length=10, null=False)
    is_disabled = fields.BooleanField(default=False, null=False)
    password_hash = fields.CharField(max_length=150, null=False)
    token = fields.CharField(max_length=200, null=True)
    registered_on = fields.DatetimeField(auto_now_add=True)
    last_login = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["hashed_password"]

    class Meta:
        abstract = True
