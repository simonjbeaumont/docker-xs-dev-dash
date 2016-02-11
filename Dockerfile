FROM fedora:23

RUN dnf update -qy

# InfluxDB
RUN dnf install -qy https://s3.amazonaws.com/influxdb/influxdb-0.9.4-1.x86_64.rpm
RUN /opt/influxdb/influx -execute 'create database inforad' || true

# Grafana
RUN dnf install -qy https://grafanarel.s3.amazonaws.com/builds/grafana-2.1.3-1.x86_64.rpm
ADD ./grafana/config.js /usr/share/grafana/config.js
ADD ./grafana/grafana.ini /etc/grafana/grafana.conf

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
