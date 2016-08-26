FROM fedora:23
MAINTAINER Si Beaumont <simon.beaumont@citrix.com>

# Update in a separate layer to minimize churn in the base image.
# Clean up afterwards to reduce image size.
RUN dnf update -qy \
 && dnf clean all

# Install base dependencies in one layer and clean up afterwards to
# reduce image size
RUN dnf install -qy \
       nginx \
       supervisor \
       cronie \
       nmap-ncat \
 && dnf clean all

RUN pip install --no-cache-dir -q \
       requests \
       jira \
       pep8 \
       pylint \
       demjson

# Install influxdb and grafana in a separate layer so they can be upgraded
# without rebuilding the preceding layers.
RUN dnf install -qy \
       https://s3.amazonaws.com/influxdb/influxdb-0.9.4-1.x86_64.rpm \
       https://grafanarel.s3.amazonaws.com/builds/grafana-2.1.3-1.x86_64.rpm \
 && dnf clean all

# influxdb
ADD ./influxdb/init.sh /init-influxdb.sh
RUN bash /init-influxdb.sh

# grafana
ADD ./grafana/init.sh /init-grafana.sh
RUN bash /init-grafana.sh
ADD ./grafana/grafana.ini /etc/grafana/grafana.ini

# nginx config
ADD ./nginx/nginx.conf /etc/nginx/nginx.conf

# supervisord
ADD ./supervisord.conf /etc/supervisord.d/supervisord.conf

# scripts to generate data
ADD ./scripts/ /scripts/
ADD ./crontab-entries /etc/cron.d/data-scripts

# import grafana dashboard
ADD ./grafana/dash.json /var/lib/grafana/dashboards/dash.json

# expose ports for nginx (grafana)
EXPOSE 80

# expose influxdb data for creating a data volume container
VOLUME /var/opt/influxdb/

# run
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.d/supervisord.conf"]
