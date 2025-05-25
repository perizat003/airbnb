from fastapi import APIRouter, Depends, Request
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
from airbnb_app.db.models import UserProfile
from airbnb_app.db.database import SessionLocal
from sqlalchemy.orm import Session

oauth_router = APIRouter(prefix="/oauth", tags=["OAuth"])

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

oauth.register(
    name='github',
    client_id=config('GITHUB_CLIENT_ID'),
    client_secret=config('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@oauth_router.get("/login/{provider}")
async def login(provider: str, request: Request):
    redirect_uri = request.url_for("auth_callback", provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

@oauth_router.get("/auth/{provider}")
async def auth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    token = await oauth.create_client(provider).authorize_access_token(request)
    user_info = await oauth.create_client(provider).parse_id_token(request, token) if provider == "google" else \
                await oauth.github.get('user', token=token)

    email = user_info.get("email") if provider == "google" else user_info.json().get("email")

    if not email:
        raise Exception("Email not found")

    user = db.query(UserProfile).filter(UserProfile.email == email).first()
    if not user:
        user = UserProfile(username=email.split('@')[0], email=email, role="guest", is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)

    return {"access_token": "JWT для пользователя", "token_type": "bearer"}


#pip install authlib