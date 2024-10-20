from fastapi import APIRouter, Depends, Form
from fastapi.responses import JSONResponse
from database import AsyncSessionLocal
from sqlalchemy.orm import Session
from typing import List, Annotated
from collections import defaultdict

from app.Utils.download_audios import download
from app.Utils.remove_space import process_audio
from app.Utils.whisper import stt_archive
from app.Utils.scanners import update_scanners, validate_tier_limit
from app.Utils.auth import get_current_user
from app.Models.ScannerModel import FilterModel, PurchaseScannerModel, DeleteScannerModel, ToggleScraperModel
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
    data, total = await crud.get_scanners_by_filter(db, model)
    return {"data": data, "pagination": {"total": total}}

@router.get('/get-state-and-county-list')
async def get_state_and_county_list_router(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    data = await crud.get_state_and_county_list(db)
    return data

@router.get('/get-selected-scanner-list')
async def get_state_and_county_list_router(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    purchased_scanner_list = await crud.get_purchased_scanners_by_user(db, user.id)
    my_scanner_list = []
    for purchased_scanner in purchased_scanner_list:
        print("purchased_scanner.scanner_id: ", purchased_scanner.scanner_id)
        scanner = await crud.get_scanner_by_scanner_id(db, purchased_scanner.scanner_id)
        my_scanner_list.append(scanner)
    return my_scanner_list
    

@router.post('/get-my-scanners')
async def get_my_scanner_router(model: FilterModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    purchased_scanner_list = await crud.get_purchased_scanners_by_user(db, user.id)
    
    my_scanner_list = []
    for purchased_scanner in purchased_scanner_list:
        print("purchased_scanner.scanner_id: ", purchased_scanner.scanner_id)
        scanner = await crud.get_scanner_by_scanner_id(db, purchased_scanner.scanner_id)
        
        if model.state_id and (scanner.state_id not in model.state_id):
            continue
        
        if model.county_id and (scanner.county_id not in model.county_id):
            continue
        
        if model.search and (model.search.lower() not in scanner.scanner_title.lower()):
            continue
            
        print(model.county_id, scanner.county_id)
        my_scanner_list.append(scanner)
        
    state_dict = defaultdict(lambda: {
        "state_name": "",
        "state_id": 0,
        "county_list": []
    })

    # Process each scanner object
    for scanner in my_scanner_list:
        state_id = scanner.state_id
        county_id = scanner.county_id
        county_name = scanner.county_name
        state_name = scanner.state_name
        
        # Set state information
        state_dict[state_id]["state_name"] = state_name
        state_dict[state_id]["state_id"] = state_id
        
        # Add county to the state's list if it's not already added
        if not any(county["county_id"] == county_id for county in state_dict[state_id]["county_list"]):
            state_dict[state_id]["county_list"].append({
                "county_name": county_name,
                "county_id": county_id
            })

    # Transform dictionary to the desired list format
    result_list = list(state_dict.values())
    
    total = len(my_scanner_list)
    
    start = (model.page - 1) * model.limit
    my_scanner_list = my_scanner_list[start: start + model.limit]
    return {"data": my_scanner_list, "states": result_list, "pagination": {"total": total}}
    
@router.post('/purchase-scanners')
async def purchase_scanners_router(model: PurchaseScannerModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    scanner_id_list = model.scanner_id_list
    if not scanner_id_list:
        return True
    
    print("scanner_id_list: ", scanner_id_list)
    
    # scanner_list = await crud.get_scanners_by_scanner_id_list(db, scanner_id_list)
    
    await crud.delete_purchased_scanners_by_user_id(db, user.id)
    usertype = await crud.get_user_type_by_id(db, user.user_type_id)
    
    # print(scanner_list)
    
    # if not usertype:
    #     return {"status": "Please subscribe your package!"}
    
    # if not validate_tier_limit(usertype, scanner_list):
    #     return {"status": "Exceed package limit!"}
    
    for scanner_id in scanner_id_list:
        # scanner_id = scanner.scanner_id
        try:
            await crud.insert_purchased_scanners(db, user.id, scanner_id)
        except Exception as e:
            print(e)
    return {"status": True, "message": "Successfully purchased"}


@router.post('/delete-purchased-scanner')
async def delete_purchased_scanner(model: DeleteScannerModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    await crud.delete_purchased_scanners_by_scanner_id(db, model.scanner_id, user.id)
    return {"status": True, "message": "Successfully purchased"} 

@router.post('/set-scraper-status')
async def toggle_scraper_router(model: ToggleScraperModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    await crud.update_scraper_status(db, model.scraper_status)
    return {"status": True, "message": "Turned on successfully" if model.scraper_status else "Turned off successfully"}

@router.post('/get-scraper-status')
async def toggle_scraper_router(model: ToggleScraperModel, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    variables = await crud.get_variables(db)
    scraper_status = variables.scraper_status if variables != None else ""
    return {"scraper_status": scraper_status}
