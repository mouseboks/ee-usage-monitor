#!/bin/sh
set -e

cd ~
git clone https://github.com/mouseboks/ee-usage-monitor

cd ~/ee-usage-monitor/ee-monitor
sudo docker build -t ee-monitor .

cd ~/ee-usage-monitor/ee-monitor-db
sudo docker build -t ee-monitor-db .

cd ~/ee-usage-monitor/ee-monitor-api
sudo docker build -t ee-monitor-api .

cd ~
sudo docker network create --driver bridge ee-monitor-nw
sudo docker volume create influxdb
sudo docker volume create grafana

