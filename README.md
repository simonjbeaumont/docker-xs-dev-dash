# Ring3 Dashboard

This repository is a collection of scripts and configuration files to bootstrap
the team dashboard using InfluxDB and Grafana.

There scripts to query the REST APIs of JIRA and Github to obtain open bug
counts and pull-requests respectively. These write to a database in
a locally-hosted InfluxDB.

## Installation
0. Install InfluxDB[1] and Grafana[2];
0. Run `./install.sh` to create the contab entries and the InfluxDB database;
0. Import `grafana-dash` to the local instance of Grafana;
0. Profit.

[1]: https://influxdb.com/download/index.html
[2]: http://grafana.org/download/
