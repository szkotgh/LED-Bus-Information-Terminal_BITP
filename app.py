import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager

while True:
    matrix_manager.matrix_pages.start_page(15)
    for i in range(0, len(info_manager.service.station_datas)):
        matrix_manager.matrix_pages.bus_station_page(info_manager.service.station_datas[i])
        matrix_manager.matrix_pages.bus_station_etc_page(info_manager.service.station_datas[i], 5)
    matrix_manager.matrix_pages.everline_page(15)