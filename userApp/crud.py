from operator import is_
from fastapi import status
from . import models, schemas, config, dependencies
from fastapi import HTTPException, Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Union
import string, random
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def username_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_user(user_id: int):
    return models.User.filter(models.User.id == user_id).first()

def get_user_by_email(email: str):
    return models.User.filter(models.User.email == email).first()

def get_users(skip: int = 0, limit: int = 100, all_users=False):
    if all_users :
        print(list(models.User.select()))
        return list(models.User.select())
    else :
        return list(models.User.select().offset(skip).limit(limit))



def get_items(skip: int = 0, limit: int = 100):
    return list(models.Item.select().offset(skip).limit(limit))

def create_user_item(item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db_item.save()
    return db_item

#//////////////////////////////////////////////////////////////////////////////////////////////

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def is_user_exist(db, username: str):
    user = {}
    for user_id in db: 
        user_id = models.User.filter(models.User.username == username).first()
        if user_id != None :
            user["id"] = user_id.id
            user["username"] = user_id.username
            user["email"] = user_id.email
            user["hashed_password"] = user_id.hashed_password
            user["is_active"] = user_id.is_active
            return schemas.UserInDB(**user)
    # if username in db:
    #     user_dict = db[username]
    #     return schemas.UserInDB(**user_dict)

def authenticate_user(username: str, password: str, dependencies=[Depends(dependencies.get_db)]):
    user = is_user_exist(list(models.User), username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta , None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.settings.secret_key, algorithm=config.settings.algorithm)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.settings.secret_key, algorithms=[config.settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = is_user_exist(list(models.User), username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



def create_user(user: schemas.UserCreate):
    fake_hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email,username =username_generator(),  hashed_password=fake_hashed_password)
    db_user.save()
    return db_user