import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager
import modules.web_manager as web_manager
import modules.utils as utils

# show test page
matrix_manager.matrix_pages.test_page(0, 1)
matrix_manager.matrix_pages.test_page(1, 3)
matrix_manager.matrix_pages.test_page(2, 3)

# if internet not connected
while True:
    if info_manager.service.network.is_internet_connected:
        matrix_manager.matrix_pages.init_test_internet_connected_page(3)
        break
    else:
        matrix_manager.matrix_pages.init_test_internet_connected_page(1)

# show start page
matrix_manager.matrix_pages.start_page(15)

# show bus station page
while True:
    for i in range(0, len(info_manager.service.station_datas)):
        for repeat in range(3):
            matrix_manager.matrix_pages.bus_station_page(info_manager.service.station_datas[i], 5)
            matrix_manager.matrix_pages.bus_station_etc_page(info_manager.service.station_datas[i], 5)
        matrix_manager.matrix_pages.everline_page(10)