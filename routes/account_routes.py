import tortoise
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import tortoise.exceptions
from tortoise.transactions import in_transaction
from utils.customer_utils import get_customer
from utils.common_utils import get_password_hash, create_access_token, verify_password
from models import Customer, Address
from schema import CustomerSignUp, TokenOut, CustomerSchema

router = APIRouter()


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    customer = await Customer.get_or_none(username=form_data.username)
    if not customer:
        raise HTTPException(status_code=401)
    if not verify_password(form_data.password, customer.password_hash):
        raise HTTPException(status_code=401)
    token = create_access_token(data={"username": customer.username})
    customer.token = token
    await customer.save()
    return TokenOut(access_token=customer.token, token_type="bearer")


@router.post("/signup")
async def signup_user(customer: CustomerSignUp):
    try:
        async with in_transaction() as conn:
            password_hash = get_password_hash(customer.password)
            new_customer = await Customer.create(
                username=customer.username,
                password_hash=password_hash,
                full_name=customer.full_name,
                email=customer.email,
                phone_no=customer.phone_no,
            )
            await new_customer.save(using_db=conn)
            new_address = Address(
                name=customer.full_name,
                address=customer.address,
                city=customer.city,
                state=customer.state,
                pinCode=customer.pinCode,
                customer_id=new_customer.id,
            )
            await new_address.save(using_db=conn)
            token = create_access_token(data={"sub": customer.username})
            new_customer.token = token
            new_customer.save(using_db=conn)
            return TokenOut(access_token=new_customer.token, token_type="bearer")
    except tortoise.exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail="Account already exist")
    except tortoise.exceptions.OperationalError:
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/logout")
async def logout(current_user: Annotated[CustomerSchema, Depends(get_customer)]):
    current_user.token = ""
    await current_user.save()
    return {"message": "Successfully logged out"}