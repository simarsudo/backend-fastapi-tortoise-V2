from datetime import timedelta
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.db_connection import get_db_session
from core.schema.user_schema import Token, User as UserSchema, CustomerSignUp
from core.utils.user_utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_customer,
    get_password_hash,
    verify_password,
)

from core.models.user_model import Customer, Address

router = APIRouter()


# TODO Add user schemas
# TODO add lower_case constraint


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db_session),
) -> Token:
    try:
        user = (
            db.query(Customer).filter(Customer.username == form_data.username).first()
        )
        if not user:
            print("User not found")
            raise HTTPException(status_code=401)
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(status_code=401)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        user.token = token
        db.commit()
        return Token(access_token=user.token, token_type="bearer")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/signup")
async def signup_user(customer: CustomerSignUp, db: Session = Depends(get_db_session)):
    # TODO optimize this code
    try:
        hashed_password = get_password_hash(customer.password)
        new_customer = Customer(
            username=customer.username,
            hashed_password=hashed_password,
            full_name=customer.full_name,
            email=customer.email,
            phone_no=customer.phone_no,
        )
        db.add(new_customer)
        db.commit()
        new_address = Address(
            name=customer.full_name,
            address=customer.address,
            city=customer.city,
            state=customer.state,
            pinCode=customer.pinCode,
            customer_id=new_customer.id,
        )
        db.add(new_address)
        db.commit()
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": customer.username}, expires_delta=access_token_expires
        )
        new_customer.token = token
        db.commit()
        return Token(access_token=new_customer.token, token_type="bearer")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500)
    except HTTPException:
        raise


@router.post("/logout")
def logout(
    current_user: Annotated[UserSchema, Depends(get_customer)],
    db: Session = Depends(get_db_session),
):
    current_user.token = ""
    db.commit()
    return {"message": "Successfully logged out"}


@router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[UserSchema, Depends(get_customer)],
):
    try:
        return current_user
    except HTTPException:
        raise HTTPException
