from functools import lru_cache
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, items
from userApp.models import User, Item
from . import metadata, config, crud, database, schemas, dependencies
import time
from typing import List

database.db.connect()
database.db.create_tables([User, Item])
database.db.close()

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