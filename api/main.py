from fastapi import FastAPI
from . import models
from .database import engine, SessionLocal, get_db
from . import post, user, auth, votes

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastApi-BlogApp",
    description="This api is fully functional api and anyone can use it. \n\n checkout my github repo.:- https://github.com/rajshahdev/fastapi-practice",
    version="0.0.1",
    contact={
        "name": "Raj Shah",
        "email": "be.rajshah@gmail.com",
    }
)
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(votes.router)
