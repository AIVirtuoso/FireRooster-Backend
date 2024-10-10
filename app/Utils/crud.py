from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, Session, aliased
from sqlalchemy import func, delete
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import desc  

from datetime import datetime, timedelta

from schema import User, Audio, Scanner, UserType, PurchasedScanner, Alert, Address, Variables, Category, FireDistrict
from database import AsyncSessionLocal
from app.Models.ScannerModel import FilterModel as ScannerFilterModel
from app.Models.AlertModel import IdFilterModel
from app.Models.AlertModel import FilterModel as AlertFilterModel

import urllib.parse
import spacy

nlp = spacy.load("en_core_web_md")

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

async def update_user(db: AsyncSession, model, email):
    stmt = select(User).filter(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    user.email = model.email
    user.first_name = model.first_name
    user.last_name = model.last_name
    user.phone_number = model.phone_number
    await db.commit()
    await db.refresh(user)
    return user

async def get_audio_by_filename(db: AsyncSession, filename):
    stmt = select(Audio).filter(Audio.file_name == filename)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_audio_by_scanner_id(db: AsyncSession, scanner_id):
    stmt = select(Audio).filter(Audio.scanner_id == scanner_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_audio_by_alert(db: AsyncSession, alert):
    query = select(Audio).filter(Audio.dateTime == alert.dateTime)
    query = query.filter(Audio.scanner_id == alert.scanner_id)
    query = query.limit(1)
    result = await db.execute(query)
    print("result: ", result)
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
        
    return data

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

async def check_alert_as_visited(db: AsyncSession, alert_id):
    query = select(Alert).filter(Alert.id == alert_id)
    result = await db.execute(query)
    result = result.scalar_one_or_none()
    updated_alert = result
    updated_alert.is_visited = 1
    print("updated_variables", updated_alert.id, updated_alert.is_visited)
    await db.commit()
    await db.refresh(updated_alert)
        

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

async def get_scanners_by_scanner_id_list(db: AsyncSession, scanner_id_list):
    query = select(Scanner).where(Scanner.scanner_id.in_(scanner_id_list))
    result = await db.execute(query)
    scanners = result.scalars().all()
    return scanners

async def get_scanners_by_filter(db: AsyncSession, filter_model: ScannerFilterModel):
    query = select(Scanner)
    # Dynamically apply filters
    if filter_model.search:
        query = query.where(Scanner.scanner_title.ilike(f'%{filter_model.search}%'))
    
    if filter_model.state_id:
        query = query.where(Scanner.state_id.in_(filter_model.state_id))
    
    if filter_model.county_id:
        query = query.where(Scanner.county_id.in_(filter_model.county_id))
    
    result = await db.execute(query)
    scanners = result.scalars().all()
    
    total = len(scanners)
    
    start = (filter_model.page - 1) * filter_model.limit
    scanners = scanners[start: start + filter_model.limit]

    return scanners, total

async def get_scanner_by_scanner_id(db: AsyncSession, scanner_id):
    stmt = select(Scanner).filter(Scanner.scanner_id == scanner_id)
    result = await db.execute(stmt)
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


async def get_alerts_by_filter(db: AsyncSession, filter_model: AlertFilterModel, purchased_scanner_list, selected_sub_categories):
    # query = select(Alert)
    AlertAlias = aliased(Alert)  
    AddressAlias = aliased(Address)  

    subquery = (  
        select(func.distinct(AlertAlias.id))  
        .select_from(AlertAlias)  
        .join(AddressAlias, AddressAlias.alert_id == AlertAlias.id)  
        .filter(AddressAlias.score >= 0.5)  
    ).subquery()  
    query = (  
        select(Alert)  
        .where(Alert.id.in_(subquery))  
        .order_by(desc(Alert.dateTime))  
    )
    result = await db.execute(query)
    alerts = result.scalars().all()
    print("alertS: ", alerts)
    if filter_model.headSearch:
        query = query.where(Alert.headline.ilike(f'%{filter_model.headSearch}%'))
    
    if filter_model.decSearch:
        query = query.where(Alert.description.ilike(f'%{filter_model.decSearch}%'))
    
    if filter_model.sub_category:
        decoded_sub_category = urllib.parse.unquote(filter_model.sub_category)
        query = query.filter(Alert.sub_category == decoded_sub_category)
    
    if filter_model.category:
        query = query.filter(Alert.category == filter_model.category)
    

    if filter_model.scanner_id:
        query = query.filter(Alert.scanner_id == filter_model.scanner_id)
        
    if filter_model.stars:
        query = query.filter(Alert.rating >= filter_model.stars)
        
    if filter_model.selected_from:  
        query = query.filter(Alert.dateTime >= filter_model.selected_from)  
    
    if filter_model.selected_to:  
        end_date = filter_model.selected_to + timedelta(days=1)  
        query = query.filter(Alert.dateTime < end_date)
    
    # query = query.filter(Alert.scanner_id.in_(purchased_scanner_list))
    # query = query.filter(Alert.sub_category.in_(selected_sub_categories))

    result = await db.execute(query)
    alerts = result.scalars().all()
    
    total = len(alerts)
    
    start = (filter_model.page - 1) * filter_model.limit
    alerts = alerts[start: start + filter_model.limit]
    
    print('alerts: ', alerts);

    return alerts, total


async def get_all_alerts(db: AsyncSession):
    query = select(Alert)
    # Dynamically apply filters

    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return alerts

async def get_alerts_by_id(db: AsyncSession, filter_model: IdFilterModel):
    query = select(Alert)
    print("filter_model.scanner_id: ", filter_model.scanner_id)
    query = query.filter(Alert.id == filter_model.alert_id)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def insert_purchased_scanners(db: AsyncSession, user_id, scanner_id):
    stmt = select(PurchasedScanner).filter(PurchasedScanner.user_id == user_id)
    stmt = stmt.filter(PurchasedScanner.scanner_id == scanner_id)
    result = await db.execute(stmt)
    result = result.scalars().all()
    
    if not result:
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
    
async def delete_purchased_scanners_by_scanner_id(db: AsyncSession, scanner_id: int, user_id: int):
    # Define the delete statement
    stmt = delete(PurchasedScanner).where(PurchasedScanner.scanner_id == scanner_id).where(PurchasedScanner.user_id == user_id)
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

async def insert_validated_address(db: AsyncSession, address, score, alert_id, type, scanner_id, dateTime):
    new_address = Address(address=address, score=score, alert_id=alert_id, type=type, scanner_id=scanner_id, dateTime=dateTime)
    db.add(new_address)
    await db.commit()
    await db.refresh(new_address)
    return new_address
                

async def get_addresses_by_alert_id(db: AsyncSession, alert_id):
    stmt = select(Address).filter(Address.alert_id == alert_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_address_by_id(db: AsyncSession, id):
    stmt = select(Address).filter(Address.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def set_variables(db: AsyncSession, prompt):
    query = select(Variables)
    result = await db.execute(query)
    result = result.scalars().all()
    if not result:
        new_variables = Variables(prompt=prompt)
        db.add(new_variables)
        print("new_variables", new_variables)
        await db.commit()
        await db.refresh(new_variables)
    else:
        updated_variables = result[0]
        updated_variables.prompt = prompt
        print("updated_variables", updated_variables)
        await db.commit()
        await db.refresh(updated_variables)
        
async def get_variables(db: AsyncSession):
    query = select(Variables)
    result = await db.execute(query)
    return result.scalar_one_or_none()
    

async def get_all_subcategories(db: AsyncSession, filter_model):
    query = select(Category)
    if filter_model.category:
        query = query.filter(Category.category == filter_model.category)
        
    if filter_model.search:
        query = query.where(Category.sub_category.ilike(f'%{filter_model.search}%'))
        
    result = await db.execute(query)
    return result.scalars().all()

async def get_selected_subcategories(db: AsyncSession):
    stmt = select(Category).filter(Category.is_selected == 1)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_subcategories(db: AsyncSession, category_object):
    stmt = select(Category).filter(Category.sub_category == category_object.sub_category)
    # print("category_object: ", category_object)
    result = await db.execute(stmt)
    result = result.scalar_one_or_none()
    result.is_selected = category_object.is_selected
    await db.commit()
    await db.refresh(result)

async def get_address_by_alert_id(db: AsyncSession, id):
    stmt = select(Address).filter(Address.alert_id == id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def insert_csv(db:AsyncSession, csv_context_json, state, county):
    query = select(Scanner).filter(  
        and_(  
            Scanner.state_name == state,  
            Scanner.county_name == county  
        )  
    ) 
    result = await db.execute(query)
    data = result.scalars().all()
    if not data:
        return None
    
    stmt = select(FireDistrict).filter(FireDistrict.state == state)
    stmt = stmt.filter(FireDistrict.county == county)
    result = await db.execute(stmt)
    data = result.scalar_one_or_none()
    if not data:
        new_district = FireDistrict(json_data=csv_context_json, state=state, county=county)
        db.add(new_district)
        await db.commit()
        await db.refresh(new_district)
        return new_district
    else:
        data.context = csv_context_json
        await db.commit()
        await db.refresh(data)
        return data


async def calculate_similarity(alert, unique_alerts, threshold=0.9):
    alert_doc = nlp(alert.description)
    for unique_alert in unique_alerts:
        unique_doc = nlp(unique_alert.description)
        if alert_doc.similarity(unique_doc) > threshold:
            return False
    return True

async def remove_duplicated_alerts(db: AsyncSession):
    query = select(Alert)
    results = await db.execute(query)
    alerts = results.scalars().all()
    print("Got all data!")

    unique_alerts = []
    for alert in alerts:
        alert_doc = nlp(alert.description)
        last_10_unique_alerts = unique_alerts[-10:]
        is_duplicate = any(alert_doc.similarity(nlp(unique_alert.description)) > 0.9 for unique_alert in last_10_unique_alerts)
        if not is_duplicate:
            unique_alerts.append(alert)
    print("Filtered unique data!")
    
    await db.execute(delete(Alert))
    print("Deleted current data!")

    for unique_alert in unique_alerts:
        db.add(Alert(
            category=unique_alert.category,
            sub_category=unique_alert.sub_category,
            headline=unique_alert.headline,
            description=unique_alert.description,
            address=unique_alert.address,
            scanner_id=unique_alert.scanner_id,
            dateTime=unique_alert.dateTime,
            is_visited=unique_alert.is_visited
        ))
    print("Added new data!")

    await db.commit()
    print("Committed!")

    return "success"
