from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional, List
from sqlalchemy.orm.session import Session
from typing import Optional
from . import models
from . import schemas
from .database import get_db
from . import oauth2
router = APIRouter(
    prefix = '/posts',
    tags = ['posts']
)

@router.get("/", response_model=List[schemas.PostResponse])
def GetPost(db: Session = Depends(get_db),user_id:int = Depends(oauth2.get_current_user), limit:int = 10, offset:int =2, search: Optional[str]=""):
    
    # we can put any amount of details in payload and you can configure the payload in auth.py(login)
    print(user_id.id)
    # print(limit)
    # print(offset)
    # print(search)
    # if we want only post we created then
    
    # posts = db.query(models.Post).filter(models.Post.owner_id == user_id.id).all()
    
    # if we want to show all the posts then
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(offset).all()
    return posts


@router.get('/{id}', response_model=schemas.PostResponse)
def GetPostNum(id: int, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.id == str(id)).first()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"the post with id {id} is not found")
    return posts


@router.post('/',status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def CreatePost(post:schemas.PostBase, db: Session = Depends(get_db),user_id:int = Depends(oauth2.get_current_user)):

    print(user_id.id)
    new_post = models.Post(owner_id=user_id.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def DeletePosts(id:int,db: Session = Depends(get_db), user_id:int = Depends(oauth2.get_current_user)):
    delete_posts = db.query(models.Post).filter(models.Post.id == id)
    if delete_posts.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"the post with id {id} is not found")
    
    # we have to check that is the post really owns by user? so 
    if delete_posts.first().owner_id != user_id.id: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not Authorize")


    delete_posts.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.PostResponse)
def UpdatePosts(id:int,posts:schemas.PostCreate, db:Session = Depends(get_db), user_id:int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"the post with id {id} is not found")

    # checking is the post is really owns the owner
    if post.owner_id != user_id.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    post_query.update(posts.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()
