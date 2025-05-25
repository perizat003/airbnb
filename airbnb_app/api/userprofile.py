from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from airbnb_app.db.database import SessionLocal
from airbnb_app.db.models import UserProfile
from airbnb_app.db.schema import UserProfileSchema, UserProfileUpdateSchema
from airbnb_app.api.auth import register, get_password_hash, verify_password


user_router = APIRouter(prefix="/users", tags=["User Profile"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_router.post("/create", response_model=dict)
async def create_user(user: UserProfileSchema, db: Session = Depends(get_db)):
    return await register(user, db)


@user_router.put('/update/', response_model=dict)
async def update_user(update_data: UserProfileUpdateSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username == update_data.username).first()
    if not user_db or not verify_password(update_data.password, user_db.password):
        raise HTTPException(status_code=403, detail="Неправильный username или password")

    for user_key, user_value in update_data.dict().items():
        setattr(user_db, user_key, user_value)

    db.commit()
    db.refresh(user_db)
    return {"message": "Profile обновлен"}


@user_router.delete('/delete/{username}/', response_model=dict)
async def delete_user(username: str, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User не найден")

    db.delete(user)
    db.commit()
    return {"message": "User удален"}

