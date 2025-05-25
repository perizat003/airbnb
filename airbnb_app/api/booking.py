from airbnb_app.db.database import SessionLocal
from airbnb_app.db.models import Booking, BookingStatusChoices, Message, Property, UserProfile
from airbnb_app.db.schema import BookingSchema, BookingCreateSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from typing import List
from datetime import datetime, timedelta
from airbnb_app.api.auth import get_current_user

booking_router = APIRouter(prefix="/booking", tags=["Booking"])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@booking_router.post('/create/', response_model=BookingSchema)
async def create_booking(data: BookingCreateSchema, db: Session = Depends(get_db),
                         current_user: UserProfile = Depends(get_current_user)):
    if current_user.role != 'guest':
        raise HTTPException(status_code=403, detail="Only guests can make bookings")

    now = datetime.utcnow()
    if data.check_in.date() < now.date():
        raise HTTPException(status_code=400, detail='Check-in не может быть в прошлом')

    if (data.check_out - data.check_in).days < 1:
        raise HTTPException(status_code=400, detail='Бронирование должно быть минимум на 1 ночь')

    property_obj = db.query(Property).filter(Property.id == data.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail='Property не найден')

    overlapping = db.query(Booking).filter(
        Booking.property_id == data.property_id,
        Booking.status == BookingStatusChoices.approved,
        Booking.check_out > data.check_in,
        Booking.check_in < data.check_out
    ).first()
    if overlapping:
        raise HTTPException(status_code=409, detail='Этот объект уже забронирован на эту дату')

    new_booking = Booking(**data.dict(), guest_id=current_user.id)
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    message = Message(
        status=BookingStatusChoices.pending,
        booking_id=new_booking.id,
        renter=property_obj.owner
    )
    db.add(message)
    db.commit()

    return new_booking

@booking_router.get("/", response_model=List[BookingSchema])
async def list_bookings(db: Session = Depends(get_db),
                        current_user: UserProfile = Depends(get_current_user)):
    return db.query(Booking).all()

@booking_router.get('/{booking_id}/', response_model=BookingSchema)
async def get_booking(booking_id: int, db: Session = Depends(get_db),
                      current_user: UserProfile = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail='Booking не найден')
    return booking

@booking_router.put('/{booking_id}/', response_model=BookingSchema)
async def update_booking(booking_id: int, booking_data: BookingCreateSchema,
                         db: Session = Depends(get_db),
                         current_user: UserProfile = Depends(get_current_user)):
    booking_db = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking_db is None:
        raise HTTPException(status_code=404, detail='Booking не найден')

    if booking_db.guest_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")

    for booking_key, booking_value in booking_data.dict().items():
        setattr(booking_db, booking_key, booking_value)

    db.add(booking_db)
    db.commit()
    db.refresh(booking_db)
    return booking_db

@booking_router.delete('/{booking_id}/')
async def delete_booking(booking_id: int, db: Session = Depends(get_db),
                         current_user: UserProfile = Depends(get_current_user)):
    booking_db = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking_db is None:
        raise HTTPException(status_code=404, detail='Booking не найден')

    if booking_db.guest_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")

    db.delete(booking_db)
    db.commit()
    return {'message': 'Бронирование успешно удалено'}

@booking_router.get('/guest/{guest_id}/', response_model=List[BookingSchema])
async def list_bookings_by_guest(guest_id: int, db: Session = Depends(get_db),
                                 current_user: UserProfile = Depends(get_current_user)):
    if current_user.id != guest_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")

    return db.query(Booking).filter(Booking.guest_id == guest_id).all()
