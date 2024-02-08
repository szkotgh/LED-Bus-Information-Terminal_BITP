import requests, json, xmltodict

url = 'http://apis.data.go.kr/6410000/busrouteservice/getBusRouteStationList'
params = {
    'serviceKey' : 'Y+K/PG7BzlPBzLKybehRrc2U90kkXQbkuDj3DrFrnXRgL2UWCO8uIyaHlZPaKPsHPn0nCF2fcRP6eVnAUn4mUA==',
    'routeId' : '241426001'
}

def xml_to_dict(xml_data, indent=4) -> json:
    try:
        json_data = json.dumps(xmltodict.parse(xml_data), indent=indent)
        return json.loads(json_data)
    except Exception as e:
        print(e)
        return None

response = requests.get(url, params=params)

response = xml_to_dict(response.content)

print(response['response']['msgBody']['busRouteStationList'])