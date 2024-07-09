import requests
from difflib import SequenceMatcher
from urllib.parse import urlencode

api_key="AIzaSyBaiaHH_dU8xqAYiY544N_vyDVQweiMyF4"

def get_geocode_data(address):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    encoded_params = urlencode(params)

    response = requests.get(f"{url}?{encoded_params}")
    
    if response.status_code == 200:
        # print(response.json())
        return response.json()
    else:
        return None

def score_address_components(user_components, google_components):
    score = 0
    max_score = len(user_components)
    for user_component in user_components:
        match_found = False
        for google_component in google_components:
            if SequenceMatcher(None, user_component, google_component).ratio() > 0.8:
                score += 1
                match_found = True
                break
        if not match_found:
            score -= 0.5 # Penalty for mismatch
    return max(0, score / max_score)

def parse_address_components(address):
    return [component.strip().lower() for component in address.split(',')]

def validate_address(addresses):
    result = []
    for data in addresses['addresses']:
        address = data['address']
        user_components = parse_address_components(address)
        geocode_data = get_geocode_data(address)
        if geocode_data and geocode_data['status'] == 'OK':
            google_components = parse_address_components(geocode_data['results'][0]['formatted_address'])
            score = score_address_components(user_components, google_components)
            print(f"User Address: {address}")
            print(f"Validated Address: {google_components}")
            print(f"Accuracy Score: {score:.2f}\n")
            result.append({"address": address, "score": score})
        else:
            print(f"Invalid or Not Found Address: {address}")
            print(f"Error: {geocode_data.get('status', 'Unknown Error') if geocode_data else 'No response from API'}\n")
    return result