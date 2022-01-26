from pydantic import BaseModel, validator, ValidationError, Field
from datetime import datetime

from typing import Optional, Text

from pydantic.networks import EmailStr
from pydantic.types import constr, conint

class UserOut(BaseModel):
    id: int
    name : constr(min_length=1)
    email : EmailStr
    country: str
    city: str
    state : str
    address: constr(min_length=10)
    phone: constr(min_length=10, max_length=10)
    class Config:
        orm_mode = True

# user sends data to us 
class PostBase(BaseModel):
    title : str
    content : str
    published : bool = True

class PostCreate(PostBase):
    pass


# and now we send data to user
class PostResponse(PostBase):
    id : int
    created_at : datetime
    owner_id : int
    owner: UserOut
    class Config:
        orm_mode = True

class PostVoteOut(BaseModel):
    Post: PostResponse
    votes:int

    class Config:
        orm_mode=True


class OtpEmail(BaseModel):
    email: EmailStr


class Otp(OtpEmail):
    otp: str
    expires: datetime
    user_id: int


class validateotp(BaseModel):
    otp: str

class Imagefile(BaseModel):
    path: str
    user_id:int
    timestamp:str

class Imageid(BaseModel):
    id:int

class ImageList(BaseModel):
    path: List[str]

    class Config:
        orm_mode = True


class Imageout(ImageList):
    status = bool

class UserBase(BaseModel):
    name : constr(min_length=1)
    email : EmailStr
    country: str
    city: str
    state : str
    address: constr(min_length=10)
    phone: constr(min_length=10, max_length=10)
    password: str



class UserOutSchema(BaseModel):
    status : bool
    data : UserOut
    message: str

class Profilebase(BaseModel):
    name : constr(min_length=1)
    country: str
    city: str
    state : str
    address: constr(min_length=10)
    phone: constr(min_length=10, max_length=10)

class ProfileOut(Profilebase):

    class Config:
        orm_mode = True

class ProfileOutSchema(BaseModel):
    status : bool
    data : ProfileOut
    message: str



class UserLogin(BaseModel):
    email : EmailStr
    password: str

class Token(BaseModel):
    access_token : str
    token_type : str

class Tokendata(BaseModel):
    id : Optional[str] = None



class Votes(BaseModel):
    posts_id:int
    dir:conint(le=1)

# class UserCreate(BaseModel):
#     id : int
#     email : EmailStr
#     created_at : datetime

#     class Config:
#         orm_mode = True

# class UserOut(BaseModel):
#     id: int
#     email: EmailStr

#     class Config:
#         orm_mode = True

