from .database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Enum, DateTime, Text, Boolean
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum
from passlib.hash import bcrypt


class RoleChoices(str, PyEnum):
    guest = 'guest'
    host = 'host'
    admin = 'admin'


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
    __tablename__ = 'user_profile'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    email: Mapped[str] = mapped_column(String(86), unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleChoices] = mapped_column(Enum(RoleChoices), default=RoleChoices.guest)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    create_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    properties: Mapped[List['Property']] = relationship('Property', back_populates='owner',
                                                        cascade='all, delete-orphan')
    bookings: Mapped[List['Booking']] = relationship('Booking', back_populates='guest',
                                                     cascade='all, delete-orphan')
    reviews: Mapped[List['Review']] = relationship('Review', back_populates='guest',
                                                   cascade='all, delete-orphan')
    user_token: Mapped[List['RefreshToken']] = relationship('RefreshToken', back_populates='user',
                                                            cascade='all, delete-orphan')
    messages: Mapped[List['UserProfile']] = relationship('Message', back_populates='host',
                                                         cascade='all, delete-orphan')


    def set_password(self, password: str):
        self.password = bcrypt.hash(password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password)

    def __repr__(self):
        return f'{self.username}'


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user_profile.id'))

    user: Mapped[UserProfile] = relationship('UserProfile', back_populates='user_token')
    token: Mapped[str] = mapped_column(String, nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())


class PropertyImages(Base):
    __tablename__ = 'property_images'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_url: Mapped[str] = mapped_column(String, nullable=False)

    property_id: Mapped[int] = mapped_column(ForeignKey('property.id'))

    property_image: Mapped['Property'] = relationship('Property', back_populates='images')


class Property(Base):
    __tablename__ = 'property'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    price_per_night: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String)
    address: Mapped[str] = mapped_column(String)
    property_type: Mapped[PropertyTypeChoices] = mapped_column(Enum(PropertyTypeChoices),
                                                               default= PropertyTypeChoices.apartment)
    rules: Mapped[RulesChoices] = mapped_column(Enum(RulesChoices),
                                                default= RulesChoices.pets_allowed)
    max_guests: Mapped[int] = mapped_column(Integer)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean)

    owner_id: Mapped[int] = mapped_column(ForeignKey('user_profile.id'))

    owner: Mapped[['UserProfile']] = relationship('UserProfile', back_populates='properties')
    images: Mapped[List['PropertyImages']] = relationship('PropertyImages', back_populates='property_image',
                                                          cascade='all, delete-orphan')
    bookings: Mapped[List['Booking']] = relationship('Booking', back_populates='property',
                                                     cascade='all, delete-orphan')
    reviews: Mapped[List['Review']] = relationship('Review', back_populates='property',
                                                   cascade='all, delete-orphan')


class Booking(Base):
    __tablename__ = 'booking'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[BookingStatusChoices] = mapped_column(Enum(BookingStatusChoices), default=BookingStatusChoices.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    check_in: Mapped[datetime] = mapped_column(DateTime)
    check_out: Mapped[datetime] = mapped_column(DateTime)

    property_id: Mapped[int] = mapped_column(ForeignKey('property.id'))
    guest_id: Mapped[int] = mapped_column(ForeignKey('user_profile.id'))

    property: Mapped['Property'] = relationship('Property', back_populates='bookings')
    guest: Mapped['UserProfile'] = relationship('UserProfile', back_populates='bookings')
    messages: Mapped[List['Message']] = relationship('Message', back_populates='booking',
                                                     cascade='all, delete-orphan')



class Review(Base):
    __tablename__ = 'review'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment: Mapped[str] = mapped_column(String(86))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    rating: Mapped[int] = mapped_column(Integer)

    property_id: Mapped[int] = mapped_column(ForeignKey('property.id'))
    guest_id: Mapped[int] = mapped_column(ForeignKey('user_profile.id'))

    property: Mapped['Property'] = relationship('Property', back_populates='reviews')
    guest: Mapped['UserProfile'] = relationship('UserProfile', back_populates='reviews')



class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[BookingStatusChoices] = mapped_column(Enum(BookingStatusChoices), default=BookingStatusChoices.pending)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    booking_id: Mapped[int] = mapped_column(ForeignKey('booking.id'))
    host_id: Mapped[int] = mapped_column(ForeignKey('user_profile.id'))

    booking: Mapped['Booking'] = relationship('Booking', back_populates='messages')
    host: Mapped['UserProfile'] = relationship('UserProfile', back_populates='messages')
