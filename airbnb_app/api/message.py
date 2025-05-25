from airbnb_app.db.database import SessionLocal
from airbnb_app.db.models import Message, BookingStatusChoices, Booking, UserProfile
from airbnb_app.db.schema import MessageSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from typing import List
from pydantic import BaseModel
from airbnb_app.api.auth import get_current_user

message_router = APIRouter(prefix="/messages", tags=["Messages"])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StatusUpdateSchema(BaseModel):
    new_status: BookingStatusChoices


@message_router.get("/host/{host_id}/", response_model=List[MessageSchema])
async def get_host_messages(host_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).join(Message.booking).join(Booking.property)\
        .filter(Booking.property.has(owner_id=host_id)).all()
    return messages


@message_router.post("/{message_id}/approve", response_model=MessageSchema)
async def approve_booking_request(message_id: int,status_update: StatusUpdateSchema,
                                  db: Session = Depends(get_db),
                                  current_user: UserProfile = Depends(get_current_user)):
    new_status = status_update.new_status

    if new_status not in [BookingStatusChoices.approved, BookingStatusChoices.rejected]:
        raise HTTPException(status_code=400, detail='Неверный статус')

    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message не найден")

    booking = db.query(Booking).filter(Booking.id == message.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking не найден")

    if booking.property.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не владелец этого объекта")

    message.status = new_status
    booking.status = new_status

    db.commit()
    db.refresh(message)
    return message
