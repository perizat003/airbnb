from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .models import RoleChoices, PropertyTypeChoices, RulesChoices, BookingStatusChoices


class UserProfileSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    role: RoleChoices
    phone_number: Optional[str]
    avatar: Optional[str]
    create_date: datetime

    class Config:
        from_attributes = True


class Images(BaseModel):
    id: int
    image_url: str
    property_id: int

    class Config:
        from_attributes = True


class Property(BaseModel):
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


class Booking(BaseModel):
    id: int
    status: BookingStatusChoices
    created_at: datetime
    check_in: int
    check_out: int
    property_id: int
    guest_id: int

    class Config:
        from_attributes = True


class Review(BaseModel):
    id: int
    comment: str
    created_at: datetime
    property_id: int
    guest_id: int

    class Config:
        from_attributes = True


class Amenity(BaseModel):
    id: int
    name: str
    icon: str

    class Config:
        from_attributes = True