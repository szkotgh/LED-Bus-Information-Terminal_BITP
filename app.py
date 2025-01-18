import modules.matrix_manager as matrix_manager
import modules.info_manager as info_manager
import modules.audio_manager as audio_manager
import modules.utils as utils

matrix_manager.matrix_pages.test_page(0, 1)
matrix_manager.matrix_pages.test_page(1, 3)
matrix_manager.matrix_pages.test_page(2, 3)
matrix_manager.matrix_pages.start_page(15)
while True:
    for i in range(0, len(info_manager.service.station_datas)):
        for repeat in range(3):
            audio_manager.master.tts_play('버스 도착 정보를 알려드립니다.', utils.get_env_key('GOOGLE_API_KEY'))
            matrix_manager.matrix_pages.bus_station_page(info_manager.service.station_datas[i], 5)
            matrix_manager.matrix_pages.bus_station_etc_page(info_manager.service.station_datas[i], 5)
        matrix_manager.matrix_pages.everline_page(10)