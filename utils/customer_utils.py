from typing import Annotated
from jose import jwt
from fastapi import Depends, HTTPException
from config import (
    SECRET_KEY,
    ALGORITHM,
    oauth2_scheme,
)
from models import Customer
from schema import CustomerSchema


async def get_customer(token: Annotated[str, Depends(oauth2_scheme)]) -> CustomerSchema:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=403,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        customer = await Customer.get_or_none(username=username, token=token)
        if customer is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if customer.is_disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return customer
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=403,
            detail="Token has Invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=403,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=403,
            detail="Token has Invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
