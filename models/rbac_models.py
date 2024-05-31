from tortoise import fields, models


class Role(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50, unique=True, null=False)

    permissions = fields.ReverseRelation["Permissions"]
    employee_role = fields.ReverseRelation["Employee"]  # type: ignore

    def __repr__(self):
        return f"Role: {self.name})"

    class Meta:
        table = "role"


class Resource(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50, unique=True, null=False)

    resource = fields.ReverseRelation["Permissions"]

    def __repr__(self):
        return f"Resource name:{self.name}"

    class Meta:
        table = "resource"


class Permissions(models.Model):
    id = fields.IntField(primary_key=True)
    read = fields.BooleanField(default=False, null=False)
    write = fields.BooleanField(default=False, null=False)
    update = fields.BooleanField(default=False, null=False)
    delete = fields.BooleanField(default=False, null=False)

    role = fields.ForeignKeyField("models.Role", related_name="roles", null=False)
    resource = fields.ForeignKeyField(
        "models.Resource", related_name="resources", null=False
    )

    def __repr__(self):
        return f"ID: {self.id} Role: {self.role_id} Resource: {self.resource_id} Read:{self.read} Write:{self.write} \
         Update:{self.update} Delete:{self.delete}"

    class Meta:
        table = "permissions"
        unique_together = ("role", "resource")
