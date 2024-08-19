import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GOOGLE_GEOCODING_API_KEY")

def get_geocode_data(address):
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    params = {
        'address': address,
        'key': api_key,
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        data = response.json()
        
        if data['results']:
            return data['results']
        else:
            print("No results found.")
            
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        
def get_score_by_location_type(location_type):
    if location_type == "ROOFTOP":
        return 1
    elif location_type == 'RANGE_INTERPOLATED':
        return 0.7
    elif location_type == 'GEOMETRIC_CENTER':
        return 0.5
    elif location_type == 'APPROXIMATE':
        return 0.3
    