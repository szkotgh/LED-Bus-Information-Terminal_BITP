import requests, json, xmltodict

serviceKey = "Y+K/PG7BzlPBzLKybehRrc2U90kkXQbkuDj3DrFrnXRgL2UWCO8uIyaHlZPaKPsHPn0nCF2fcRP6eVnAUn4mUA=="
keyword    = "29412"

def xml_to_json(xml_data, indent=4) -> json:
    try:
        return json.dumps(xmltodict.parse(xml_data), indent=indent)
    except Exception as e:
        print(e)
        return None

url = 'http://apis.data.go.kr/6410000/busstationservice/getBusStationList'
params = {
    'serviceKey' : serviceKey,
    'keyword'    : keyword
}

response = requests.get(url, params=params)
# response = xml_to_json(response.content)

print(response.text)