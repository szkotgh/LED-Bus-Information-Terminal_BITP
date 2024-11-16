import os
from bitp_app import BITPApp        

BITP_App = BITPApp()
while True:
    try:
        BITP_App.show_main_content()
    except Exception as e:
        BITP_App.matrix_manager.error_page(str(e), 10)
        # os.system('sudo systemctl restart bitp')