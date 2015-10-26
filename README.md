# Ring3 Dashboard

This repository is a collection of scripts and configuration files to bootstrap
the team dashboard using InfluxDB and Grafana.

There scripts to query the REST APIs of JIRA and Github to obtain open bug
counts and pull-requests respectively. These write to a database in
a locally-hosted InfluxDB.

## Installation
0. Install python-requests library[3];
0. Install InfluxDB[1] and Grafana[2];
0. Run `./install.sh` to create the contab entries and the InfluxDB database;
0. Import `grafana-dash` to the local instance of Grafana;
0. Profit.

## Github Authentication
Github imposes rate-limiting on its API. The limit is significantly higher if
you autenticate your requests. The Github script supports this. To enable it
you can add the following line to your crontab so that the token is exported in
the environment for the Github script:

```diff
+ GH_TOKEN=<gh-token>
...
```

[1]: https://influxdb.com/download/index.html
[2]: http://grafana.org/download/
[3]: http://docs.python-requests.org/en/latest/
