from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from database import AsyncSessionLocal
from sqlalchemy.orm import Session
from typing import List, Annotated

from app.Utils.download_audios import download
from app.Utils.remove_space import process_audio
from app.Utils.whisper import stt_archive
from app.Utils.scanners import update_scanners
from app.Utils.auth import get_current_user
from app.Models.ScannerModel import FilterModel, PurchaseScannerModel
from schema import User
import app.Utils.crud as crud


router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        

@router.get('/update-scanners')
async def get_scanners_router(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    scanner_lists = await update_scanners(db, 1)
    return scanner_lists

@router.post('/get-scanners-by-filter')
async def get_scanners_by_filter(model: FilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    data = await crud.get_scanners_by_filter(db, model)
    total = await crud.get_total_scanners(db)
    return {"data": data, "pagination": {"total": total}}

@router.get('/get-state-and-county-list')
async def get_state_and_county_list_router(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    data = await crud.get_state_and_county_list(db)
    return data

@router.get('/purchase-scanners')
async def purchase_scanners_router(model: PurchaseScannerModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    scanner_id_list = model.scanner_id_list
    print(scanner_id_list)
    
    await crud.delete_purchased_scanners_by_user_id(db, user.id)
    
    for scanner_id in scanner_id_list:
        try:
            await crud.insert_purchased_scanners(db, user.id, scanner_id)
        except Exception as e:
            print(e)