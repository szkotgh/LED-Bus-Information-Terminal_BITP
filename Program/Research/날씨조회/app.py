import requests

url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
params = {
    'serviceKey' : 'Y+K/PG7BzlPBzLKybehRrc2U90kkXQbkuDj3DrFrnXRgL2UWCO8uIyaHlZPaKPsHPn0nCF2fcRP6eVnAUn4mUA==',
    'numOfRows'  : '1000',
    'pageNo'     : '1',
    'dataType'   : 'json',
    'base_date'  : '20240209',
    'base_time'  : '0600',
    'nx'         : '55',
    'ny'         : '127'
}

response = requests.get(url, params=params)

print(response.text)