#!/bin/sh
set -e

sudo docker run --network=ee-monitor-nw -d --rm --name=ee-monitor-db --log-driver=gcplogs --log-opt gcp-log-cmd=true -v influxdb:/var/lib/influxdb ee-monitor-db
sudo docker run --network=ee-monitor-nw -d --rm --name=ee-monitor --log-driver=gcplogs  --log-opt gcp-log-cmd=true -v /home/jamesm/conf/ee-accounts.ini:/ee-monitor/conf/ee-accounts.ini ee-monitor
sudo docker run --network=ee-monitor-nw -d --rm --name=ee-monitor-api --log-driver=gcplogs  --log-opt gcp-log-cmd=true -p 5002:5002 ee-monitor-api
sudo docker run --network=ee-monitor-nw -d --rm --name=grafana  --log-driver=gcplogs --log-opt gcp-log-cmd=true -p 3000:3000 -v grafana:/var/lib/grafana grafana/grafana
