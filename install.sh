#!/bin/sh
(crontab -l; sed 's!@CWD@!'$PWD'!' crontab-entries) | awk '!x[$0]++' | crontab -
/opt/influxdb/influx -execute 'CREATE DATABASE inforad' >/dev/null
