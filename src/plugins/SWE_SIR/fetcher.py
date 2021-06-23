# Copyright (C) 2020 University of Oxford
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Svenska Intensivvårdsregistret (SIR)
# https://portal.icuregswe.org/siri/report/corona.inrapp
#

import os
import io
import logging
import psycopg2
from datetime import date, datetime
import requests
import pandas as pd

__all__ = ('SwedenSIRFetcher',)

from utils.fetcher.base_epidemiology import BaseEpidemiologyFetcher

logger = logging.getLogger(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))

class SwedenSIRFetcher(BaseEpidemiologyFetcher):
    LOAD_PLUGIN = False
    SOURCE = 'SWE_SIR'

    # SIR region divisions
    REGIONS = {
        'Hela riket': [],
        'Blekinge': ['37', '87'],
        'Dalarna': ['27', '41'],
        'Gotland': ['61'],
        'Gävleborg': ['46', '4', '44'],
        'Halland': ['29', '35'],
        'Jämtland': ['23'],
        'Jönköping': ['15', '14', '16'],
        'Kalmar': ['1', '3'],
        'Kronoberg': ['49', '36'],
        'Norrbotten': ['45', '70', '68', '48'],
        'Orebro': ['84', '85', '50', '83'],
        'Skåne': ['54', '10', '73', '30', '74', '75', '88', '24', '53'],
        'Stockholm': ['6', '43', '62', '72', '95', '42', '77', '9', '8', '7', '58', '5', '89'],
        'Södermanland': ['64', '57'],
        'Uppsala': ['55', '90', '56', '79', '78'],
        'Västra Götaland': ['39', '28', '52', '34', '92', '31', '33', '59', '19', '22', '20', '18', '21', '86', '38'],
        'Värmland': ['25', '17', '26'],
        'Västerbotten': ['71', '51', '47', '81'],
        'Västernorrland': ['32', '66', '67'],
        'Västmanland': ['65'],
        'Östergötland': ['91', '11', '82', '40', '12']
    }

    def get_gids(self) -> dict:
        '''Gets the name and gid of Sweden and all its adm_area_1 instances.
        
        Fetches the adm_area_1 data from the database and manually adds Sweden's gid.
        '''
        # Local DB
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            dbname='covid19database',
            user='postgres',
            password='password'
        )

        sql = f"SELECT adm_area_1, adm_area_1_code FROM covid19_schema.administrative_division WHERE country = 'Sweden' AND adm_level = '1'"
        df_adm_div = pd.read_sql(sql, conn)

        conn.close()

        nested_dict = df_adm_div.to_dict()
        merged_dict = self.merge_dict(nested_dict)
        merged_dict['Hela riket'] = 'SWE'
        
        return merged_dict


    def merge_dict(self, nested_dict) -> dict:
        '''Takes a dict with two nested dicts and returns a merged dict'''
        left_dict = list(nested_dict.values())[0] 
        right_dict = list(nested_dict.values())[1]

        merged_dict = {}

        for key in left_dict:
            merged_dict[left_dict[key]] = right_dict[key]

        return merged_dict


    def fetch(self, startdat, stopdat, region):
        '''Fetches API data from SRI and returns a merged dictionary'''
        logger.debug(f'Getting ICU data for SWE between {startdat} and {stopdat} for {region}.')

        url = 'https://portal.icuregswe.org/siri/api/reports/GenerateExcel'

        data = {
            'highChartUrl': '/api/reports/GenerateHighChart',
            'tableUrl': '/api/reports/GenerateExcel',
            'reportName': 'corona.kumulativ',
            'chartWidth': '900',
            'startdat': startdat,
            'stopdat': stopdat,
            'sasong[0]': 2020
        }

        region_list = self.REGIONS[region]

        for i in region_list:
            idx = region_list.index(i)
            data[f'avd[{idx}]'] = i

        headers = {
            'origin': 'https://portal.icuregswe.org',
            'referer': 'https://portal.icuregswe.org/siri/report/corona.kumulativ'
        }

        r = requests.post(url, data=data, headers=headers)
        df = pd.read_excel(io.BytesIO(r.content), skiprows=[0])
        
        nested_dict = df.to_dict()
        merged_dict = self.merge_dict(nested_dict=nested_dict)

        return merged_dict


    def run(self):
        '''The main function of the fetcher'''
        today = date.today()

        gids_list = self.get_gids()

        print('ADM LIST:', gids_list)
        print(len(gids_list))

        # Calculate how many days of data should be fetched
        #if self.sliding_window_days:
            # Number of days in the past to process
            #sliding_window_days = self.sliding_window_days
        #else:
            # Number of days since first SIR data (2020 w13)
            #sliding_window_days = (today - date(2020, 3, 23)).days

        startdat = '2020-03-02' # First SIR data (2020 w10)
        stopdat = today 
        #region = self.REGIONS['Skåne']

        for region in self.REGIONS:
            r = self.fetch(startdat, stopdat, region)

            for key, value in r.items():
                # Get sunday of week in key
                sunday = datetime.strptime(key + '-0', '%Y v%W-%w')
                #print('KEY:', key)
                #print('SUNDAY:', sunday)

                upsert_date = sunday

                vtf_cumulative = value
                gid = gids_list[region]

                upsert_obj = {
                    'source': self.SOURCE,
                    'date': upsert_date,
                    'country': 'Sweden',
                    'countrycode': 'SWE',
                    'gid': '{' + gid + '}',
                    'hospitalised_icu': vtf_cumulative
                }

                if region != 'Hela riket':
                    upsert_obj['adm_area_1'] = region

                #print(upsert_obj)
                self.upsert_data(**upsert_obj)