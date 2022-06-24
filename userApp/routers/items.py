from fastapi import APIRouter, Depends
from .. import crud, schemas, dependencies
from typing import List

# router = APIRouter(
#     prefix="/items",
#     tags=["Items"],
#     dependencies=[Depends(dependencies.get_db)],
#     responses={404: {"description": "Not found"}},
# )
# If you configure these things in main.py then here use only
router = APIRouter()

@router.get("/", response_model=List[schemas.Item], dependencies=[Depends(dependencies.get_db)])
def read_items(skip: int = 0, limit: int = 100):
    items = crud.get_items(skip=skip, limit=limit)
    return items