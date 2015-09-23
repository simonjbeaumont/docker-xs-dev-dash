#!/usr/bin/env python

import sys
import time
import requests

params = [
    "user:xapi-project",
    "type:pr",
    "state:open",
    "-repo:xapi-project/sm",
    "-repo:xapi-project/blktap",
]
query = "+".join(params)
search_uri = "https://api.github.com/search/issues?q=" + query

try:
    response = requests.get(search_uri).json()
except requests.exceptions.ConnectionError:
    sys.stderr.write("error: Connection to Github failed")
    sys.exit(3)
except ValueError:
    sys.stderr.write("error: Response from Github API was not JSON")
    sys.exit(4)

pull_reqs = response["items"]
urls = [pr["html_url"] for pr in pull_reqs]
repos = [url.split('/')[4] for url in urls]
counts = dict([[r, repos.count(r)] for r in set(repos)])


influx_uri = "http://localhost:8086/write?db=inforad"
tstamp = int(time.time()) * 10**9
try:
    for (repo, count) in counts.iteritems():
        data = "open_pull_requests,repo=%s value=%d %d" % (repo, count, tstamp)
        resp = requests.post(influx_uri, data=data)
    data = "total_open_pull_requests value=%d" % len(pull_reqs)
    resp = requests.post(influx_uri, data=data)
except requests.exceptions.ConnectionError:
    sys.stderr.write("error: Connection to local influxdb failed")
    sys.exit(5)
