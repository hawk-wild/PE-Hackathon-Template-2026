from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.domain import User
from app.models.schemas import UserCreate, UserOut, UserUpdate
from typing import List, Optional
from app.utils import parse_users_csv
from pydantic import ValidationError
from pydantic import EmailStr

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/bulk", response_model=dict)
async def create_users_bulk(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")
    
    content = await file.read()
    text_content = content.decode("utf-8")
    parsed_users = parse_users_csv(text_content)
    
    count = 0
    for user_data in parsed_users:
        try:
            # Simple validation using pure pydantic
            schema = UserCreate(username=user_data["username"], email=user_data["email"])
            if not db.query(User).filter(User.email == schema.email).first():
                db_user = User(username=schema.username, email=schema.email)
                db.add(db_user)
                count += 1
        except ValidationError:
            pass  # Skip invalid rows
    
    db.commit()
    return {"count": count}

@router.get("", response_model=List[UserOut])
def get_users(page: int = 1, per_page: int = 10, db: Session = Depends(get_db)):
    skip = (page - 1) * per_page
    users = db.query(User).offset(skip).limit(per_page).all()
    return users

@router.get("/{id}", response_model=UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/{id}", response_model=UserOut)
def update_user(id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.username is not None:
        db_user.username = user.username
        
    db.commit()
    db.refresh(db_user)
    return db_user
