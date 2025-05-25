from airbnb_app.db.database import SessionLocal
from airbnb_app.db.models import PropertyImages
from airbnb_app.db.schema import PropertyImagesSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, APIRouter
from typing import List

image_router = APIRouter(prefix='/images', tags=['Property Images'])


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@image_router.post('/create/', response_model=PropertyImagesSchema)
async def create_image(image: PropertyImagesSchema, db: Session = Depends(get_db)):
    image_db = PropertyImages(**image.dict())
    db.add(image_db)
    db.commit()
    db.refresh(image_db)
    return image_db


@image_router.get('/', response_model=List[PropertyImagesSchema])
async def list_images(db: Session = Depends(get_db)):
    return db.query(PropertyImages).all()


@image_router.get('/{image_id}/', response_model=PropertyImagesSchema)
async def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(PropertyImages).filter(PropertyImages.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image не найден")
    return image


@image_router.put('/{image_id}/', response_model=PropertyImagesSchema)
async def update_image(image_id: int, image: PropertyImagesSchema, db: Session = Depends(get_db)):
    image_db = db.query(PropertyImages).filter(PropertyImages.id == image_id).first()
    if image_db is None:
        raise HTTPException(status_code=404, detail='Image не найден')

    for image_key, image_value in image.dict().items():
        setattr(image_db, image_key, image_value)

    db.commit()
    db.refresh(image_db)
    return image_db


@image_router.delete('/{image_id}/')
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    image_db = db.query(PropertyImages).filter(PropertyImages.id == image_id).first()
    if image_db is None:
        raise HTTPException(status_code=404, detail='Image не найден')

    db.delete(image_db)
    db.commit()
    return {'message': 'Image успешно удален'}
