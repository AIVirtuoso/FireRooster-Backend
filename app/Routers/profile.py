from fastapi import APIRouter, Depends, Form, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Annotated
import secrets
import pandas as pd
from sqlalchemy.orm import Session
import io  # Import the io module to handle byte streams  

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
    await crud.update_user(db, model, user.email)
    return {"status": True, "message": "Set Profile Successfully"}

@router.get('/get-profile')
async def get_profile_router(user: Annotated[User, Depends(get_current_user)],  db: Session = Depends(get_db)):
    variables = await crud.get_variables(db)
    prompt =  variables.prompt if variables != None else ""
    return {"first_name": user.first_name, "last_name": user.last_name, "email": user.email, "phone_number": user.phone_number, "prompt": prompt}

@router.get('/get-prompt')
async def get_profile_router(db: Session = Depends(get_db)):
    variables = await crud.get_variables(db)
    return variables.prompt if variables != None else ""

@router.post('/upload-csv')
async def upload_csv(file:UploadFile = Form(...), state:str = Form(...), county: str = Form(...), db: Session = Depends(get_db)):
    try:
        contents = await file.read()  
        data = pd.read_csv(io.BytesIO(contents))  
        csv_context_json = data.to_json(orient='records')  
        print(csv_context_json)  # or use return if you want to send this as a response  
        response = await crud.insert_csv(db, csv_context_json, state, county)
        if not response:
            return {"message": "invalid state or county", "status": 422}
        else:
            return {"message": "CSV inserted successfully!", "status": 200}
    except:
        return {"message": "Invalid CSV format", "status": 500}