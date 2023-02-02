from dataclasses import dataclass
import toml
from access_point_routines import wifi_access_point
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt

mqtt_broker_address = "192.168.45.1"
MQTT_TOPIC_TEMPERATURE = "temp"
MQTT_TOPIC_HUMIDITY = "humidity"

rx_temp = None
rx_humid = None

@dataclass
class Config:
    room: str
    sampling_period: int  # in seconds
    influx_url: str  # "http://localhost:8086"
    influx_org: str  # "wernerfamily"
    influx_token: str
    influx_bucket: str  # "humidity"

    @classmethod
    def load(cls):
        with open("config.toml") as toml_config:
            vals = {key.lower(): val for key, val in toml.load(toml_config).items()}
            toml_config.close()
            return cls(**vals)


def write_to_influx_bucket(config=None, rx_temp=None, rx_humidity=None):
    if config is None:
        config = Config.load()
    influx_client = InfluxDBClient(config.influx_url, config.influx_token, org=config.influx_org)
    point = Point("Humidity").tag("Sensor", config.room).field("Temp", rx_temp).field("Humidity", rx_humidity)
    influx_client_wr_api = influx_client.write_api(SYNCHRONOUS)
    influx_client_wr_api.write(config.influx_bucket, config.influx_org, record=point)


def on_connect(mqtt_client, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqtt_client, obj, msg):
    global rx_temp
    global rx_humid

    print("Message Topic: " + msg.topic + " Message QoS: " + str(msg.qos) + " Data: " + str(msg.payload.decode()))
    if "temp" in msg.topic:
        rx_temp = float(msg.payload.decode())
    elif "humid" in msg.topic:
        rx_humid = float(msg.payload.decode())
    else:
        print("Unknown Topic")
    print("Temp: ", rx_temp, " Humid: ", rx_humid)
    write_to_influx_bucket(rx_temp=rx_temp, rx_humidity=rx_humid)


def on_publish(mqtt_client, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqtt_client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " Granted QoS: " + str(granted_qos))


def on_log(mqtt_client, obj, level, string):
    print(string)


def main():
    config = Config.load()
    wifi_access_point.start_access_point()
    mqttc = mqtt.Client("P1")
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.connect(mqtt_broker_address)
    mqttc.subscribe(MQTT_TOPIC_TEMPERATURE)
    mqttc.subscribe(MQTT_TOPIC_HUMIDITY)
    mqttc.loop_forever()


if __name__ == "__main__":
    main()
