FROM fedora:23

RUN dnf update -qy

# InfluxDB
RUN dnf install -qy https://s3.amazonaws.com/influxdb/influxdb-0.9.4-1.x86_64.rpm
ADD ./influxdb/init.sh /init-influxdb.sh
RUN bash /init-influxdb.sh

# Grafana
RUN dnf install -qy https://grafanarel.s3.amazonaws.com/builds/grafana-2.1.3-1.x86_64.rpm
ADD ./grafana/init.sh /init-grafana.sh
RUN bash /init-grafana.sh
ADD ./grafana/grafana.ini /etc/grafana/grafana.ini
ADD ./grafana/dash.json /var/lib/grafana/dashboards/dash.json

# nginx
RUN dnf install -qy nginx
ADD ./nginx/nginx.conf /etc/nginx/nginx.conf

# supervisord
RUN dnf install -qy supervisor
ADD ./supervisord.conf /etc/supervisord.d/supervisord.conf

# Expose ports for nginx, grafana, influxdb
EXPOSE 80 3000 8083 8086

# Run
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.d/supervisord.conf"]
