#!/bin/bash
set -e

STAMP="/.influxdb-setup-complete"

if [ -f ${STAMP} ]; then
  echo "influxdb already configured, nothing to do."
  exit 0
fi

/etc/init.d/influxdb start

# wait for influxdb to respond to requests
until /opt/influxdb/influx -execute 'show databases'; do sleep 1; done
/opt/influxdb/influx -execute 'create database inforad'

/etc/init.d/influxdb stop

touch ${STAMP}
