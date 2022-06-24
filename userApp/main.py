from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, items
from userApp.models import User as UserModel, Item, Token as TokenModel
from . import metadata, config, crud, database, schemas, dependencies
import time
from typing import List, Union
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(config.settings.access_token_expire_minutes)

database.db.connect()
database.db.create_tables([UserModel, Item, TokenModel])
database.db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    # getting title from .env file
    title = config.settings.app_name,
    description = metadata.description,
    version = metadata.version,
    terms_of_service = metadata.terms_of_service,
    contact = metadata.contact,
    license_info = metadata.license_info,
    openapi_tags= metadata.tags_metadata,
    docs_url = metadata.docs_url, 
    redoc_url = metadata.redoc_url,
    openapi_url = metadata.openapi_url
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = metadata.origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(users.router)
# app.include_router(items.router)
# we also can configure like 
app.include_router(
    items.router,
    prefix="/items",
    tags=["Items"],
    dependencies=[Depends(dependencies.get_db)],
    responses={404: {"description": "Not found"}},
)

@lru_cache()
def get_settings():
    return config.Settings()

@app.get('/')
def root():
    return {'message': 'ok'} 

# @app.get("/info")
# async def info(settings: config.Settings= Depends(get_settings)):
#     return {
#         "app_name": settings.app_name,
#         "admin_email": settings.admin_email,
#         "items_per_user": settings.items_per_user,
#     }


# @app.get(
#     "/slowusers/", response_model=List[schemas.User], dependencies=[Depends(get_db)]
# )
# def read_slow_users(skip: int = 0, limit: int = 100):
#     global sleep_time
#     sleep_time = max(0, sleep_time - 1)
#     time.sleep(sleep_time)  # Fake long processing request
#     users = crud.get_users(skip=skip, limit=limit)
#     return users

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     return pwd_context.hash(password)

# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)

# def authenticate_user(fake_db, username: str, password: str):
#     user = get_user(fake_db, username)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# def create_access_token(data: dict, expires_delta: Union[timedelta , None] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = schemas.TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(fake_users_db, username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user


# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/abc/me/", response_model=User)
async def read_users_me(current_user: User = Depends(crud.get_current_active_user)):
    return current_user


@app.get("/abc/me/items/")
async def read_own_items(current_user: User = Depends(crud.get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]