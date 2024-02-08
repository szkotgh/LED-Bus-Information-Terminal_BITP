import app

bus_station_list = app.get_bus_station_list()

for bus_station in bus_station_list:
    app.get_arvl_bus_list(bus_station)

for bus_station in bus_station_list:
    print(f"{bus_station.stationNm} ({bus_station.mobileNo})")
    
    for arvl_bus in bus_station.arvl_bus_list:
        if arvl_bus.is_arvl == False:
            print("{:6} ({:>2}분) ({:>2}번째 전)     {:10}".format(arvl_bus.routeNm, arvl_bus.predictTime, arvl_bus.locationNo, arvl_bus.routeNowStaNm))
    
    print("곧도착: ", end="")
    for arvl_bus in bus_station.arvl_bus_list:
        if arvl_bus.is_arvl == True:
            print(arvl_bus.routeNm, end=" ")
    
    print(end="\n\n")