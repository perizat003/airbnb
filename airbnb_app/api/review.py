from airbnb_app.db.database import SessionLocal
from airbnb_app.db.models import Review, Booking
from airbnb_app.db.schema import ReviewSchema, ReviewCreateSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from typing import List
from datetime import datetime


review_router = APIRouter(prefix="/review", tags=["Review"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@review_router.post('/create/', response_model=ReviewSchema)
async def create_review(review_data: ReviewCreateSchema, db: Session = Depends(get_db)):
    existing = db.query(Review).filter(Review.property_id == review_data.property_id,
                                       Review.guest_id == review_data.guest_id).first()
    if existing:
        raise HTTPException(status_code=400, detail='Вы уже оставили отзыв об этом объекте недвижимости')

    booking = db.query(Booking).filter(Booking.property_id == review_data.property_id,
                                       Booking.guest_id == review_data.guest_id,
                                       Booking.status == 'approved',
                                       Booking.check_out < datetime.utcnow()).first()

    if not booking:
        raise HTTPException(status_code=403,
                            detail='Чтобы оставить отзыв, у вас должно быть завершенное бронирование')

    new_review = Review(**review_data.dict())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review


@review_router.get('/', response_model=List[ReviewSchema])
async def list_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()


@review_router.get('/{review_id}/', response_model=ReviewSchema)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail='Review не найден')
    return review


@review_router.put('/{review_id}/', response_model=ReviewSchema)
async def update_review(review_id: int, review_data: ReviewCreateSchema,
                        db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail='Review не найден')

    for review, review_key, review_value in review_data.dict().items():
        setattr(review, review_key, review_value)

    db.commit()
    db.refresh(review)
    return review


@review_router.delete('/{review_id}/')
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail='Review не найден')

    db.delete(review)
    db.commit()
    return {'message': 'Отзыв успешно удален'}


@review_router.get('/property/{property_id}/', response_model=List[ReviewSchema])
async def list_reviews_by_property(property_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.property_id == property_id).all()
