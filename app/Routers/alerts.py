from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from database import AsyncSessionLocal
from sqlalchemy.orm import Session
from typing import List, Annotated

from app.Utils.download_audios import download
from app.Utils.remove_space import process_audio
from app.Utils.whisper import stt_archive, add_addresses
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
        await stt_archive(db, purchased_scanner_id)
    
    
    alerts = await crud.get_all_alerts(db)
    for alert in alerts:
        await add_addresses(db, alert)

@router.post('/get-alerts-by-filter')
async def get_alerts_by_filter_router(model: FilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):#user: Annotated[User, Depends(get_current_user)], 
    purchased_scanner_list = await crud.get_purchased_scanners_by_user(db, user.id)
    purchased_scanner_id_list = list({purchased_scanner.scanner_id for purchased_scanner in purchased_scanner_list}) # remove duplicate

    alerts, total = await crud.get_alerts_by_filter(db, model, purchased_scanner_id_list)
    result = []
    for alert in alerts:
        addresses = await crud.get_addresses_by_alert_id(db, alert.id)
        result.append({"alert": alert, "addresses": addresses})
    return {"alerts": result, "pagination": {"total": total}}

@router.post('/get-alert-by-id')
async def get_alerts_by_filter_router(model: IdFilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    alert = await crud.get_alerts_by_id(db, model)
    addresses = await crud.get_addresses_by_alert_id(db, alert.id)
    return {"alert": alert, "addresses": addresses}