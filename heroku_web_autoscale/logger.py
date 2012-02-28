import logging

logger = logging.getLogger("heroku_web_autoscale")


ch = logging.StreamHandler()

try:
    import django
except:
    logger.setLevel(logging.WARN)
    ch.setLevel(logging.WARN)

formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
