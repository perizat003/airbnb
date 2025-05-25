from fastapi import FastAPI
from airbnb_app.api import (property, auth, review,
                            images, booking, message,
                            userprofile, property_pagination)
import uvicorn
from airbnb_app.admin import admin


airbnb_app = FastAPI(title='OnlineStore')
airbnb_app.include_router(property.property_router)
airbnb_app.include_router(auth.auth_router)
airbnb_app.include_router(review.review_router)
airbnb_app.include_router(images.image_router)
airbnb_app.include_router(booking.booking_router)
airbnb_app.include_router(message.message_router)
airbnb_app.include_router(userprofile.user_router)
airbnb_app.include_router(admin.admin_router)
airbnb_app.include_router(property_pagination.pagination_router)

if __name__ == '__main__':
    uvicorn.run(airbnb_app, host='127.0.0.1', port=8000)

