import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.safetydata.go.kr"
dataName = "/V2/api/DSSP-IF-00247"
serviceKey = "K62438D807NA7877"

st_num = 9776
while 1:
    payloads = {
        "serviceKey": serviceKey,
        "returnType": "json",
        "pageNo": str(st_num),
        "numOfRows": "1",
    }

    response = requests.get(url + dataName, params=payloads)
    print(response.text)
    
    if response.text.find('용인') != -1:
        print("\n\n")
        print(response.text)
        break;
    
    st_num -= 1
    