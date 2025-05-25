from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from .models import (RoleChoices, PropertyTypeChoices,
                     RulesChoices, BookingStatusChoices,
                     bcrypt)


class UserProfileSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: RoleChoices
    phone_number: Optional[str]
    avatar: Optional[str]
    create_date: datetime

    class Config:
        from_attributes = True


class UserProfileLoginSchema(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class UserProfileUpdateSchema(BaseModel):
    username: str
    password: str
    email: Optional[str]
    phone_number: Optional[str]
    avatar: Optional[str]


class PropertyImagesSchema(BaseModel):
    id: int
    image_url: str
    property_id: int

    class Config:
        from_attributes = True


class PropertySchema(BaseModel):
    id: int
    title: str
    description: str
    price_per_night: int
    city: str
    address: str
    property_type: PropertyTypeChoices
    rules: RulesChoices
    max_guests: int
    bedrooms: int
    bathrooms: int
    is_active: bool
    owner_id: int

    class Config:
        from_attributes = True


class PropertyCreateSchema(BaseModel):
    title: str
    description: str
    price_per_night: int
    city: str
    address: str
    property_type: PropertyTypeChoices
    rules: RulesChoices
    max_guests: int
    bedrooms: int
    bathrooms: int
    is_active: bool
    owner_id: int

    class Config:
        from_attributes = True


class BookingSchema(BaseModel):
    id: int
    status: BookingStatusChoices
    created_at: datetime
    check_in: datetime
    check_out: datetime
    property_id: int
    guest_id: int

    class Config:
        from_attributes = True


class BookingCreateSchema(BaseModel):
    check_in: datetime
    check_out: datetime
    property_id: int
    guest_id: int

    class Config:
        from_attributes = True



class ReviewSchema(BaseModel):
    id: int
    comment: str
    created_at: datetime
    rating: int = Field(None, gt=0, lt=6)
    property_id: int
    guest_id: int

    class Config:
        from_attributes = True


class ReviewCreateSchema(BaseModel):
    comment: str
    rating: int = Field(None, gt=0, lt=6)
    property_id: int
    guest_id: int

    class Config:
        from_attributes = True


class MessageSchema(BaseModel):
    id: int
    status: BookingStatusChoices
    created_at: datetime
    booking_id: int

    class Config:
        orm_mode = True

class StatusUpdateSchema(BaseModel):
    new_status: BookingStatusChoices

    class Config:
        orm_mode = True
