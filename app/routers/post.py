from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app import models
from app.db import get_db
from app.schemas import PostCreate, PostUpdate, PostResponse

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("", response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):

    new_post = models.Post(
        title=post.title,
        content=post.content,
        published=post.published
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post_query.delete(synchronize_session=False)
    db.commit()


@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, post: PostUpdate, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    existing_post = post_query.first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
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