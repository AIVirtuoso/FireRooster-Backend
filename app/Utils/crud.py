from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, Session, aliased
from sqlalchemy import func, delete
from sqlalchemy import and_

from datetime import datetime

from schema import User, Audio, Scanner, UserType, PurchasedScanner, Alert
from database import AsyncSessionLocal
from app.Models.ScannerModel import FilterModel as ScannerFilterModel
from app.Models.AlertModel import FilterModel as AlertFilterModel



async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).filter(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_user_type_by_id(db: AsyncSession, id: int):
    stmt = select(UserType).filter(UserType.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_usertype(db: AsyncSession, user, type):
    user.user_type_id = type
    await db.commit()
    await db.refresh(user)
    return user

async def create_user(db: AsyncSession, **kwargs):
    new_user = User(**kwargs)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_audio_by_filename(db: AsyncSession, filename):
    stmt = select(Audio).filter(Audio.file_name == filename)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def insert_audio(db: AsyncSession, audio, context, scanner_id):
    stmt = select(Audio).filter(Audio.file_name == audio)
    result = await db.execute(stmt)
    data = result.scalar_one_or_none()
    print(data)
    if not data:
        new_audio = Audio(file_name=audio, context=context, scanner_id=scanner_id)
        db.add(new_audio)
        await db.commit()
        await db.refresh(new_audio)
        return new_audio
        
    return new_user

async def insert_alert(db: AsyncSession, purchased_scanner_id, event):
    new_alert = Alert(headline=event['Headline'], description=event['Description'], address=event['Incident_Address'], scanner_id=purchased_scanner_id)
    db.add(new_alert)
    await db.commit()
    await db.refresh(new_alert)
    return new_alert

async def get_total_alerts(db: AsyncSession) -> int:
    # Create a select statement to count the total number of rows
    stmt = select(func.count(Alert.id))
    result = await db.execute(stmt)
    total_alerts = result.scalar_one()
    
    return total_alerts
        

async def get_audios_by_scanner_id(db: AsyncSession, purchased_scanner_id):
    stmt = select(Audio).filter(Audio.scanner_id == purchased_scanner_id)
    result = await db.execute(stmt)
    audios = result.scalars().all()
    return audios

async def insert_scanner(db: AsyncSession, stid, st_name, ctid, ct_name, scanner):
    stmt = select(Scanner).filter(Scanner.feed_id == scanner['scanner_id'])
    result = await db.execute(stmt)
    data = result.scalar_one_or_none()
    if not data:
        new_scanner = Scanner(state_id=stid, state_name=st_name, county_id=ctid, county_name=ct_name, scanner_id=scanner['scanner_id'], scanner_title=scanner['scanner_title'], listeners_count=scanner['listeners_count'])
        db.add(new_scanner)
        await db.commit()
        await db.refresh(new_scanner)
        # print("new_scanner: ", new_scanner)
        return new_scanner
    return data

async def get_total_scanners(db: AsyncSession) -> int:
    # Create a select statement to count the total number of rows
    stmt = select(func.count(Scanner.id))
    result = await db.execute(stmt)
    total_scanners = result.scalar_one()
    
    return total_scanners

async def get_scanners_by_filter(db: AsyncSession, filter_model: ScannerFilterModel):
    query = select(Scanner)
    # Dynamically apply filters
    if filter_model.state_id:
        query = query.where(Scanner.state_id.in_(filter_model.state_id))
    
    if filter_model.county_id:
        query = query.where(Scanner.county_id.in_(filter_model.county_id))
    
    start = (filter_model.page - 1) * filter_model.limit
    
    query = query.offset(start).limit(filter_model.limit)

    result = await db.execute(query)
    scanners = result.scalars().all()
    return scanners

async def get_scanner_by_scanner_id(db: AsyncSession, scanner_id):
    stmt = select(Scanner).filter(Scanner.scanner_id == scanner_id)
    result = await db.execute(stmt)
    # print("scanner result: ",result)
    return result.scalar_one_or_none()

async def get_state_and_county_list(db: AsyncSession):
    # A subquery to fetch distinct state names and ids
    state_alias = aliased(Scanner)
    state_stmt = (
        select(state_alias.state_name, state_alias.state_id)
        .distinct()
    )
    state_results = await db.execute(state_stmt)
    distinct_states = state_results.all()

    final_result = []

    for state in distinct_states:
        state_name, state_id = state
        
        # Fetch counties related to the current state
        county_stmt = (
            select(Scanner.county_name.label('county_name'), Scanner.county_id.label('county_id'))
            .where(Scanner.state_id == state_id)
        )
        county_results = await db.execute(county_stmt)
        counties = county_results.all()

        seen_county_ids = set()
        county_list = []

        for county in counties:
            county_id = county.county_id
            if county_id not in seen_county_ids:
                seen_county_ids.add(county_id)
                county_list.append({'county_name': county.county_name, 'county_id': county_id})
        
        state_dict = {
            'state_name': state_name,
            'state_id': state_id,
            'county_list': county_list
        }
        
        final_result.append(state_dict)
    
    return final_result


async def get_alerts_by_filter(db: AsyncSession, filter_model: AlertFilterModel):
    query = select(Alert)
    # Dynamically apply filters
    if filter_model.scanner_id:
        query = query.filter(Alert.scanner_id == filter_model.scanner_id)
    
    start = (filter_model.page - 1) * filter_model.limit
    
    query = query.offset(start).limit(filter_model.limit)

    result = await db.execute(query)
    scanners = result.scalars().all()
    return scanners

async def insert_purchased_scanners(db: AsyncSession, user_id, scanner_id):
    new_purchased_scanner = PurchasedScanner(user_id=user_id, scanner_id=scanner_id)
    print("new_purchased_scanner: ", new_purchased_scanner)
    db.add(new_purchased_scanner)
    await db.commit()
    await db.refresh(new_purchased_scanner)
    return new_purchased_scanner

async def delete_purchased_scanners_by_user_id(db: AsyncSession, user_id: int):
    # Define the delete statement
    stmt = delete(PurchasedScanner).where(PurchasedScanner.user_id == user_id)
    await db.execute(stmt)
    await db.commit()
    
async def get_purchased_scanners_by_user(db: AsyncSession, user_id):
    stmt = select(PurchasedScanner).filter(PurchasedScanner.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_all_purchased_scanners(db: AsyncSession):
    stmt = select(PurchasedScanner)
    result = await db.execute(stmt)
    return result.scalars().all()