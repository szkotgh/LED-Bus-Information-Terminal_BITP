import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manage
import modules.info_manager.apis.control_pannel as control_pannel
matrix = matrix_manager

while True:
    # matrix.matrix_pages.bus_station_etc_page(0, 10)
    matrix.matrix_pages.start_page(10)
    print(control_pannel.get_state())
    control_pannel.set_states({"LED1": True, "LED2": False, "LED3": False, "LED4": False})
    control_pannel.set_states({"LED1": False, "LED2": True, "LED3": False, "LED4": False})
    control_pannel.set_states({"LED1": False, "LED2": False, "LED3": True, "LED4": False})
    control_pannel.set_states({"LED1": False, "LED2": False, "LED3": False, "LED4": True})
    
    control_pannel.set_states({"RELAY1": True, "RELAY2": True, "RELAY3": True, "RELAY4": True})
    control_pannel.set_states({"RELAY1": False, "RELAY2": False, "RELAY3": False, "RELAY4": False})