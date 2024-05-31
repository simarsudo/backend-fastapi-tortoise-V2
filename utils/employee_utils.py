from typing import Annotated
from jose import jwt
from fastapi import Depends, HTTPException
from config import (
    SECRET_KEY,
    ALGORITHM,
    oauth2_scheme,
)
from models import Employee


async def get_employee(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise
        employee = await Employee.get_or_none(username=username, token=token)
        if employee is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if employee.is_disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        if any([employee.is_admin, employee.is_superuser, employee.is_staff]) is False:
            employee.token = ""
            await employee.save()
            raise HTTPException(
                status_code=403,
                detail="Unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return employee
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=401,
            detail="Token has Invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token has Invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
