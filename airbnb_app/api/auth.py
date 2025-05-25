from airbnb_app.db.database import SessionLocal
from airbnb_app.db.models import UserProfile, RefreshToken
from airbnb_app.db.schema import UserProfileSchema, UserProfileLoginSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from typing import List, Optional
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from airbnb_app.cinfig import (ALGORITHM, SECRET_KEY, ACCESS_TOKEN_LIFETIME,
                               REFRESH_TOKEN_LIFETIME)
from datetime import timedelta, datetime
from jose import JWTError



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserProfile:
    credentials_exception = HTTPException(status_code=401,detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserProfile).filter(UserProfile.username == username).first()
    if user is None:
        raise credentials_exception
    return user



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta]= None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_LIFETIME))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_LIFETIME))


@auth_router.post('/register', response_model=dict)
async def register(user: UserProfileSchema, db: Session = Depends(get_db)):
    hash_password = get_password_hash(user.password)
    user_db = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    user_email = db.query(UserProfile).filter(UserProfile.email == user.email).first()
    if user_db:
        raise HTTPException(status_code=400, detail='username бар экен')
    elif user_email:
        raise HTTPException(status_code=400, detail='email бар экен')
    user_db = UserProfile(
        username = user.username,
        email = user.email,
        role = user.role,
        phone_number = user.phone_number,
        avatar = user.avatar,
        create_date = user.create_date,
        password = hash_password
    )

    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return {'message': 'Registered'}


@auth_router.post('/login')
async def login(form_data: UserProfileLoginSchema ,
                db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail='Малымат туура эмес')

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})

    new_token = RefreshToken(user_id=user.id, token=refresh_token)
    db.add(new_token)
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth_router.post('/logout')
async def logout(refresh_token: str, db: Session = Depends(get_db)):

    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()

    if not stored_token:
        raise HTTPException(status_code=401, detail='Малымат туура эмес')

    db.delete(stored_token)
    db.commit()

    return {"message": "Вышли"}


@auth_router.post('/refresh')
async def refresh(refresh_token: str,db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=401, detail='Малымат туура эмес')

    user = db.query(UserProfile).filter(UserProfile.id == stored_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token({"sub": stored_token.id})

    return {"access_token": access_token,"token_type": "bearer"}