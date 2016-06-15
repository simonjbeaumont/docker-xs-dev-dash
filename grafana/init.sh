#!/bin/bash
set -e

STAMP="/.grafana-setup-complete"

if [ -f ${STAMP} ]; then
  echo "grafana already configured, nothing to do."
  exit 0
fi

/etc/init.d/grafana-server start

until nc localhost 3000 < /dev/null; do sleep 1; done

# create influxdb datasource
curl 'http://admin:admin@localhost:3000/api/datasources' \
    -X POST -H "Content-Type: application/json" \
    --data-binary <<DATASOURCE \
      '{
        "name":"influx",
        "type":"influxdb",
        "url":"http://localhost:8086",
        "access":"proxy",
        "isDefault":true,
        "database":"inforad",
        "user":"n/a","password":"n/a"
      }'
DATASOURCE
echo

# create extra user for light theme
curl 'http://admin:admin@localhost:3000/api/admin/users' \
    -X POST -H "Content-Type: application/json" \
    --data-binary <<DATASOURCE \
      '{
        "name":"light",
        "user":"light",
        "password":"light",
        "email":"light"
      }'
DATASOURCE
echo

# set light theme for light user
curl 'http://admin:admin@localhost:3000/api/users/2' \
    -X PUT -H "Content-Type: application/json" \
    --data-binary <<DATASOURCE \
      '{
        "name":"light",
        "user":"light",
        "password":"light",
        "email":"light",
        "theme":"light"
      }'
DATASOURCE
echo

/etc/init.d/grafana-server stop

touch ${STAMP}
