import os
import time
import logging
from .rpiaccesspoint import AccessPoint
import json

access_point_config = {
    "wlan": "wlan0",
    "ip": "192.168.45.1",
    "netmask": "255.255.255.0",
    "ssid": "HumidityServer",
    "password": "password@123"
}


def load_config(config_path):
    try:
        with open(config_path) as access_point_config_file:
            dc = json.load(access_point_config_file)
        return dc
    except:
        return None


def start_access_point(config_path=None):
    if os.geteuid() != 0:
        logging.error("Need root rights.")
        return 1

    logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s", level=logging.DEBUG)
    if config_path is not None:
        config_json = load_config(config_path)

        if config_json is None:
            logging.error("Config loading error")
            return 1
    else:
        logging.error("AccessPoint Configuration File Not Provided, Using Defaults")
        logging.error(json.dumps(access_point_config))
        config_json = access_point_config

    access_point = AccessPoint(**config_json)

    access_point.stop()
    time.sleep(5)
    access_point.start()
