#!/bin/sh
/opt/influxdb/influx -execute 'CREATE DATABASE inforad' >/dev/null
sed 's!@CWD@!'$PWD'!;s!@USER@!'$USER'!' crontab-entries > /etc/cron.d/ring3-dash
