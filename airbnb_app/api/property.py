from airbnb_app.db.database import SessionLocal
from airbnb_app.db.models import Property, UserProfile
from airbnb_app.db.schema import PropertySchema, PropertyCreateSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from typing import List
from airbnb_app.api.auth import get_current_user
from airbnb_app.admin.admin import admin_router, admin_only  # Не забудь подключить

property_router = APIRouter(prefix='/property', tags=['Property'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@property_router.post('/create/', response_model=PropertySchema)
async def create_property(prop_data: PropertyCreateSchema, db: Session = Depends(get_db),
                          current_user: UserProfile = Depends(get_current_user)):
    if current_user.role != 'host':
        raise HTTPException(status_code=403, detail="Only hosts can create properties")

    property_db = Property(**prop_data.dict(), owner_id=current_user.id)
    db.add(property_db)
    db.commit()
    db.refresh(property_db)
    return property_db

@property_router.get('/', response_model=List[PropertySchema])
async def list_property(db: Session = Depends(get_db)):
    return db.query(Property).filter(Property.is_approved == True).all()

@property_router.get('/{property_id}/', response_model=PropertySchema)
async def detail_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail='Property не найден')
    return prop

@property_router.put('/{property_id}/', response_model=PropertySchema)
async def update_property(property_id: int, prop_data: PropertyCreateSchema,
                          db: Session = Depends(get_db),
                          current_user: UserProfile = Depends(get_current_user)):
    property_db = db.query(Property).filter(Property.id == property_id).first()

    if property_db.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этому объекту")

    if property_db is None:
        raise HTTPException(status_code=404, detail='Property не найден')

    if property_db.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")

    for key, value in prop_data.dict().items():
        setattr(property_db, key, value)

    db.add(property_db)
    db.commit()
    db.refresh(property_db)
    return property_db



@property_router.delete('/{property_id}/')
async def delete_property(property_id: int, db: Session = Depends(get_db),
                          current_user: UserProfile = Depends(get_current_user)):
    property_db = db.query(Property).filter(Property.id == property_id).first()
    if property_db is None:
        raise HTTPException(status_code=404, detail='Property не найден')

    if property_db.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Нет доступа")

    db.delete(property_db)
    db.commit()
    return {'message': 'ресурс успешно удален'}

@property_router.get('/owner/{owner_id}/', response_model=List[PropertySchema])
async def list_properties_by_owner(owner_id: int, db: Session = Depends(get_db)):
    return db.query(Property).filter(Property.owner_id == owner_id).all()



@admin_router.get("/properties/pending", response_model=List[PropertySchema])
async def list_pending_properties(db: Session = Depends(get_db),
                                  current_user: UserProfile = Depends(admin_only)):
    pending = db.query(Property).filter(Property.is_approved == False).all()
    return pending

@admin_router.put("/property/{property_id}/approve")
async def approve_property(property_id: int, db: Session = Depends(get_db),
                           current_user: UserProfile = Depends(admin_only)):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    prop.is_approved = True
    db.commit()
    return {"message": f"Property {prop.id} одобрен"}

@admin_router.put("/property/{property_id}/reject")
async def reject_property(property_id: int, db: Session = Depends(get_db),
                          current_user: UserProfile = Depends(admin_only)):
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    db.delete(prop)
    db.commit()
    return {"message": f"Property {property_id} отклонён и удалён"}