from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .database import get_db
from . import oauth2
from . import schemas
from . import models

router = APIRouter(
    prefix='/votes',
    tags=['Vote']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def votes(vote: schemas.Votes, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    vote_query = db.query(models.Votes).filter(models.Votes.posts_id == vote.posts_id,
                                               models.Votes.user_id == user_id.id)
    found_vote = vote_query.first()

    post_query = db.query(models.Post).filter(models.Post.id == vote.posts_id).first()
    if not post_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post not exist")

    if vote.dir == 1:
        # to check if the vote already exist
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {user_id.id} has already voted on post {vote.posts_id}")
        new_vote = models.Votes(user_id=user_id.id, posts_id=vote.posts_id)
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return {"message": "vote added successfully "}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"vote does not exist")
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "vote deleted successfully "}
