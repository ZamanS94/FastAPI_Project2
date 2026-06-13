from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app import models
from app.db import get_db
from app.schemas import UserCreate, UserResponse
from app.utils.utils import hash

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    password = hash(user.password)

    new_user = models.User(
        email=user.email,
        password=password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.id == id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user