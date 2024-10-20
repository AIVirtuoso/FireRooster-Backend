from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from database import AsyncSessionLocal
from sqlalchemy.orm import Session
from typing import List, Annotated
from datetime import datetime
import requests

from app.Utils.download_audios import download
from app.Utils.remove_space import process_audio
from app.Utils.whisper import stt_archive, add_addresses
from app.Utils.scanners import update_scanners
from app.Models.AlertModel import FilterModel, IdFilterModel, CategoryFilterModel, SelectedCategoryModel, UnlockContactInfoModel
from app.Utils.auth import get_current_user
from app.Utils.alerts import get_geocode_data, get_score_by_location_type, validate_address

from schema import User, Alert
import app.Utils.crud as crud


router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def object_as_dict(obj):
    print("obj", obj)
    print({c.key: getattr(obj, c.key) for c in obj.__table__.columns})
    return {c.key: getattr(obj, c.key) for c in obj.__table__.columns}  

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
    selected_sub_categories = await crud.get_selected_subcategories(db)
    selected_sub_categories = [item.sub_category for item in selected_sub_categories]
    purchased_scanner_list = await crud.get_purchased_scanners_by_user(db, user.id)
    purchased_scanner_id_list = list({purchased_scanner.scanner_id for purchased_scanner in purchased_scanner_list}) # remove duplicate
    alerts, total = await crud.get_alerts_by_filter(db, model, purchased_scanner_id_list, selected_sub_categories)
    result = []
    for alert in alerts:
        scanner = await crud.get_scanner_by_scanner_id(db, alert.scanner_id)
        result.append({"alert": alert, "scanner": scanner})
    return {"alerts": result, "pagination": {"total": total}}

@router.post('/get-alert-by-id')
async def get_alerts_by_filter_router(model: IdFilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    await crud.check_alert_as_visited(db, model.alert_id)
    alert = await crud.get_alerts_by_id(db, model)
    addresses = await crud.get_addresses_by_alert_id(db, alert.id)
    scanner = await crud.get_scanner_by_scanner_id(db, alert.scanner_id)
    audio = await crud.get_audio_by_alert(db, alert)
    return {"alert": alert, "addresses": addresses, "scanner": scanner, "audio": audio}

@router.post('/all-subcategories')
async def get_all_subcategories(model:CategoryFilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    sub_categories = await crud.get_all_subcategories(db, model)
    
    sub_categories_dicts = [object_as_dict(sub) for sub in sub_categories]  

    # Sort by "Category"  
    sorted_list = sorted(sub_categories_dicts, key=lambda x: x.get('category'))
    print("sorted_list: ", sorted_list)
    return sorted_list

@router.post('/update-selected-subcategories')
async def update_selected_subcategories(model: List[SelectedCategoryModel], user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    print('here')
    print(model)
    for category_object in model:
        await crud.update_subcategories(db, category_object)
    return {"status": True, "message": "Successfully updated"}

@router.get('/update-addresses')
async def update_addresses_router(db: Session = Depends(get_db)):
    alerts = await crud.get_all_alerts(db)
    for alert in alerts:
        # if alert.id <= 1340:
        #     continue
        try:
            formatted_addresses = get_geocode_data(alert.address)
            
            # print("alert id: ", alert.id)
            
            # address = await crud.get_address_by_alert_id(db, alert.id)
            # if address:
            #     print("address: ", address)
            #     continue
            
            for result in formatted_addresses:
                formatted_address = result.get('formatted_address')
                type = validate_address(result)
                # location = result.get('geometry', {}).get('location', {})
                # lat = location.get('lat')
                # lng = location.get('lng')
                score = get_score_by_location_type(result.get('geometry').get('location_type'))
                if type == "Commercial Address":
                    print("score: ", score)
                    print("formatted_address-: ", formatted_address)
                    print("type: ", type)
                    
                await crud.insert_validated_address(
                    db,
                    formatted_address,
                    score,
                    alert.id,
                    type,
                    alert.scanner_id,
                    alert.dateTime
                )
            # print("alert.address: ", alert.address)
            # print("formatted_addresses: ", formatted_addresses)
        except Exception as e:
            print(e)

@router.post('/remove-duplicated-alerts')
async def remove_duplicated_alerts(db: Session = Depends(get_db)):
    return
    # message = await crud.remove_duplicated_alerts(db)
    # return {"message": message}

@router.post('/unlock-contact-info')
async def unlock_contact_info_router(model: UnlockContactInfoModel, db: Session = Depends(get_db)):
    url = "http://108.61.203.106:7000/api/v1/verify-address"
    
    try:  
        response = requests.get(url, params={"address_id": model.address_id})  
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
            
        else:
            return False
    
    except requests.exceptions.RequestException as e:  
        print(f"An error occurred: {e}")
        return False
