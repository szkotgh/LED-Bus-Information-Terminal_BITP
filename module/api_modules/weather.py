'''
WEATHER.PY
----------
날씨와 관련된 객체와 변수가 있는 모듈입니다.
기온과 미세먼지를 얻는 API를 손쉽게 호출할 수 있습니다.
'''

import sys
import datetime
import requests
import xmltodict

class weather_api_requester:
    '''
    날씨 API 요청 관리 객체
    '''
    def __init__(self, SERVICE_KEY):
        self.SERVICE_KEY = SERVICE_KEY
        self.base_url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0'

    def get_vilage_fcst(self, nx, ny, base_date, base_time, num_of_rows=1000, page_no=1, data_type='JSON'):
        url = f"{self.base_url}/getVilageFcst"
        params = {
            'serviceKey': self.SERVICE_KEY,
            'numOfRows': num_of_rows,
            'pageNo': page_no,
            'dataType': data_type,
            'base_date': base_date,
            'base_time': base_time,
            'nx': nx,
            'ny': ny
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            if data_type == 'JSON':
                return response.json()
            else:
                return xmltodict.parse(response.content)
        else:
            response.raise_for_status()

    def get_tomorrow_weather(self, nx, ny):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        base_date = today.strftime('%Y%m%d')
        
        # Determine appropriate base_time based on current time
        current_time = today.strftime('%H%M')
        if '2300' <= current_time or current_time < '0500':
            base_time = '2300'
        elif '0500' <= current_time < '1100':
            base_time = '0500'
        elif '1100' <= current_time < '1700':
            base_time = '1100'
        else:
            base_time = '1700'
        
        tomorrow_date = tomorrow.strftime('%Y%m%d')

        # Debugging: Print the request details
        print(f"Requesting data for base_date: {base_date}, base_time: {base_time}")
        
        data = self.get_vilage_fcst(nx, ny, base_date, base_time)
        
        # Debugging: Print the response data
        print("Response data:", data)
        
        # Extract weather forecast for tomorrow
        forecast = []
        if data['response']['header']['resultCode'] == '00':
            items = data['response']['body']['items']['item']
            for item in items:
                if item['fcstDate'] == tomorrow_date:
                    forecast.append(item)
        else:
            # Debugging: Print the resultCode and resultMsg if not '00'
            print(f"Error: {data['response']['header']['resultCode']} - {data['response']['header']['resultMsg']}")
        return forecast

if __name__ == "__main__":
    SERVICE_KEY = 'Y+K/PG7BzlPBzLKybehRrc2U90kkXQbkuDj3DrFrnXRgL2UWCO8uIyaHlZPaKPsHPn0nCF2fcRP6eVnAUn4mUA=='  # Replace with your actual service key
    nx = 55  # Replace with actual X coordinate
    ny = 127  # Replace with actual Y coordinate

    weather_requester = weather_api_requester(SERVICE_KEY)
    tomorrow_weather = weather_requester.get_tomorrow_weather(nx, ny)
    print(tomorrow_weather)
