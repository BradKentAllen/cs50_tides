#!/usr/bin/env python
'''
file name:  NOAA_tides.py
date created: February 2025
created by:  Brad Allen
project/support:  cs50             # root or script it supports
description:
    Get tide data from NOAA COOPs and interpolate tides

special instruction:

Co Ops API:  https://api.tidesandcurrents.noaa.gov/api/prod/
Current Station Index:  https://tidesandcurrents.noaa.gov/noaacurrents/Stations?g=698
Current Station Map:  https://tidesandcurrents.noaa.gov/map/index.html#
    - On the map, click 'advanced' in left
    - Change data type to current prediction

'''
__revision__ = 'v0.0.1'
__status__ = 'DEV' # 'DEV', 'alpha', 'beta', 'production'

import datetime
import json
import math
import pickle

import pandas as pd
import requests
from requests.exceptions import HTTPError

import config


class NOAA_TIDES():
    def __init__(self, db):
        self.cache_days = config.NOAA_data_cache_days
        self.stations_dict = config.NOAA_tide_stations
        self.db = db

    def create_stations_tides_dict(self):
        ''' Cache a single file with tide dict that starts day before at midnight
        and goes for number of days set in __init__
        '''
        start_datetime = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
        time_range = 24 * self.cache_days

        stations_tides_dict = {}

        for station in self.stations_dict:
            station_ID = self.stations_dict.get(station, None)
            if station_ID is not None:
                stations_tides_dict[station] = self.get_tide_prediction(station_ID, start_datetime, time_range)

        return stations_tides_dict

    def get_tide_prediction(self, station_ID, begin_date=datetime.datetime.now().strftime("%Y%m%d"), time_range=config.NOAA_data_cache_days):
        '''Return JSON from NOAA and convert to a tide dict
        '''
        url = "&".join(('https://tidesandcurrents.noaa.gov/api/datagetter?datum=mllw',
                        f"begin_date={begin_date}",
                        f"range={time_range}",
                        f"product={'predictions'}",
                        f"interval={'hilo'}",
                        f"format=json",
                        f"units={'english'}",
                        f"time_zone=lst_ldt",
                        f"station={station_ID}",
                        ))

        response = requests.get(url)

        # use requests built in error handling
        response.raise_for_status()

        # load json into data object
        tide_data = json.loads(response.text)

        tide_dict = {}

        for count, _tide_dict in enumerate(tide_data.get("predictions")):
            _tide_name = f"tide_{count}"

            # rename the height key
            _tide_dict['height'] = _tide_dict.pop('v')

            # change time to datetime
            _time = datetime.datetime.strptime(_tide_dict.get('t'), '%Y-%m-%d %H:%M')
            _tide_dict.pop('t')
            _tide_dict['time'] = _time

            # put in tide dict
            tide_dict[_tide_name] = _tide_dict

        return tide_dict

    def create_tide_data_file(self, stations_tides_dict):
        '''creates a dict with date and duration
        '''
        return {
            "stations_tides_dict": stations_tides_dict,
            "date": datetime.datetime.now(),
            "duration_days": config.NOAA_data_cache_days,
        }

    def cache_tide_data(self, tide_dict):
        '''standard method for caching the tide data
        '''
        self.db.pickle_file(tide_dict, config.tides_cache_filepathname)
        return True

    def get_tide_cache(self):
        return self.db.load_pickle_file(config.tides_cache_filepathname)

    def parse_station_tide_data(self, tides_data, station_name):
        '''parse a full tides_data dict to one station's predictions
        '''
        station_tide_data = tides_data.get("stations_tides_dict", "no tide data").get(station_name, "no station data")
        return station_tide_data

    def get_next_tide_string(self, tide_dict, time=None):
        '''returns display string telling type of tide and height
        IMPORTANT:  the input here is the data for one station, stations_tides must be parsed down to a station using
        parse station data.
        '''
        print(">>>> get_next_tide_string <<<")

        # note:  you cannot dynamically assign a default value in the function because the default will be assigned when the 
        # class inits, not each time it runs.

        if not isinstance(time, datetime.datetime):
            time = datetime.datetime.now()
        print(f"will use this time: {time}")
        print(f"datatime.datetime.now(): {datetime.datetime.now()}")
        # #### Find which two tides you are between
        previous_key = 0
        for key, value in tide_dict.items():
            print(f'{key}: {value}')
            if time <= value.get('time'):
                break

            previous_key = key

        next_tide = tide_dict.get(key)['type']
        next_tide_time = tide_dict.get(key)['time']
        next_tide_height = float(tide_dict.get(key)['height'])

        if next_tide == 'H':
            next_tide = 'High'
        else:
            next_tide = 'Low'

        tide_string = f"{next_tide_height:.1f}\' {next_tide} at {datetime.datetime.strftime(next_tide_time, '%-I:%M %p')}"

        return tide_string

    def get_current_tide_height(self, tide_dict):
        '''XXXX needs work
        How to get data for first tide after midnight and last tide of day
        '''
        # #### Find which two tides you are between
        previous_key = 0
        for key, value in tide_dict.items():
            #print(f'{key}: {value}')
            if datetime.datetime.now() <= value.get('time'):
                break

            previous_key = key

        #print(f'\ntide is betwen {previous_key} and {key}')

        # #### Deal with first tide period after midnight
        if previous_key == 0:
            tide_dict[0] = previous_tide_data


        # use keys to get tides at start and finish of 
        start_tide_dict = tide_dict[previous_key]
        end_tide_dict = tide_dict[key]
        
        minutes_span = int(((end_tide_dict.get('time') - start_tide_dict.get('time')).total_seconds()/60))

        tide_minutes = int(((datetime.datetime.now() - start_tide_dict.get('time')).total_seconds()/60))

        tide_span = float(end_tide_dict.get('height')) - float(start_tide_dict.get('height'))

        # determine which portion of sine wave to use
        sine_offset = 1.5

        # position on sine wave
        try:
            i = math.pi * (sine_offset + (tide_minutes / minutes_span))
        except ZeroDivisionError:
            i = 0

        # get actual value
        # offset the sine wave up (0 to 2) then divide to get (0 to 1)
        sine_x = (math.sin(i) + 1.0) / 2

        # use the sine and the full tide span to get the current height
        tide_height = (sine_x * tide_span) + float(start_tide_dict.get('height'))

        return tide_height




if __name__ == "__main__":
    run = NOAA_TIDES(db="fake_db")  
    # #### Test Tides ####
    print("\nTest Tides")

    station_name = "Arletta"
    station_ID = 9446491

    filename = "temp.pkl"

   
    # #### IMPORTANT:  Uncomment this section to query the NOAA API
    tide_dict = run.get_tide_prediction(station_ID=station_ID)

    # Pickle the dictionary and save it to a file
    
    with open(filename, 'wb') as file:
        pickle.dump(tide_dict, file)
   

    # Load the pickled dictionary from the file
    with open(filename, 'rb') as file:
        tide_dict = pickle.load(file)

    print(tide_dict)

    # test get_next_tide_string
    next_tide_str = run.get_next_tide_string(tide_dict, datetime.datetime.now())

    print(f"\n{next_tide_str}")

    # test get_current_tide_height
    current_tide_height = run.get_current_tide_height(tide_dict)

    print(f"\ncurrent tide height: {current_tide_height:.2f}")
    





















