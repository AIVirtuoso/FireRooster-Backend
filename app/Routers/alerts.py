from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from database import AsyncSessionLocal
from sqlalchemy.orm import Session
from typing import List, Annotated

from app.Utils.download_audios import download
from app.Utils.remove_space import process_audio
from app.Utils.whisper import stt_archive
from app.Utils.scanners import update_scanners
from app.Models.AlertModel import FilterModel, IdFilterModel
from app.Utils.auth import get_current_user
from schema import User
import app.Utils.crud as crud
router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        

@router.get('/update-alerts')
async def update_alerts_router(db: Session = Depends(get_db)):
    purchased_scanner_list = await crud.get_all_purchased_scanners(db)
    print("purchased_scanner_list: ", purchased_scanner_list)
    purchased_scanner_id_list = list({purchased_scanner.scanner_id for purchased_scanner in purchased_scanner_list}) # remove duplicate
    
    for purchased_scanner_id in purchased_scanner_id_list:
        if purchased_scanner_id != 32270:
            continue
        await stt_archive(db, purchased_scanner_id)

@router.post('/get-alerts-by-filter')
async def get_alerts_by_filter_router(model: FilterModel, db: Session = Depends(get_db)):#user: Annotated[User, Depends(get_current_user)], 
    data, total = await crud.get_alerts_by_filter(db, model)
    for item in data:
        print(item.address)
    return {"data": data, "pagination": {"total": total}}

@router.post('/get-alert-by-id')
async def get_alerts_by_filter_router(model: IdFilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    data = await crud.get_alerts_by_id(db, model)
    return data