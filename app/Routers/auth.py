from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from typing import List, Annotated
import secrets
from sqlalchemy.orm import Session
from app.Utils.auth import get_current_user

from database import AsyncSessionLocal
from app.Models.AuthModel import SignUpModel, SignInModel
import app.Utils.auth as Auth
import app.Utils.crud as crud
from schema import User

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post('/register/')
async def register(model: SignUpModel, db: Session = Depends(get_db)):
    if model.password != model.password2:
        return JSONResponse(content={"success": "Both password must match"}, status_code=400)
    hashed_password = Auth.get_password_hash(model.password)
    # print(password_in_db)
    forgot_password_token = secrets.token_urlsafe()

    user = await crud.get_user_by_email(db, model.email)
    # print("signup user: ", user)
    
    if not user:
        # await send_approve_email(email, db)
        model.forgot_password_token = forgot_password_token
        await crud.create_user(db, email=model.email, hashed_password=hashed_password, first_name=model.first_name, last_name=model.last_name, forgot_password_token=forgot_password_token)
        return JSONResponse(content={"success": True}, status_code=200)
    else:
        return JSONResponse(content={"message": "That email already exists"}, status_code=400)

@router.post("/token")
async def signin_for_access_token(model: SignInModel, db: Session = Depends(get_db)):
    print("email: ", model.email)
    user = await Auth.authenticate_user(db, model.email, model.password)  # This function needs to be updated to use db
    if not user:
        return JSONResponse(content={"message": "Email or Password are incorrect!"}, status_code=401)
    print("sigin user: ", user.email)
    # if user.approved == 0:
    #     return JSONResponse(content={"message": "This email is not approved!"}, status_code=400)
    access_token = Auth.create_access_token(data={"sub": user.email})  # Assuming 'user' is an object
    user_to_return = {'email': user.email, 'hashed_password': user.hashed_password, 'first_name': user.first_name, 'last_name': user.last_name, "tier": user.user_type_id}
    return {"access_token": access_token, "token_type": "bearer", "user": user_to_return}

@router.get('/user')
async def get_user(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    usertype = await crud.get_user_type_by_id(db, user.user_type_id)
    purchased_scanners = []
    purchased_scanner_list = await crud.get_purchased_scanners_by_user(db, user.id)
    
    for purchased_scanner in purchased_scanner_list:
        scanner = await crud.get_scanner_by_scanner_id(db, purchased_scanner.scanner_id)
        purchased_scanners.append(scanner)
    
    return {"user": user, "usertype": usertype, "purchased_scanners": purchased_scanners}