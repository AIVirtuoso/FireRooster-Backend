from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from typing import List, Annotated
import secrets
from sqlalchemy.orm import Session
 
from database import AsyncSessionLocal

from app.Utils.auth import get_current_user
from app.Models.ProfileModel import SetProfileModel
import app.Utils.crud as crud
from schema import Variables, User

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post('/set-profile')
async def set_profile_router(model: SetProfileModel, user: Annotated[User, Depends(get_current_user)],  db: Session = Depends(get_db)):
    await crud.set_variables(db, model.prompt)
    return {"status": True, "message": "Set Profile Successfully"}

@router.get('/get-profile')
async def get_profile_router(user: Annotated[User, Depends(get_current_user)],  db: Session = Depends(get_db)):
    variables = await crud.get_variables(db)
    return {"first_name": user.first_name, "last_name": user.last_name, "email": user.email, "prompt": variables.prompt if variables != None else ""}

@router.get('/get-prompt')
async def get_profile_router(db: Session = Depends(get_db)):
    variables = await crud.get_variables(db)
    return variables.prompt if variables != None else ""