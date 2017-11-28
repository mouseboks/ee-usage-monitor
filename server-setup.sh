#!/bin/sh
set -e

cd ~
git clone https://github.com/mouseboks/ee-usage-monitor

cd ~/ee-usage-monitor/ee-monitor
sudo docker build -t ee-monitor .

cd ~/ee-usage-monitor/ee-monitor-db
sudo docker build -t ee-monitor-db .

cd ~
sudo docker network create --driver bridge ee-monitor-nw
sudo docker volume create influxdb
sudo docker volume create grafana

sudo docker run --network=ee-monitor-nw -d --rm --name=ee-monitor-db --log-driver=gcplogs --log-opt gcp-log-cmd=true -v influxdb:/var/lib/influxdb ee-monitor-db
sudo docker run --network=ee-monitor-nw -d --rm --name=ee-monitor --log-driver=gcplogs  --log-opt gcp-log-cmd=true -v /home/jamesm/conf/ee-accounts.ini:/ee-monitor/conf/ee-accounts.ini ee-monitor
sudo docker run --network=ee-monitor-nw -d --rm --name=grafana  --log-driver=gcplogs --log-opt gcp-log-cmd=true -p 3000:3000 -v grafana:/var/lib/grafana grafana/grafana
