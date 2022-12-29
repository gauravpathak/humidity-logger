#!/usr/bin/env python3

from dataclasses import dataclass
import time, toml, os, sys
from sense_hat import SenseHat
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision


CONFIG_FILE = "config.toml"


@dataclass
class Config:
    room: str
    sampling_period: int  # in seconds
    influx_url: str  # "http://localhost:8086"
    influx_org: str  # "wernerfamily"
    influx_token: str
    influx_bucket: str  # "humidity"


def log(*args):
    print(*args, file=sys.stderr)


with open(os.path.join(os.path.dirname(__file__), CONFIG_FILE)) as f:
    vals = {key.lower(): val for key, val in toml.load(f).items()}
    config = Config(**vals)


sense = SenseHat()
client = InfluxDBClient(config.influx_url, config.influx_token, org=config.influx_org)
write_api = client.write_api(SYNCHRONOUS)


def get_point():
    return (
        Point("humidity")
        .tag("sensor", config.room)
        .field("humidity", float(sense.get_humidity()))
        .field("pressure", float(sense.get_pressure()))
        .field(
            "temperature_from_humidity", float(sense.get_temperature_from_humidity())
        )
        .field(
            "temperature_from_pressure", float(sense.get_temperature_from_pressure())
        )
        .time(int(time.time()), WritePrecision.S)
    )


log("Initial measurement:", get_point())  # First measurement is often a bit weird
time.sleep(1)
log("Second measurement:", get_point())
log("Started...")

while True:
    p = get_point()
    log(p)
    write_api.write(config.influx_bucket, config.influx_org, p)
    time.sleep(config.sampling_period)
