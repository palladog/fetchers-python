import os
import io
from datetime import date, timedelta
import requests
import pandas as pd

dir_path = os.path.dirname(os.path.realpath(__file__))

def merge_dict(dct):
    week_dict = list(dct.values())[0] 
    vtf_dict = list(dct.values())[1] # vtf = vårdtillfällen

    merged_dict = {}

    for key in week_dict:
        merged_dict[week_dict[key]] = vtf_dict[key]

    return merged_dict


def fetch():
    url = 'https://portal.icuregswe.org/siri/api/reports/GenerateExcel'

    data = {
        'highChartUrl': '/api/reports/GenerateHighChart',
        'tableUrl': '/api/reports/GenerateExcel',
        'reportName': 'corona.kumulativ',
        'chartWidth': '900',
        'startdat': '2020-01-01',
        'stopdat': '2021-06-18',
        'sasong[0]': 2020,
    }

    headers = {
        'origin': 'https://portal.icuregswe.org',
        'referer': 'https://portal.icuregswe.org/siri/report/corona.kumulativ'
    }

    r = requests.post(url, data=data, headers=headers)
    df = pd.read_excel(io.BytesIO(r.content), skiprows=[0])
    nested_dict = df.to_dict()
    merged_dict = merge_dict(nested_dict)
    print(merged_dict)

fetch()

    