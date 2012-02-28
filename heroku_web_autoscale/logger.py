import logging

logger = logging.getLogger("heroku_web_autoscale")
logger.setLevel(logging.WARN)

ch = logging.StreamHandler()
ch.setLevel(logging.WARN)

formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
