from flask import Flask
import threading
import modules.config as config
import modules.matrix_manager as matrix_manager
import modules.web_manager.router as web_mgr_router

# 원격으로 접속하여 BIT를 관리할 수 있도록 하는 웹서버를 만들기 위한 Manager임.
# 이미지, 동영상, 음악 파일 등을 업로드 하면 웹에서 관리하여 재생할 수 있도록 해야함.
# 또, 실시간으로 현재 띄워지고 있는 정보나 BIT 상태를 확인할 수 있도록 해야함.
# 귀찮아서 만들진 않음 . . .

class FlaskAppRunner:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.thread = None

        # Start web manager
        matrix_manager.matrix_pages.text_page(f"웹 서버 실행 중 . . .", 0, 0.1, _status_prt=False)
        try:
            self.start()
        except:
            matrix_manager.matrix_pages.exit_page(['웹 서버 실행 실패', '웹 서버를 실행할 수 없습니다.', '', '', 'BIT를 부팅할 수 없습니다 . . .'], 1, 1, 2, _text_color='orange', _status_prt=False, _exit_code=1)
        matrix_manager.matrix_pages.text_page(['웹 서버 실행 성공'], 0, 1, _text_color='lime', _status_prt=False)

        # Register router
        self.app.register_blueprint(web_mgr_router.router_bp)

    def start(self):
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run_flask, daemon=True)
            self.thread.start()
            return 0
        else:
            return 1

    def run_flask(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

service = FlaskAppRunner(config.OPTIONS['web']['host'], config.OPTIONS['web']['port'])