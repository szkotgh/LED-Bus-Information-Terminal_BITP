import os
import module.utils as utils
import tempfile

class SpeakerManager:
    def __init__(self):
        self.logger = utils.create_logger('speaker_manager')
        self.tmp_path = tempfile.mkdtemp()
        self.logger.info(f"tmp_path : {self.tmp_path}")
    