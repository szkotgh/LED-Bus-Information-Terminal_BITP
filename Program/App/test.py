import app, sys, time


try:
    from tqdm import tqdm
except:
    sys.exit("tqdm module is not installed")


app.cls()

print("geting_bus_station_list..")
bus_station_list = app.get_bus_station_list()
print("geted_bus_station_list")

print("geting_arvl_bus_list..")
for bus_station in bus_station_list:
    try:
        app.get_arvl_bus_list(bus_station)
    except:
        pass
print("geted_arvl_bus_list")
        

for bus_station in bus_station_list:
    print(f"{bus_station.stationNm} ({bus_station.mobileNo})")
    
    for arvl_bus in bus_station.arvl_bus_list:
        if arvl_bus.is_arvl == False:
            try:
                print("{:20} ({:>2}분) ({:>2}번째 전)     {:10}".format(arvl_bus.routeNm+"(회차지대기)" if arvl_bus.flag == "WAIT" else arvl_bus.routeNm, arvl_bus.predictTime, arvl_bus.locationNo, arvl_bus.routeNowStaNm))
            except:
                pass
            
    arvl_bus_list = []
    for arvl_bus in bus_station.arvl_bus_list:
        if arvl_bus.is_arvl == True:
            arvl_bus_list.append(arvl_bus.routeNm)
    
    print("곧도착: ", end="")
    if arvl_bus_list != []:
        for arvl_bus in arvl_bus_list:
            print(arvl_bus, end=" ")
            
    ## TTS
    if arvl_bus_list != []:
        speak_text = ""
        for arvl_bus in bus_station.arvl_bus_list:
            if arvl_bus.is_arvl == True:
                speak_text = speak_text + str(arvl_bus.routeNm) + "번, "
        
        speak_text = speak_text[:-2] + ". "
        speak_text = speak_text + "버스가 잠시 후 도착할 예정입니다."
        
        app.speak_text(speak_text)
    
    print(end="\n\n")