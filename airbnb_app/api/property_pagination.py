from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from airbnb_app.db.database import SessionLocal
from airbnb_app.db.models import Property
from airbnb_app.db.schema import PropertySchema

pagination_router = APIRouter(prefix='/property', tags=['PropertyAdvanced'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pagination_router.get('/search/', response_model=List[PropertySchema])
async def search_properties(
    db: Session = Depends(get_db),
    city: Optional[str] = None,
    min_price: Optional[int] = Query(None, ge=0),
    max_price: Optional[int] = Query(None, ge=0),
    property_type: Optional[str] = None,
    min_guests: Optional[int] = Query(None, ge=1),  # фильтр по минимум гостей
    order_by: Optional[str] = None,  # price_asc, price_desc, rating_desc, date_desc

    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    query = db.query(Property).filter(Property.is_approved == True)  # показываем только одобренные

    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if not min_price:
        query = query.filter(Property.price_per_night >= min_price)
    if not max_price:
        query = query.filter(Property.price_per_night <= max_price)
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if not min_guests:
        query = query.filter(Property.max_guests >= min_guests)

    if order_by == "price_asc":
        query = query.order_by(Property.price_per_night.asc())
    elif order_by == "price_desc":
        query = query.order_by(Property.price_per_night.desc())
    elif order_by == "rating_desc":
        query = query.order_by(Property.rating.desc())
    elif order_by == "date_desc":
        query = query.order_by(Property.created_at.desc())

    properties = query.offset(offset).limit(limit).all()
    return properties
