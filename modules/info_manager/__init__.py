import os
import sys
import json
import logging
from datetime import datetime, timedelta
import modules.config as config
import modules.utils as utils

class InfoManager:
    def __init__(self, SERVICE_KEY):
        self.SERVICE_KEY = SERVICE_KEY