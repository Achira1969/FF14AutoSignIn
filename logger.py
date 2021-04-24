import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)
