# Raspberry Pi Humidity Logger

- Grafana Dashboard: `localhost:3000`
- IndexDB Dashboard: `localhost:8086`

## Setup Grafana and InfluxDB node

1. Install Raspberry OS Lite 64-bit using Raspberry Imager (https://grafana.com/tutorials/install-grafana-on-raspberry-pi/)
2. Install InfluxDB: https://docs.influxdata.com/influxdb/v2.6/install/?t=Raspberry+Pi

```bash
wget -q https://repos.influxdata.com/influxdb.key
echo '23a1c8836f0afc5ed24e0486339d7cc8f6790b83886c4c96995b88a061c5bb5d influxdb.key' | sha256sum -c && cat influxdb.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdb.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdb.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt-get update && sudo apt-get install -y influxdb2
sudo systemctl enable influxdb
sudo systemctl start influxdb
sudo systemctl status influxdb
influx setup
```

3. Install Grafana (https://grafana.com/tutorials/install-grafana-on-raspberry-pi/)

```bash
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
sudo systemctl status grafana-server
```

4. Creage InfluxDB token for Grafana: `influx auth create --org wernerfamily --all-access -d grafana`
5. Go to `hostname:3000` and log in with `admin:admin`
6. Setup InflxuDB data source in Grafana

## Setup data collection node

1. Install Raspberry OS Lite 64-bit using Raspberry Imager (https://grafana.com/tutorials/install-grafana-on-raspberry-pi/)

### Use the setup script
2. Run `curl 'https://raw.githubusercontent.com/benediktwerner/humidity-logger/master/setup-data-node.py' | python3`

### or do it manually
2. Install sense-hat lib: `sudo apt-get install sense-hat`
3. Install influxdb lib: `sudo apt-get install -y python3-pip && pip install 'influxdb-client[ciso]'`
4. Copy `logger.py` to `~/humidity-logger/logger.py`
5. Copy `config.toml.example` to `~/humidity-logger/config.toml` and adjust the values
  - You can create an InfluxDB token via the InfluxDB UI at `http://hostname:8086` or via `influx auth create --org wernerfamily --write-buckets`
6.  Copy `humidity-logger.service` to `/etc/systemd/system/`
7.  Enable and start the service:
```bash
sudo systemctl enable humidity-logger
sudo systemctl start humidity-logger
```
