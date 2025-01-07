import modules.matrix_manager as matrix_manager
from modules.userCtrl_manager import get_state, set_states
matrix = matrix_manager.MatrixPages()

while True:
    state = get_state()
    if state == None:
        continue