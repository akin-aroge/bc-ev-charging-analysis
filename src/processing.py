import pandas as pd
import os
import requests


RAW_DATA_PATH = os.path.normpath(r'./data/raw/raw_data.csv')
CLEAN_DATA_PATH = os.path.normpath(r'./data/clean/clean_data.csv')

def _pull_data():
    """queries api to retrieve data filtered by query parameters and returns a dataframe object"""
    api_key = os.environ['LOCATOR_API_KEY']
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
    # response = requests.get("http://developer.nrel.gov/api/alt-fuel-stations/v1.json", params=query_params)
    
    try:
        response = requests.get("http://developer.nrel.gov/api/alt-fuel-stations/v1.json", params=query_params)
        response.raise_for_status()
        r_dict = response.json()
        raw_data = pd.json_normalize(r_dict['fuel_stations'])
        # print("data refresh")
        return raw_data
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)



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

    # TODO: temporary solution for raw data, consider removing.   
    data = pd.read_csv(file_path)  
    
    return data
        
def bound_df_region(df, boundaries):
    '''
    This filters the input dataset and returns only the subset 
    where the latitude and longitude values are within the boundaries set.
    
    Note: This was needed to catch some outlier location (somewhere in Quebec) 
    points seen when visualizing the map later in the analysis
    '''
    region_only_df = df[(df['latitude'] >= boundaries['lat_min']) &
                   (df['latitude'] <= boundaries['lat_max']) &
                    (df['longitude'] >= boundaries['lon_min']) &
                    (df['longitude'] <= boundaries['lon_max'])
                   ].copy(deep=True)
    
    return region_only_df
    


# British Columbia Boundaries. Source: https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/
BC_MAX_LAT = 60.00
BC_MAX_LON = -114.03
BC_MIN_LAT = 48.30
BC_MIN_LON = -139.06

BC_boundaries = {'lat_min':BC_MIN_LAT,
                'lat_max': BC_MAX_LAT,
                'lon_min': BC_MIN_LON,
                'lon_max':BC_MAX_LON}



def sanitize(data):

    clean_data = ( data.loc[:, data.nunique() != 1]  # drop constant column
        .dropna(axis=1, how='all')  # drop columns with no values
        .pipe(bound_df_region, boundaries=BC_boundaries) # trim datapoints outside BC
        )

    return clean_data


def get_clean_data(update=False):

    if not update:
        try:
            clean_data = pd.read_csv(CLEAN_DATA_PATH)
            return clean_data
        except FileNotFoundError:
            raw_data = get_raw_data(file_path=RAW_DATA_PATH, update=update)
            clean_data = sanitize(raw_data)

    elif update:
        raw_data = get_raw_data(file_path=RAW_DATA_PATH, update=update)
        clean_data = sanitize(raw_data)

    clean_data.to_csv(CLEAN_DATA_PATH, index=False)

    return clean_data



