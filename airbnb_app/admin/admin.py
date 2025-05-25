from fastapi import Depends, HTTPException, status, APIRouter
from airbnb_app.api.auth import get_current_user
from airbnb_app.db.models import UserProfile,Property
from airbnb_app.db.database import SessionLocal
from sqlalchemy.orm import Session


admin_router = APIRouter(prefix="/admin", tags=["Admin"])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def admin_only(current_user: UserProfile = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins have access to this resource"
        )
    return current_user


@admin_router.put("/user/{user_id}/block", dependencies=[Depends(admin_only)])
async def block_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.username} заблокирован"}


@admin_router.put("/user/{user_id}/unblock")
async def unblock_user(user_id: int, db: Session = Depends(get_db),
                       current_user: UserProfile = Depends(admin_only)):
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": f"User {user.username} разблокирован"}


@admin_router.put("/property/{property_id}/approve", dependencies=[Depends(admin_only)])
async def approve_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    property_obj.is_approved = True
    db.commit()
    return {"message": "Property approved successfully"}


@admin_router.delete("/user/{user_id}", dependencies=[Depends(admin_only)])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


from sqlalchemy import func


@admin_router.get("/stats")
async def get_stats(db: Session = Depends(get_db),
                    current_user: UserProfile = Depends(admin_only)):
    total_users = db.query(func.count(UserProfile.id)).scalar()
    active_users = (db.query(func.count(UserProfile.id)).filter
                    (UserProfile.is_active == True).scalar())
    total_bookings = db.query(func.count(Booking.id)).scalar()
    active_bookings = (db.query(func.count(Booking.id)).filter
                       (Booking.status == BookingStatusChoices.approved).scalar())


    popular_cities = (
        db.query(Property.city, func.count(Property.id).label("count"))
        .group_by(Property.city)
        .order_by(func.count(Property.id).desc())
        .limit(5)
        .all()
    )


    total_revenue = db.query(func.sum(Booking.total_price)).filter(
        Booking.status == BookingStatusChoices.approved).scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "popular_cities": popular_cities,
        "total_revenue": total_revenue
    }
