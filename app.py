from dotenv import load_dotenv
import os
from bit_web import BITApp

load_dotenv()
WEB_HOST = os.getenv('WEB_HOST')
WEB_PORT = os.getenv('WEB_PORT')

app = BITApp(WEB_HOST, WEB_PORT, True)
app.run()
