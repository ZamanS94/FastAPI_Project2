from fastapi import FastAPI, HTTPException, Depends, status
from app.schemas import PostCreate, PostUpdate, PostResponse
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text
from app import models
from app.db import engine, get_db

#table
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is running"}


#all posts
@app.get("/posts",response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


# post creation
@app.post("/posts", status_code=status.HTTP_201_CREATED,response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):

    new_post = models.Post(title=post.title,content=post.content,published=post.published)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# single post
@app.get("/posts/{id}",response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


# post deletion
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
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

    return


# updating post
@app.put("/posts/{id}",response_model=PostResponse)
def update_post(id: int, post: PostUpdate, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id)

    existing_post = post_query.first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post_query.update({"title": post.title,"content": post.content,"published": post.published},
                      synchronize_session=False)

    db.commit()

    updated_post = post_query.first()

    return updated_post


# testing db connection
@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        return {"db_status": "OK", "result": result[0]}
    except Exception as e:
        return {"db_status": "FAILED", "error": str(e)}