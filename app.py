import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager
matrix = matrix_manager

while True:
    matrix.matrix_pages.start_page(10)
    print(info_manager.service.control_pannel.get_state())