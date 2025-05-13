from .database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Enum, DateTime, Text, Boolean
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum


class RoleChoices(str, PyEnum):
    guest = 'guest'
    host = 'host'


class PropertyTypeChoices(str, PyEnum):
    apartment = 'apartment'
    house = 'house'
    studio = 'studio'


class RulesChoices(str, PyEnum):
    no_smoking = 'no_smoking'
    pets_allowed = 'pets_allowed'


class BookingStatusChoices(str, PyEnum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'
    cancelled = 'cancelled'


class UserProfile(Base):
    __tablename__ = 'userprofile'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    email: Mapped[str] = mapped_column(String(86), unique=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[RoleChoices] = mapped_column(Enum(RoleChoices), default=RoleChoices.guest)
    phone_number: Mapped[Optional[str]] = mapped_column(String)
    avatar: Mapped[Optional[str]] = mapped_column(String)
    create_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    properties: Mapped[List['Property']] = relationship('Property', back_populates='owner',
                                                        cascade='all, delete-orphan')
    bookings: Mapped[List['Booking']] = relationship('Booking', back_populates='guest',
                                                     cascade='all, delete-orphan')
    reviews: Mapped[List['Review']] = relationship('Review', back_populates='guest',
                                                     cascade='all, delete-orphan')

class Images(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

    property_id: Mapped[int] = mapped_column(ForeignKey('property.id'))

    property: Mapped['Property'] = relationship('Property', back_populates='images')


class Property(Base):
    __tablename__ = 'property'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    price_per_night: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    property_type: Mapped[PropertyTypeChoices] = mapped_column(Enum(PropertyTypeChoices), default= PropertyTypeChoices.apartment)
    rules: Mapped[RulesChoices] = mapped_column(Enum(RulesChoices), default= RulesChoices.pets_allowed)
    max_guests: Mapped[int] = mapped_column(Integer)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean)

    owner_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))

    owner: Mapped['UserProfile'] = relationship('UserProfile', back_populates='properties')
    images: Mapped[List['Images']] = relationship('Images', back_populates='property', cascade='all, delete-orphan')
    bookings: Mapped[List['Booking']] = relationship('Booking', back_populates='property', cascade='all, delete-orphan')
    reviews: Mapped[List['Review']] = relationship('Review', back_populates='property')


class Booking(Base):
    __tablename__ = 'booking'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[BookingStatusChoices] = mapped_column(Enum(BookingStatusChoices), default=BookingStatusChoices.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    check_in: Mapped[int] = mapped_column(Integer)
    check_out: Mapped[int] = mapped_column(Integer)

    property_id: Mapped[int] = mapped_column(ForeignKey('property.id'))
    guest_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))

    property: Mapped['Property'] = relationship('Property', back_populates='bookings')
    guest: Mapped['UserProfile'] = relationship('UserProfile', back_populates='bookings')


class Review(Base):
    __tablename__ = 'review'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment: Mapped[str] = mapped_column(String(86))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    property_id: Mapped[int] = mapped_column(ForeignKey('property.id'))
    guest_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))

    property: Mapped['Property'] = relationship('Property', back_populates='reviews')
    guest: Mapped['UserProfile'] = relationship('UserProfile', back_populates='reviews')


class Amenity(Base):
    __tablename__ = 'amenity'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    icon: Mapped[str] = mapped_column(String, nullable=True)
