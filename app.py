import modules.config as config
import modules.utils as utils
import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager
from modules.userCtrl_manager import get_state, set_states
import time

while 1:
    status = get_state()
    if status is None:
        continue
    
    set_states({"LED1": status['BUTTON1'], "LED2": status['BUTTON2']})
    time.sleep(0.1)