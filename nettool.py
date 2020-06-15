import logging
import random
import shutil
import time

import requests

logger = logging.getLogger(__name__)

RANDOM_WAITING_TIME = 5000


def get(url, params):
    """
    send get request
    :param url: destination url
    :param params: parameters to send
    :return: response as json data
    """
    try:
        random_sleep_milliseconds = float(random.randint(0, RANDOM_WAITING_TIME)) / float(1000)
        logger.debug("sleep in %f seconds", random_sleep_milliseconds)
        time.sleep(random_sleep_milliseconds)
        r = requests.get(url, params, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        })
        return r.json()
    except Exception as ex:
        logger.error(ex)
    return None
