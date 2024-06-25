import requests
import app.Utils.crud as crud

from bs4 import BeautifulSoup

def extract_ids_from_response(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    archive_info = []

    table_body = soup.find('tbody')
    if table_body:
        for row in table_body.find_all('tr'):
            feed_link = row.find('a')
            feed_id = int(feed_link['href'].split('/')[-1])
            feed_title = feed_link.text.strip()
            
            # Number of listeners
            listeners_span = row.find('span', class_='badge')
            listeners_count = listeners_span.text.split()[0] if listeners_span else '0'
            
            archive_info.append({
                'scanner_id': feed_id,
                'scanner_title': feed_title,
                'listeners_count': listeners_count
            })
    
    return archive_info


def parse_scanners(session, ctid):
    url = "https://www.broadcastify.com/scripts/ajax/chooserFeeds.php"
    data = {
        "ctid": str(ctid),
        "a": "feeds",
        "style": "v2"
    }
    print("formatted_url: ", url)
    response = session.post(url, data=data)
    scanners_list = extract_ids_from_response(response)
    return scanners_list

def get_state_list_for_country(session, coid):
    url = f"https://www.broadcastify.com/scripts/ajax/location.php?coid={coid}"
    state_response = session.get(url).json()
    state_list = []
    for state in state_response:
        state_list.append({"state_id": state['optionValue'], "state_name": state["optionDisplay"]})
    return state_list

def get_county_list_for_state(session, stid):
    print("stid: ", stid)
    url = f"https://www.broadcastify.com/scripts/ajax/location.php?stid={stid}"
    county_response = session.get(url).json()
    county_list = []
    print('-----------------------')
    for county in county_response:
        county_list.append({"county_id": county['optionValue'], "county_name": county['optionDisplay']})
    return county_list

async def update_scanners(db, coid = 1):
    username = "alertai"
    password = "Var+(n42421799)"
    action = "auth"
    redirect = "https://www.broadcastify.com/"
    
    s = requests.Session()

    base_url = "https://www.broadcastify.com"
    login_url = "https://m.broadcastify.com/login/"
    payload = {
        "username": username,
        "password": password,
        "action": action,
        "redirect": redirect,
    }
    s.post(
        login_url,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    # verify if this is successful
    if s.cookies.get("bcfyuser1", default=None) is None:
        print("Login failed")
        return
    print("Login successful")



    state_list = get_state_list_for_country(s, coid)
    
    result = []
    print("state_list: ", state_list)
    
    for state in state_list:
        state_id = int(state['state_id'])
        state_name = state['state_name']
        if state_id == 0:
            continue
        
        county_list = get_county_list_for_state(s, state_id)
        print("county_list", county_list)
        state_dict = {}
        state_dict['state_id'] = state_id
        state_dict['state_name'] = state_name
        state_scanners = []
        
        for county in county_list:
            county_id = int(county['county_id'])
            county_name = county['county_name']
            
            if county_id == 0:
                continue
            
            county_dict = {}
            county_dict['county_id'] = county_id
            county_dict['county_name'] = county_name
            
            
            scanners_in_county = parse_scanners(
                s,
                ctid=county_id
            )
            
            county_dict['scanners'] = scanners_in_county
            
            for scanner in scanners_in_county:
                await crud.insert_scanner(db, state_id, state_name, county_id, county_name, scanner)
            state_scanners.append(county_dict)
        state_dict['scanners'] = state_scanners
        result.append(state_dict)
    return result
