# docker-xs-dev-dash

A docker image for the Xenserver Ring3 team's information radiatory dashboard
using [InfluxDB][1] and [Grafana][2].

There are scripts to query the REST APIs of JIRA and Github to obtain open bug
counts and pull-requests respectively. These write to a database in
a locally-hosted InfluxDB. It also records other useful information like the
current build status.

This has all been packaged up into a Docker container for seamless deployment.
No need to worry about the host environment or dependencies, so long as you
have Docker.

## Usage
0. Install [Docker][3];
0. Get a Github API key (see [below][4]);
0. `make run`;
0. Profit.

This has now deployed the whole application in a container. It has mapped your
local port 80 to the container port 80 which is pointing to Grafana. So you
should be able to open up a broswer and see the dashboard at `localhost`.

## Persistent storage
The Dockerfile and Makefile have been constructed so that a "Data Volume
Container" (see `man docker-run`) is created that will persist the data in
InfluxDB across different containers/instances.

If you want to start from scratch, you can run `make purge`.

## Github Authentication
Github imposes rate-limiting on its API. The limit is significantly higher if
you autenticate your requests. The Github script supports this. The Dockerfile
will `ADD` a file containing your key to the container so that it can be used
by this script. This file must be present when you build the container in
a file called `.gh-token`.

## Development
The python scripts all supprt a `--dry-run` (or `-n`) option so that you can
try them out. If you are developing outside the container you will want to
install the python packages that the scripts use on your host (see the `pip
install` command in the Dockerfile). However, it's recommended to do your
development _inside_ the container. To enter the container use:

```sh
make shell
```

This will drop you into the container with none of the services running. If you
want them running you can execute `supervisord` as in the Dockerfile. It also
mounts the repo inside the container.

If you want to expose the InfluxDB ports then you can do so as follows:

```sh
PORTS="-p 8083:8083 -p 8086:8086" make <run|shell>
```

## Customisation for other teams
Most of the scripts to gather data have all of their parameters at the top.
E.g. `tickets.py` speifies a dictionary at the top of the file of JIRA filter
names to gather information for. To track different metrics, just edit these
scripts and run `make run` (you may want to get rid of the old data using `make
purge`).

## Importing old data
If you have some InfluxDB data to import then then you can use `make shell`
which mounts the current directory inside the container. This allows you to
place your data in the directory alongside the Makefile and from within the
container move whatever you need into `/var/opt/influxdb` which is the volume
exposed by the data volume container. **Note:** this should be done with no
other containers accessing the data volume container to avoid any corruption.

## Secondary automation
If you want to configure a machine to automatically run and display this
dashboard then there are some instructions in INSTALL.md.

[1]: https://influxdb.com/download/index.html
[2]: http://grafana.org/download/
[3]: https://docker.com
[4]: #github-authentication
