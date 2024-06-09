import tortoise
from typing import Annotated, List
from slugify import slugify
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from config import BASELINK, SIZE_IDS, TAXRATE
import tortoise.exceptions
from tortoise.expressions import Q
from tortoise.transactions import in_transaction
from models.product_models import Orders, Sizes
from utils import get_employee
from models import Employee, Products, Images, Inventory
from schema import (
    EmployeeSchema,
    NewEmployeeSchema,
    AllEmployeeOut,
    ChangEmployeeStatusIn,
    ChangEmployeeStatusOut,
    GetAllProducts,
    AddProductIn,
    AddProductOut,
    AddProductImages,
    UpdateBottomwearInventoryIn,
    UpdateBottomwearInventoryOut,
    UpdateTopWearInventoryIn,
    UpdateTopWearInventoryOut,
)
from schema import (
    OrderItemsOut,
    OrderImageOut,
)
from utils import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from Enum.enum_definations import OrderStatus


router = APIRouter()


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        employee = await Employee.get_or_none(username=form_data.username)
        if not employee:
            raise HTTPException(status_code=401)
        if not verify_password(form_data.password, employee.password_hash):
            raise HTTPException(status_code=401)
        if any([employee.is_superuser, employee.is_admin, employee.is_staff]):
            token = create_access_token(data={"username": employee.username})
            employee.token = token
            employee
            employee_roles = []
            if employee.is_superuser:
                employee_roles.append("is_superuser")
            if employee.is_admin:
                employee_roles.append("is_admin")
            if employee.is_staff:
                employee_roles.append("is_staff")
            token = create_access_token(data={"username": employee.username})
            employee.token = token
            await employee.save()
            return {
                "access_token": employee.token,
                "token_type": "bearer",
                "roles": employee_roles,
            }
        else:
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
    except tortoise.exceptions.OperationalError:
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/add-new-employee")
async def create_employee(
    new_employee_details: NewEmployeeSchema,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
):
    try:
        old_employee = await Employee.filter(
            Q(
                username=new_employee_details.username,
                email=new_employee_details.email,
                join_type="OR",
            )
        )
        for emp in old_employee:
            if emp.username == new_employee_details.username.lower():
                raise HTTPException(status_code=400, detail="Username already exists")
            if emp.email == new_employee_details.email:
                raise HTTPException(status_code=400, detail="Email already exists")
        password_hash = get_password_hash(new_employee_details.password)
        employee = Employee(
            username=new_employee_details.username.lower(),
            email=new_employee_details.email.lower(),
            password_hash=password_hash,
            full_name=new_employee_details.full_name.lower(),
            phone_no=new_employee_details.phone_no,
            is_staff=True,
        )
        await employee.save()
        return {"detail": "User created successfully", "employee_id": employee.id}
    except tortoise.exceptions.OperationalError:
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.get("/all-employee", response_model=List[AllEmployeeOut])
async def get_all_employee(
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
):
    try:
        q = await Employee.all()
        response = []
        for _ in q:
            role = ""
            if _.is_superuser:
                continue
            if _.is_admin:
                role = "Admin"
            if _.is_staff:
                role = "Staff"
            response.append(
                {
                    "id": _.id,
                    "username": _.username,
                    "email": _.email,
                    "fullName": _.full_name,
                    "phone_no": _.phone_no,
                    "isDisabled": _.is_disabled,
                    "role": role,
                }
            )
        return response
    except tortoise.exceptions.OperationalError:
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/change-employee-status", response_model=ChangEmployeeStatusOut)
async def disable_employee(
    employee_data: ChangEmployeeStatusIn,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
):
    emp = await Employee.get_or_none(id=employee_data.id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.is_disabled = employee_data.status
    await emp.save()
    return {"detail": f"Employee status changed to {emp.is_disabled}"}


@router.get("/get-all-products", response_model=GetAllProducts)
async def get_all_products(
    page: int,
    per_page: int,
    name: str | None = None,
    employee=Depends(get_employee),
):
    offset = (page - 1) * per_page
    products = await Products.all().offset(offset).limit(per_page)
    if name:
        products = (
            await Products.filter(name__icontains=name)
            .all()
            .offset(offset)
            .limit(per_page)
        )
    return products


@router.post("/add-product", response_model=AddProductOut)
async def add_new_product(
    product: AddProductIn,
    employee=Depends(get_employee),
):
    db_product = Products(
        name=product.name,
        slug=slugify(product.name),
        description=product.description,
        price=product.price,
        type=product.type,
    )
    await db_product.save()
    return {"id": db_product.id}


@router.post("/add-product-images/{product_id}", response_model=AddProductImages)
async def add_product_images(
    product_id: int,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    files: List[UploadFile] = File(...),
):
    product_db = await Products.get_or_none(id=product_id)
    if product_db is None:
        raise HTTPException(status_code=404, detail="Product not found")
    images_entries = []
    for file in files:
        content = await file.read()
        with open(f"static/public/{product_id}_{file.filename}", "wb") as f:
            f.write(content)
            images_entries.append(
                Images(
                    product_id=product_id,
                    path=f"static/public/{product_id}_{file.filename}",
                )
            )
    await Images.bulk_create(images_entries)
    return {"message": "Images added"}


@router.post("/update-topwear-inventory", response_model=UpdateTopWearInventoryOut)
async def update_topwear_inventory(
    sizes: UpdateTopWearInventoryIn,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
):
    try:
        db_product = await Products.get_or_none(id=sizes.product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        db_inv = (
            await Inventory.filter(product=sizes.product_id)
            .all()
            .prefetch_related("product")
            .prefetch_related("size")
        )
        if db_inv:
            async with in_transaction() as conn:
                for inv in db_inv:
                    if inv.size.size == "s":
                        inv.quantity = sizes.s
                        await inv.save(using_db=conn)
                    elif inv.size.size == "m":
                        inv.quantity = sizes.m
                        await inv.save(using_db=conn)
                    elif inv.size.size == "l":
                        inv.quantity = sizes.l
                        await inv.save(using_db=conn)
                    elif inv.size.size == "xl":
                        inv.quantity = sizes.xl
                        await inv.save(using_db=conn)
                    elif inv.size.size == "xxl":
                        inv.quantity = sizes.xxl
                        await inv.save(using_db=conn)
                return {"message": "Inventory updated"}
        else:
            new_inventory_entries = [
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("s"),
                    quantity=sizes.s,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("m"),
                    quantity=sizes.m,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("l"),
                    quantity=sizes.l,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("xl"),
                    quantity=sizes.xl,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("xxl"),
                    quantity=sizes.xxl,
                ),
            ]
            await Inventory.bulk_create(new_inventory_entries)
            return {"message": "Inventory updated"}
    except tortoise.exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail="Account already exist")
    except tortoise.exceptions.OperationalError:
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post(
    "/update-bottomwear-inventory", response_model=UpdateBottomwearInventoryOut
)
async def update_bottomwear_inventory(
    sizes: UpdateBottomwearInventoryIn,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
):
    try:
        db_product = await Products.get_or_none(id=sizes.product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        db_inv = (
            await Inventory.filter(product=sizes.product_id)
            .all()
            .prefetch_related("product")
            .prefetch_related("size")
        )
        if db_inv:
            async with in_transaction() as conn:
                for inv in db_inv:
                    if inv.size.size == "32":
                        inv.quantity = sizes.size_32
                        await inv.save(using_db=conn)
                    elif inv.size.size == "34":
                        inv.quantity = sizes.size_34
                        await inv.save(using_db=conn)
                    elif inv.size.size == "36":
                        inv.quantity = sizes.size_36
                        await inv.save(using_db=conn)
                    elif inv.size.size == "38":
                        inv.quantity = sizes.size_38
                        await inv.save(using_db=conn)
                    elif inv.size.size == "40":
                        inv.quantity = sizes.size_40
                        await inv.save(using_db=conn)
                return {"message": "Inventory updated"}
        else:
            new_inventory_entries = [
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("32"),
                    quantity=sizes.size_32,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("34"),
                    quantity=sizes.size_34,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("36"),
                    quantity=sizes.size_36,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("38"),
                    quantity=sizes.size_38,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=SIZE_IDS.get("40"),
                    quantity=sizes.size_40,
                ),
            ]
            await Inventory.bulk_create(new_inventory_entries)
            return {"message": "Inventory updated"}
    except tortoise.exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail="Account already exist")
    except tortoise.exceptions.OperationalError:
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.get("/get-orders")
async def get_orders(customer: Annotated[EmployeeSchema, Depends(get_employee)]):
    try:
        orders = (
            await Orders.filter(status=OrderStatus.PACKING)
            .order_by(("-order_placed_on"))
            .prefetch_related("OrderItem")
        )
        if not orders:
            return []
        response = []
        for order in orders:
            total = 0
            res_dict = dict(order)
            for item in await order.OrderItem.all().values():
                tax_price = item["price"] + (item["price"] * TAXRATE) / 100
                total += tax_price * item["qty"]
                res_dict["total"] = total
            response.append(res_dict)
        return response
    except HTTPException:
        raise


@router.get("/get-shipped-orders")
async def get_shipped_orders(
    customer: Annotated[EmployeeSchema, Depends(get_employee)],
):
    try:
        orders = (
            await Orders.filter(status=OrderStatus.SHIPPED)
            .order_by(("-order_placed_on"))
            .prefetch_related("OrderItem")
        )
        if not orders:
            return []
        response = []
        for order in orders:
            total = 0
            res_dict = dict(order)
            for item in await order.OrderItem.all().values():
                tax_price = item["price"] + (item["price"] * TAXRATE) / 100
                total += tax_price * item["qty"]
                res_dict["total"] = total
            response.append(res_dict)
        return response
    except HTTPException:
        raise


@router.post("/update-status-to-shipped")
async def update_order_status(
    id: int, customer: Annotated[EmployeeSchema, Depends(get_employee)]
):
    try:
        order = await Orders.get_or_none(id=id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        order.status = OrderStatus.SHIPPED
        await order.save()
        return {"success": 200}
    except HTTPException:
        raise


@router.get(
    "/get-orders-details",
)
async def get_orders_details(
    order_number, customer: Annotated[EmployeeSchema, Depends(get_employee)]
):
    try:
        response = {"orderDetails": {}, "orderItems": []}
        order = await Orders.get_or_none(order_number=order_number).prefetch_related(
            "OrderItem__product", "OrderItem__product__images"
        )
        if order is None:
            return {}
        response["orderDetails"] = order
        for item in order.OrderItem:
            product = (await OrderItemsOut.from_tortoise_orm(item.product)).model_dump()
            image_dict = (
                await OrderImageOut.from_tortoise_orm(item.product.images[0])
            ).model_dump()
            size = await Sizes.get_or_none(id=item.size_id)
            product["image"] = BASELINK + image_dict["path"]
            product["size"] = size.size
            product["qty"] = item.qty

            response["orderItems"].append(product)
        return response
    except HTTPException:
        raise


# ##################################################################


# @router.post("/add_employee_role")
# def add_employee_role(
#     employee_id: int,
#     role_id: int,
#     employee: Annotated[EmployeeSchema, Depends(get_employee)],
# ):
#     employee = Employee.get_or_none(employee_id)
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     role = db.query(Role).get(role_id)
#     if not role:
#         raise HTTPException(status_code=404, detail="Role not found")
#     if employee.role == role.id:
#         return HTTPException(
#             status_code=400, detail="Employee is already have the same role"
#         )
#     try:
#         employee.role = role.id
#         db.commit()
#         return {"detail": "Role added successfully"}
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Something went wrong")
#     except HTTPException:
#         raise


# @router.post("/create_new_role")
# def create_new_role(
#     role_name: str,
#     employee: Annotated[EmployeeSchema, Depends(get_employee)],
#     db: Session = Depends(get_db_session),
# ):
#     try:
#         if role_name == "superuser":
#             raise HTTPException(status_code=401, detail="Not enough permissions")
#         role = role_name.lower()
#         try:
#             new_role = Role(name=role)
#             db.add(new_role)
#             db.commit()
#             return {"message": "Role created"}
#         except IntegrityError:
#             raise HTTPException(status_code=400, detail="Role already exist")
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500)
#     except HTTPException:
#         raise


# @router.post("/delete_role")
# def delete_role(
#     role_id: int,
#     employee: Annotated[EmployeeSchema, Depends(get_employee)],
#     db: Session = Depends(get_db_session),
# ):
#     role = db.query(Role).get(role_id)
#     if role is None:
#         raise HTTPException(status_code=404, detail="Role not found")
#     try:
#         q = db.query(Permissions).filter(Permissions.role_id == role_id).first()
#         db.delete(q)
#         db.commit()
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500)
#     except HTTPException:
#         raise


# @router.post("/create_new_resource")
# def create_new_resource(
#     resource_name: str,
#     employee: Annotated[EmployeeSchema, Depends(get_employee)],
#     db: Session = Depends(get_db_session),
# ):
#     try:
#         resource = resource_name.lower()
#         try:
#             new_resource = Resource(name=resource)
#             db.add(new_resource)
#             db.commit()
#             return {"message": "Resource created"}
#         except IntegrityError:
#             db.rollback()
#             raise HTTPException(
#                 status_code=400, detail="Resource already exists with the same name"
#             )
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500)
#     except HTTPException:
#         raise


# @router.post("/delete_resource")
# def delete_resource(
#     resource_id: int,
#     employee: Annotated[EmployeeSchema, Depends(get_employee)],
#     db: Session = Depends(get_db_session),
# ):
#     resource = db.query(Resource).get(resource_id)
#     if resource is None:
#         raise HTTPException(status_code=404, detail="Resource not found")
#     try:
#         p = db.query(Permissions).filter(Permissions.resource_id == resource_id).first()
#         db.commit()
#         db.delete(p)
#         db.execute(delete(Resource).where(Resource.id == resource_id))
#         db.commit()
#         return {"message": "Role deleted"}
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500)
#     except HTTPException:
#         raise


# @router.post("/update_role_permissions")
# def update_role_permissions(
#     role_name: str,
#     resource_name: str,
#     read: bool,
#     write: bool,
#     update: bool,
#     delete: bool,
#     employee: Annotated[EmployeeSchema, Depends(get_employee)],
#     db: Session = Depends(get_db_session),
# ):
#     try:
#         role = db.query(Role).filter(Role.name == role_name).first()
#         if role is None:
#             raise HTTPException(status_code=404, detail="Role not found")
#         resource = db.query(Resource).filter(Resource.name == resource_name).first()
#         if resource is None:
#             raise HTTPException(status_code=404, detail="Resource name not found")
#         try:
#             q = Permissions(
#                 role_id=role.id,
#                 resource_id=resource.id,
#                 read=read,
#                 write=write,
#                 update=update,
#                 delete=delete,
#             )
#             db.add(q)
#             db.commit()
#             return {"message": "Permissions created"}
#         except IntegrityError:
#             db.rollback()
#             q = (
#                 db.query(Permissions)
#                 .where(
#                     Permissions.role_id == role.id,
#                     Permissions.resource_id == resource.id,
#                 )
#                 .first()
#             )
#             q.read = read
#             q.write = write
#             q.update = update
#             q.delete = delete
#             db.commit()
#             return {"message": "Permissions updated"}
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(status_code=500)
#     except HTTPException:
#         raise
