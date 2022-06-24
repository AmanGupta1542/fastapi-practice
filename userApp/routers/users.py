from fastapi import APIRouter, Depends, HTTPException
from .. import crud, schemas, dependencies
from typing import List
router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(dependencies.get_db)],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.User, dependencies=[Depends(dependencies.get_db)])
def create_user(user: schemas.UserCreate):
    db_user = crud.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(user=user)


@router.get("/", response_model=List[schemas.User], dependencies=[Depends(dependencies.get_db)])
def read_users(skip: int = 0, limit: int = 100):
    users = crud.get_users(skip=skip, limit=limit)
    return users


@router.get(
    "/{user_id}", response_model=schemas.User, dependencies=[Depends(dependencies.get_db), Depends(crud.get_current_active_user)]
)
def read_user(user_id: int):
    db_user = crud.get_user(user_id=user_id)
    print('ok')
    print(db_user.token)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post(
    "/{user_id}/items/",
    response_model=schemas.Item,
    dependencies=[Depends(dependencies.get_db)],
)
def create_item_for_user(user_id: int, item: schemas.ItemCreate):
    return crud.create_user_item(item=item, user_id=user_id)