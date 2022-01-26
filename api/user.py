from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, UploadFile, File
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
import shutil, os
from . import oauth2
from pytz import timezone

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


@router.post('/otp', status_code=status.HTTP_200_OK)
def OtpEmail(userotp: schemas.OtpEmail, db: Session = Depends(get_db)):
    expires = datetime.utcnow() + timedelta(minutes=3)

    user_otp = db.query(models.User).filter(models.User.email == userotp.email)
    user_otp_verify = user_otp.first()

    user_id = user_otp_verify.id

    if user_otp_verify == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"the {userotp.email} is not found")

    randomnum = rand_pass(5)
    expires = expires.strftime('%Y-%m-%d %H:%M:%S.%f')

    generate_auth_email(randomnum, userotp.email)
    # print(schemas.Otp(email=userotp.email,otp = randomnum, expires=expires))
    new_otp = models.EmailOtp(
        **schemas.Otp(email=userotp.email, otp=randomnum, expires=expires, user_id=user_id).dict())

    db.add(new_otp)
    db.commit()
    return {"status": True, "data": {"id": user_otp_verify.id}, "message": "success"}

@router.post('/validateotp/{id}')
def validateotp(id:int,post_otp:schemas.validateotp, db: Session = Depends(get_db)):
    user_otp = db.query(models.EmailOtp).filter(models.EmailOtp.user_id == id)

    if user_otp.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid user")

    if datetime.utcnow() < user_otp.all()[-1].expires:
        if user_otp.all()[-1].otp == post_otp.otp:
            return {"status":True, "data":{"id":user_otp.all()[-1].user_id}, "message":"success"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Time out")


@router.post('/forget/{id}')
def forget(id: int, forget: schemas.ForgetPassword, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"the post with id {id} is not found")

    hashed_password = hash(forget.password)
    forget.password = hashed_password

    user_query.update(forget.dict(), synchronize_session=False)
    db.commit()
    return {"status": True, "data": {"id": user.id}, "message": "success"}


@router.post("/image/{id}")
def image(id: int, image: UploadFile = File(...), db: Session = Depends(get_db),
          user_id: int = Depends(oauth2.get_current_user)):
    if str(id) != user_id.id:

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User not found")

    direct_path = os.getcwd()

    folder_path = os.path.join(direct_path, 'imagefolder')

    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    image_folder_path = os.path.join(folder_path, f'{id}')

    if not os.path.isdir(image_folder_path):
        os.mkdir(image_folder_path)

    os.chdir(image_folder_path)

    ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d-%H:%M:%S')
    imagefilepath = os.path.join(image_folder_path, f'{id}_{ind_time}.png')
    # print(imagefilepath)
    with open(imagefilepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    os.chdir(direct_path)
    # timestamp_ind_time = datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')
    # save_image = models.Imagefile(**schemas.Imagefile(path=imagefilepath, user_id=id, timestamp=ind_time).dict())
    save_image = models.Imagefile(path=imagefilepath, user_id=id, timestamp=ind_time)
    db.add(save_image)
    db.commit()
    db.refresh(save_image)
    return {"status": True, "data": {"id": id, "image": imagefilepath, "timestamp": ind_time}}


@router.post('/image')
def getimage(schemas_user_id: schemas.Imageid, db: Session = Depends(get_db),
             user_id: int = Depends(oauth2.get_current_user)):
    if schemas_user_id.id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    print(type(schemas_user_id.id))
    user_query = db.query(models.Imagefile).filter(models.Imagefile.user_id == str(schemas_user_id.id)).all()
    # user = user_query.first()
    if not user_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User not found")
    return {"status": True, "data": user_query}