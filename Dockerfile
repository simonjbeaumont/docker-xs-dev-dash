FROM fedora:23
MAINTAINER Si Beaumont <simon.beaumont@citrix.com>

RUN dnf update -qy

# influxdb
RUN dnf install -qy https://s3.amazonaws.com/influxdb/influxdb-0.9.4-1.x86_64.rpm
ADD ./influxdb/init.sh /init-influxdb.sh
RUN bash /init-influxdb.sh

# grafana
RUN dnf install -qy https://grafanarel.s3.amazonaws.com/builds/grafana-2.1.3-1.x86_64.rpm
ADD ./grafana/init.sh /init-grafana.sh
RUN bash /init-grafana.sh
ADD ./grafana/grafana.ini /etc/grafana/grafana.ini

# nginx
RUN dnf install -qy nginx
ADD ./nginx/nginx.conf /etc/nginx/nginx.conf

# supervisord
RUN dnf install -qy supervisor
ADD ./supervisord.conf /etc/supervisord.d/supervisord.conf

# scripts to generate data
RUN dnf install -qy cronie
RUN pip install -q requests jira
ADD ./scripts/* /scripts/
ADD ./crontab-entries /etc/cron.d/data-scripts

# import grafana dashboard
ADD ./grafana/dash.json /var/lib/grafana/dashboards/dash.json

# Expose ports for nginx and grafana
EXPOSE 80 3000

# Run
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.d/supervisord.conf"]