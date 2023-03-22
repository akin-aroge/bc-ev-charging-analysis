import pandas as pd
import os
import requests

def get_raw_data(file_path, update=False):
    
    '''retrieve exisiting raw data either from `file_path` or from api if update=True.
    data is saved for future retrival
    '''
    
    if not update:
        try:
            data = pd.read_csv(file_path)
        except FileNotFoundError:
            print("file does not exist, downloading data instead")
            data = _pull_data()
            data.to_csv(file_path, index=False)
    else:
        data = _pull_data()
        data.to_csv(file_path, index=False)
        
    data = pd.read_csv(file_path)  
    
    
    return data
        
    
    
def _pull_data():
    """queries api to retrieve data filtered by query parameters and returns a dataframe object"""
    api_key = os.environ['API_KEY']
    query_params = {'api_key':api_key, 
                'country':'CA',
                'state':'BC',
               'access':'public',
               'status':'E,P',
               'owner_type': 'all',
               'cards_accepted': 'all',
               'fuel_type':'ELEC',
               'ev_charging_level':'2,dc_fast',
               'ev_connector_type': 'all',
               'ev_network':'all'}
    response = requests.get("http://developer.nrel.gov/api/alt-fuel-stations/v1.json", params=query_params)
    r_dict = response.json()
    raw_data = pd.json_normalize(r_dict['fuel_stations'])
    
    return raw_data