from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func

from app import models
from app.db import get_db
from app.schemas import PostCreate, PostUpdate, PostResponse, PostOut
from app.oauth2 import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("", response_model=List[PostOut],)
#def get_posts(db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user),
 #             limit: int=10,search: Optional[str]=""):
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):   
    #print(current_user.email)
    #return db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).all()
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):

    new_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published,
        owner_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=PostOut,)
def get_post(id: int, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):

    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this post"
        )

    post_query.delete(synchronize_session=False)
    db.commit()

@router.put("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if existing_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this post"
        )

    post_query.update(
        {
            "title": post.title,
            "content": post.content,
            "published": post.published
        },
        synchronize_session=False
    )

    db.commit()

    return post_query.first()