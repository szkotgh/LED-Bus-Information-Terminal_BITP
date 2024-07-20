import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("\n[%(levelname)s|%(name)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.info("ㅎㅇ")