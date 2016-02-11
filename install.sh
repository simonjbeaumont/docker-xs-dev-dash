#!/bin/sh
/opt/influxdb/influx -execute 'CREATE DATABASE inforad' >/dev/null
sudo sed 's!@CWD@!'$PWD'!;s!@USER@!'$USER'!' crontab-entries > /etc/cron.d/ring3-dash
sudo cp --backup=numbered grafana/grafana.ini /etc/grafana/grafana.ini
sudo chgrp grafana /etc/grafana/grafana.ini
sudo mkdir -p /var/lib/grafana/dashboards
sudo cp --backup=numbered grafana/dash.json /var/lib/grafana/dashboards/ring3-dash.json
sudo chgrp grafana /var/lib/grafana/dashboards/ring3-dash.json
