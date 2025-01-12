import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager
matrix = matrix_manager

while True:
    # matrix.matrix_pages.bus_station_etc_page(0, 10)
    print(info_manager.service.control_pannel.status_devices)
    matrix.matrix_pages.start_page(10)