from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from sqlalchemy.orm.session import Session
from . import models
from fastapi.responses import JSONResponse
from .utils import hash, rand_pass, welcome_auth_email, generate_auth_email
from . import schemas
from .database import get_db
from fastapi.encoders import jsonable_encoder
import json
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/users",
    tags=['users']
)


@router.post('/', response_model=schemas.UserOutSchema)
def UserCreate(users: schemas.UserBase, db: Session = Depends(get_db)):
    # print(db.query(models.User).filter(models.User.username == users.username).first().username)
    if db.query(models.User).filter(models.User.email == users.email).first() != None:
        if users.email == db.query(models.User).filter(models.User.email == users.email).first().email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="email already exist")

    users.password = hash(users.password)
    new_user = models.User(**users.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # return new_user
    # otp verification code from EmailOtp function
    expires = datetime.utcnow() + timedelta(minutes=3)

    randomnum = rand_pass(5)
    expires = expires.strftime('%Y-%m-%d %H:%M:%S.%f')

    welcome_auth_email(users.name, randomnum, users.email)
    # generate_auth_email(randomnum,users.email)
    # print(schemas.Otp(email=userotp.email,otp = randomnum, expires=expires))
    new_otp = models.EmailOtp(
        **schemas.Otp(email=users.email, otp=randomnum, expires=expires, user_id=new_user.id).dict())

    db.add(new_otp)
    db.commit()
    return {"status": True, "data": new_user, "message": "User Created Successfully"}


@router.get('/{id}', response_model=schemas.UserOutSchema)
def GetUser(id: int, db: Session = Depends(get_db)):
    get_user = db.query(models.User).filter(models.User.id == id).first()

    if not get_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"the user {id} is not found")

    return {"status": True, "data": get_user, "message": "User Fetched Successfully"}


@router.put("/{id}", response_model=schemas.ProfileOutSchema)
def UpdateUser(id: int, users: schemas.Profilebase, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"the post with id {id} is not found")
    user_query.update(users.dict(), synchronize_session=False)
    db.commit()
    return {"status": True, "data": user_query.first(), "message": "User Modified Successfully"}
