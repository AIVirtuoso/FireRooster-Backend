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
        archive_list = await download(purchased_scanner_id)
        # archive_list = [{'id': '27296-1719290905', 'start_time': '11:48 PM', 'end_time': '12:18 AM', 'filename': 'audios/27296-1719290905_p.mp3'}, {'id': '27296-1719289115', 'start_time': '11:18 PM', 'end_time': '11:48 PM', 'filename': 'audios/27296-1719289115_p.mp3'}, {'id': '27296-1719287325', 'start_time': '10:48 PM', 'end_time': '11:18 PM', 'filename': 'audios/27296-1719287325_p.mp3'}, {'id': '27296-1719285535', 'start_time': '10:18 PM', 'end_time': '10:48 PM', 'filename': 'audios/27296-1719285535_p.mp3'}, {'id': '27296-1719283745', 'start_time': '09:49 PM', 'end_time': '10:19 PM', 'filename': 'audios/27296-1719283745_p.mp3'}, {'id': '27296-1719281955', 'start_time': '09:19 PM', 'end_time': '09:49 PM', 'filename': 'audios/27296-1719281955_p.mp3'}, {'id': '27296-1719280165', 'start_time': '08:49 PM', 'end_time': '09:19 PM', 'filename': 'audios/27296-1719280165_p.mp3'}, {'id': '27296-1719278375', 'start_time': '08:19 PM', 'end_time': '08:49 PM', 'filename': 'audios/27296-1719278375_p.mp3'}, {'id': '27296-1719276585', 'start_time': '07:49 PM', 'end_time': '08:19 PM', 'filename': 'audios/27296-1719276585_p.mp3'}, {'id': '27296-1719274795', 'start_time': '07:19 PM', 'end_time': '07:49 PM', 'filename': 'audios/27296-1719274795_p.mp3'}, {'id': '27296-1719273005', 'start_time': '06:50 PM', 'end_time': '07:20 PM', 'filename': 'audios/27296-1719273005_p.mp3'}, {'id': '27296-1719271215', 'start_time': '06:20 PM', 'end_time': '06:50 PM', 'filename': 'audios/27296-1719271215_p.mp3'}, {'id': '27296-1719269425', 'start_time': '05:50 PM', 'end_time': '06:20 PM', 'filename': 'audios/27296-1719269425_p.mp3'}, {'id': '27296-1719267635', 'start_time': '05:20 PM', 'end_time': '05:50 PM', 'filename': 'audios/27296-1719267635_p.mp3'}, {'id': '27296-1719265845', 'start_time': '04:50 PM', 'end_time': '05:20 PM', 'filename': 'audios/27296-1719265845_p.mp3'}, {'id': '27296-1719264055', 'start_time': '04:20 PM', 'end_time': '04:43 PM', 'filename': 'audios/27296-1719264055_p.mp3'}, {'id': '27296-1719262265', 'start_time': '03:51 PM', 'end_time': '04:21 PM', 'filename': 'audios/27296-1719262265_p.mp3'}, {'id': '27296-1719260475', 'start_time': '03:21 PM', 'end_time': '03:51 PM', 'filename': 'audios/27296-1719260475_p.mp3'}, {'id': '27296-1719258685', 'start_time': '02:51 PM', 'end_time': '03:21 PM', 'filename': 'audios/27296-1719258685_p.mp3'}, {'id': '27296-1719256895', 'start_time': '02:21 PM', 'end_time': '02:51 PM', 'filename': 'audios/27296-1719256895_p.mp3'}, {'id': '27296-1719255105', 'start_time': '01:51 PM', 'end_time': '02:21 PM', 'filename': 'audios/27296-1719255105_p.mp3'}, {'id': '27296-1719253315', 'start_time': '01:21 PM', 'end_time': '01:51 PM', 'filename': 'audios/27296-1719253315_p.mp3'}, {'id': '27296-1719251525', 'start_time': '12:52 PM', 'end_time': '01:22 PM', 'filename': 'audios/27296-1719251525_p.mp3'}, {'id': '27296-1719249735', 'start_time': '12:22 PM', 'end_time': '12:52 PM', 'filename': 'audios/27296-1719249735_p.mp3'}, {'id': '27296-1719247945', 'start_time': '11:52 AM', 'end_time': '12:22 PM', 'filename': 'audios/27296-1719247945_p.mp3'}, {'id': '27296-1719246155', 'start_time': '11:22 AM', 'end_time': '11:52 AM', 'filename': 'audios/27296-1719246155_p.mp3'}, {'id': '27296-1719244365', 'start_time': '10:52 AM', 'end_time': '11:22 AM', 'filename': 'audios/27296-1719244365_p.mp3'}, {'id': '27296-1719242575', 'start_time': '10:22 AM', 'end_time': '10:52 AM', 'filename': 'audios/27296-1719242575_p.mp3'}, {'id': '27296-1719240785', 'start_time': '09:53 AM', 'end_time': '10:23 AM', 'filename': 'audios/27296-1719240785_p.mp3'}, {'id': '27296-1719238995', 'start_time': '09:23 AM', 'end_time': '09:53 AM', 'filename': 'audios/27296-1719238995_p.mp3'}, {'id': '27296-1719237205', 'start_time': '08:53 AM', 'end_time': '09:23 AM', 'filename': 'audios/27296-1719237205_p.mp3'}, {'id': '27296-1719235415', 'start_time': '08:23 AM', 'end_time': '08:53 AM', 'filename': 'audios/27296-1719235415_p.mp3'}, {'id': '27296-1719233625', 'start_time': '07:53 AM', 'end_time': '08:23 AM', 'filename': 'audios/27296-1719233625_p.mp3'}, {'id': '27296-1719231834', 'start_time': '07:23 AM', 'end_time': '07:53 AM', 'filename': 'audios/27296-1719231834_p.mp3'}, {'id': '27296-1719230044', 'start_time': '06:54 AM', 'end_time': '07:24 AM', 'filename': 'audios/27296-1719230044_p.mp3'}, {'id': '27296-1719228255', 'start_time': '06:24 AM', 'end_time': '06:54 AM', 'filename': 'audios/27296-1719228255_p.mp3'}, {'id': '27296-1719226464', 'start_time': '05:54 AM', 'end_time': '06:24 AM', 'filename': 'audios/27296-1719226464_p.mp3'}, {'id': '27296-1719224674', 'start_time': '05:24 AM', 'end_time': '05:54 AM', 'filename': 'audios/27296-1719224674_p.mp3'}, {'id': '27296-1719222884', 'start_time': '04:54 AM', 'end_time': '05:24 AM', 'filename': 'audios/27296-1719222884_p.mp3'}, {'id': '27296-1719221094', 'start_time': '04:24 AM', 'end_time': '04:54 AM', 'filename': 'audios/27296-1719221094_p.mp3'}, {'id': '27296-1719219304', 'start_time': '03:55 AM', 'end_time': '04:25 AM', 'filename': 'audios/27296-1719219304_p.mp3'}, {'id': '27296-1719217514', 'start_time': '03:25 AM', 'end_time': '03:55 AM', 'filename': 'audios/27296-1719217514_p.mp3'}, {'id': '27296-1719215724', 'start_time': '02:55 AM', 'end_time': '03:25 AM', 'filename': 'audios/27296-1719215724_p.mp3'}, {'id': '27296-1719213934', 'start_time': '02:25 AM', 'end_time': '02:55 AM', 'filename': 'audios/27296-1719213934_p.mp3'}, {'id': '27296-1719212144', 'start_time': '01:55 AM', 'end_time': '02:25 AM', 'filename': 'audios/27296-1719212144_p.mp3'}, {'id': '27296-1719210354', 'start_time': '01:25 AM', 'end_time': '01:55 AM', 'filename': 'audios/27296-1719210354_p.mp3'}, {'id': '27296-1719208564', 'start_time': '12:56 AM', 'end_time': '01:26 AM', 'filename': 'audios/27296-1719208564_p.mp3'}, {'id': '27296-1719206774', 'start_time': '12:26 AM', 'end_time': '12:56 AM', 'filename': 'audios/27296-1719206774_p.mp3'}]
        print("purchased_scanner_id: ", purchased_scanner_id)
        print(archive_list)
        await stt_archive(db, purchased_scanner_id, archive_list)

@router.post('/get-alerts-by-filter')
async def get_alerts_by_filter_router(model: FilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    data, total = await crud.get_alerts_by_filter(db, model)
    return {"data": data, "pagination": {"total": total}}

@router.post('/get-alert-by-id')
async def get_alerts_by_filter_router(model: IdFilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    data = await crud.get_alerts_by_id(db, model)
    return data