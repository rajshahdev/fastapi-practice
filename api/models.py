
from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP 
from .database import Base
from sqlalchemy.sql.expression import text
from datetime import datetime
from sqlalchemy.schema import FetchedValue

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(Text,nullable=False)
    content = Column(Text,nullable=False)
    published = Column(Boolean,default='True',nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    owner_id = Column(Integer,ForeignKey('users.id',ondelete="CASCADE") ,nullable=False)
    # so this is not any kind of foreign key or something rather sqlalchemy returns a piece of information
    # when ever we fetch from the posts table
    owner = relationship("User")
    vote = relationship("Votes")
    # mysql_engine='InnoDB'
    # mysql_charset='utf8mb4'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True,nullable=False)
    name = Column(String(200),nullable=False)
    email = Column(String(200),nullable=False)
    country = Column(String(200),nullable=False)
    city = Column(String(200),nullable=False)
    state = Column(String(200),nullable=False)
    address = Column(String(200),nullable=False)
    phone = Column(String(10),nullable=False)
    password = Column(String(200),nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))
    # created_at = datetime.utcnow()
    # mysql_engine='InnoDB'
    # mysql_charset='utf8mb4'

class Votes(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    posts_id = Column(Integer, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)










