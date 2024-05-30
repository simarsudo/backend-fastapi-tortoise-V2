from datetime import timedelta
from typing import Annotated, List
from slugify import slugify
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from core.db_connection import get_db_session
from core.models import (
    Role,
    Resource,
    Permissions,
    Employee,
    Products,
    Image,
    Inventory,
)
from core.schema.admin_route_schema import (
    NewEmployeeSchema,
    AllEmployeeSchema,
    UpdateEmployeeStatus,
    ProductSchemaCreate,
    TopWearSizes,
    BottomWearSizes,
)
from core.schema.employee_schema import EmployeeSchema
from core.utils.admin_utils import get_employee
from core.utils.user_utils import (
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
)

router = APIRouter()


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db_session),
):
    employee = (
        db.query(Employee).filter(Employee.username == form_data.username).first()
    )
    try:
        if not employee:
            print("Incorrect username")
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
        if not verify_password(form_data.password, employee.hashed_password):
            print("Incorrect password")
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
        if any([employee.is_superuser, employee.is_admin, employee.is_staff]):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            token = create_access_token(
                data={"sub": employee.username}, expires_delta=access_token_expires
            )
            employee.token = token
            db.commit()
            employee_roles = []
            if employee.is_superuser:
                employee_roles.append("is_superuser")
            if employee.is_admin:
                employee_roles.append("is_admin")
            if employee.is_staff:
                employee_roles.append("is_staff")
            return {
                "access_token": employee.token,
                "token_type": "bearer",
                "roles": employee_roles,
            }
        else:
            print("Not Employee")
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/add-new-employee")
def create_employee(
    new_employee_details: NewEmployeeSchema,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    # Todo add data verification
    try:
        if any([employee.is_admin, employee.is_superuser]) is False:
            raise HTTPException(
                status_code=403,
                detail="Need a superuser or admin role to perform this action",
            )
        hashed_password = get_password_hash(new_employee_details.password)
        username_lower = new_employee_details.username.lower()
        email_lower = new_employee_details.email.lower()
        q = (
            db.query(Employee)
            .filter(
                (Employee.username == new_employee_details.username)
                | (Employee.email == new_employee_details.email)
            )
            .all()
        )
        for u in q:
            if u.username == username_lower:
                raise HTTPException(status_code=400, detail="Username already exists")
            if u.email == email_lower:
                raise HTTPException(status_code=400, detail="Email already exists")
    except HTTPException:
        raise
    try:
        employee = Employee(
            username=new_employee_details.username.lower(),
            email=new_employee_details.email.lower(),
            hashed_password=hashed_password,
            full_name=new_employee_details.full_name.lower(),
            phone_no=new_employee_details.phone_no,
            is_staff=True,
        )
        db.add(employee)
        db.commit()
        return {"detail": "User created successfully", "employee_id": employee.id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")
    except HTTPException:
        raise


@router.get("/all-employee", response_model=List[AllEmployeeSchema])
def get_all_employee(
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    if any([employee.is_admin, employee.is_superuser]) is False:
        raise HTTPException(
            status_code=403,
            detail="Need a superuser or admin role to perform this action",
        )
    try:
        q = db.query(Employee).all()
        employees = []
        for employee in q:
            role = ""
            if employee.is_superuser:
                continue
            if employee.is_admin:
                role = "Admin"
            if employee.is_staff:
                role = "Staff"
            employees.append(
                {
                    "id": employee.id,
                    "username": employee.username,
                    "email": employee.email,
                    "fullName": employee.full_name,
                    "role": role,
                    "isDisabled": employee.is_disabled,
                }
            )
        return employees
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")
    except HTTPException:
        raise


@router.post("/change-employee-status")
def disable_employee(
    employee_data: UpdateEmployeeStatus,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    if any([employee.is_admin, employee.is_superuser]) is False:
        raise HTTPException(
            status_code=403,
            detail="Need a superuser or admin role to perform this action",
        )
    try:
        employee = db.query(Employee).get(employee_data.id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        employee.is_disabled = employee_data.status
        db.commit()
        return {"detail": f"Employee status changed to {employee.is_disabled}"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")
    except HTTPException:
        raise


@router.post("/add_employee_role")
def add_employee_role(
    employee_id: int,
    role_id: int,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    employee = db.query(Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if employee.role == role.id:
        return HTTPException(
            status_code=400, detail="Employee is already have the same role"
        )
    try:
        employee.role = role.id
        db.commit()
        return {"detail": "Role added successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")
    except HTTPException:
        raise


@router.post("/create_new_role")
def create_new_role(
    role_name: str,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    try:
        if role_name == "superuser":
            raise HTTPException(status_code=401, detail="Not enough permissions")
        role = role_name.lower()
        try:
            new_role = Role(name=role)
            db.add(new_role)
            db.commit()
            return {"message": "Role created"}
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Role already exist")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/delete_role")
def delete_role(
    role_id: int,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    role = db.query(Role).get(role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    try:
        q = db.query(Permissions).filter(Permissions.role_id == role_id).first()
        db.delete(q)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/create_new_resource")
def create_new_resource(
    resource_name: str,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    try:
        resource = resource_name.lower()
        try:
            new_resource = Resource(name=resource)
            db.add(new_resource)
            db.commit()
            return {"message": "Resource created"}
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400, detail="Resource already exists with the same name"
            )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/delete_resource")
def delete_resource(
    resource_id: int,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    resource = db.query(Resource).get(resource_id)
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    try:
        p = db.query(Permissions).filter(Permissions.resource_id == resource_id).first()
        db.commit()
        db.delete(p)
        db.execute(delete(Resource).where(Resource.id == resource_id))
        db.commit()
        return {"message": "Role deleted"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/update_role_permissions")
def update_role_permissions(
    role_name: str,
    resource_name: str,
    read: bool,
    write: bool,
    update: bool,
    delete: bool,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    try:
        role = db.query(Role).filter(Role.name == role_name).first()
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        resource = db.query(Resource).filter(Resource.name == resource_name).first()
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource name not found")
        try:
            q = Permissions(
                role_id=role.id,
                resource_id=resource.id,
                read=read,
                write=write,
                update=update,
                delete=delete,
            )
            db.add(q)
            db.commit()
            return {"message": "Permissions created"}
        except IntegrityError:
            db.rollback()
            q = (
                db.query(Permissions)
                .where(
                    Permissions.role_id == role.id,
                    Permissions.resource_id == resource.id,
                )
                .first()
            )
            q.read = read
            q.write = write
            q.update = update
            q.delete = delete
            db.commit()
            return {"message": "Permissions updated"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


# Products routes
@router.post("/add-product")
async def add_new_product(
    product: ProductSchemaCreate,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    if any([employee.is_admin, employee.is_superuser]) is False:
        return HTTPException(status_code=401, detail="Not enough permissions")
    try:
        db_product = Products(
            name=product.name,
            slug=slugify(product.name),
            description=product.description,
            price=product.price,
            type=product.type,
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return {"id": db_product.id}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/add-product-images/{product_id}")
async def add_product_images(
    product_id: int,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db_session),
):
    print("recieved a request")
    try:
        if any([employee.is_admin, employee.is_superuser]) is False:
            return HTTPException(status_code=401, detail="Not enough permissions")
        product_db = db.query(Products).filter(Products.id == product_id).first()
        if product_db is None:
            raise HTTPException(status_code=404, detail="Product not found")
        images_entries = []
        for file in files:
            content = await file.read()
            with open(f"static/public/{product_id}_{file.filename}", "wb") as f:
                f.write(content)
                images_entries.append(
                    Image(
                        product_id=product_id,
                        image_path=f"static/public/{product_id}_{file.filename}",
                    )
                )
        db.add_all(images_entries)
        db.commit()
        return {"message": "Images added"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/update-topwear-inventory")
async def update_topwear_inventory(
    sizes: TopWearSizes,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    try:
        if any([employee.is_admin, employee.is_superuser]) is False:
            return HTTPException(status_code=401, detail="Not enough permissions")
        db_product = db.query(Products).filter(Products.id == sizes.product_id).first()
        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        # Todo make this check better
        topwear_size_ids = {
            "s": 1,
            "m": 2,
            "l": 3,
            "xl": 4,
            "xxl": 5,
        }
        inventory_details = (
            db.query(Inventory).filter(Inventory.product_id == sizes.product_id).all()
        )
        if not inventory_details:
            new_inventory_entries = [
                Inventory(
                    product_id=sizes.product_id,
                    size_id=topwear_size_ids.get("s"),
                    quantity=sizes.s,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=topwear_size_ids.get("m"),
                    quantity=sizes.m,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=topwear_size_ids.get("l"),
                    quantity=sizes.l,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=topwear_size_ids.get("xl"),
                    quantity=sizes.xl,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=topwear_size_ids.get("xxl"),
                    quantity=sizes.xxl,
                ),
            ]
            db.add_all(new_inventory_entries)
            db.commit()
            return {"message": "Inventory updated"}
        else:
            for inv in inventory_details:
                if inv.size_id == topwear_size_ids.get("s"):
                    inv.quantity = sizes.s
                if inv.size_id == topwear_size_ids.get("m"):
                    inv.quantity = sizes.m
                if inv.size_id == topwear_size_ids.get("l"):
                    inv.quantity = sizes.l
                if inv.size_id == topwear_size_ids.get("xl"):
                    inv.quantity = sizes.xl
                if inv.size_id == topwear_size_ids.get("xxl"):
                    inv.quantity = sizes.xxl
            db.commit()
            return {"message": "Inventory updated"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/update-bottomwear-inventory")
async def update_bottomwear_inventory(
    sizes: BottomWearSizes,
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    db: Session = Depends(get_db_session),
):
    try:
        if any([employee.is_admin, employee.is_superuser]) is False:
            return HTTPException(status_code=401, detail="Not enough permissions")
        db_product = db.query(Products).filter(Products.id == sizes.product_id).first()
        if db_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        # Todo make this check better
        bottomwear_size_ids = {
            "32": 6,
            "34": 7,
            "36": 8,
            "38": 9,
            "40": 10,
        }
        inventory_details = (
            db.query(Inventory).filter(Inventory.product_id == sizes.product_id).all()
        )
        if not inventory_details:
            new_inventory_entries = [
                Inventory(
                    product_id=sizes.product_id,
                    size_id=bottomwear_size_ids.get("32"),
                    quantity=sizes.size_32,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=bottomwear_size_ids.get("34"),
                    quantity=sizes.size_34,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=bottomwear_size_ids.get("36"),
                    quantity=sizes.size_36,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=bottomwear_size_ids.get("38"),
                    quantity=sizes.size_38,
                ),
                Inventory(
                    product_id=sizes.product_id,
                    size_id=bottomwear_size_ids.get("40"),
                    quantity=sizes.size_40,
                ),
            ]
            db.add_all(new_inventory_entries)
            db.commit()
            return {"message": "Inventory updated 1"}
        else:
            for inv in inventory_details:
                if inv.size_id == bottomwear_size_ids.get("32"):
                    inv.quantity = sizes.size_32
                if inv.size_id == bottomwear_size_ids.get("34"):
                    inv.quantity = sizes.size_34
                if inv.size_id == bottomwear_size_ids.get("36"):
                    inv.quantity = sizes.size_36
                if inv.size_id == bottomwear_size_ids.get("38"):
                    inv.quantity = sizes.size_38
                if inv.size_id == bottomwear_size_ids.get("40"):
                    inv.quantity = sizes.size_40
            db.commit()
            return {"message": "Inventory updated 2"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.get("/get-all-products")
def get_all_products(
    employee: Annotated[EmployeeSchema, Depends(get_employee)],
    page: int,
    per_page: int,
    name: str | None = None,
    db: Session = Depends(get_db_session),
):
    try:
        if any([employee.is_admin, employee.is_superuser]) is False:
            return HTTPException(status_code=401, detail="Not enough permissions")

        offset = (page - 1) * per_page
        stmt = select(Products.id, Products.name, Products.type, Products.price)
        if name:
            stmt = stmt.where(func.lower(Products.name).contains(func.lower(name)))
        stmt = stmt.offset(offset).limit(per_page)
        results = db.execute(stmt)
        items = results.fetchall()
        return_items = []
        for item in items:
            result = {}
            item_id, item_name, item_type, item_price = item
            result["pid"] = item_id
            result["name"] = item_name
            result["type"] = item_type
            result["price"] = item_price
            return_items.append(result)
        return return_items
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise
