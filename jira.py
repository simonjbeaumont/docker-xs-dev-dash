#!/usr/bin/env python

import sys
import time
import requests


def jql(project, priority=None):
    params = [
        "teams=xs-ring3",
        "resolution=empty",
        "project=" + project,
    ]
    if priority:
        params += ["priority=" + priority]
    return "+AND+".join(params)

queries = [
    ("CA", "Blocker"),
    ("CA", "Critical"),
    ("CA", "Major"),
    ("XOP", None),
    ("SCTX", None),
]

counts = {}
try:
    base_uri = "https://issues.citrite.net/rest/api/2/search?jql="
    for (pro, pri) in queries:
        search_uri = base_uri + jql(pro, pri)
        response = requests.get(search_uri).json()
        counts[(pro, pri)] = response['total']
except requests.exceptions.ConnectionError:
    sys.stderr.write("error: Connection to Github failed")
    sys.exit(3)
except ValueError:
    sys.stderr.write("error: Response from Github API was not JSON")
    sys.exit(4)

influx_uri = "http://localhost:8086/write?db=inforad"
timestamp = int(time.time()) * 10**9
for ((pro, pri), count) in counts.iteritems():
    pri_tag = "" if pri is None else ",priority=%s" % pri
    payload = "%s%s value=%d %d" % (pro, pri_tag, count, timestamp)
    try:
        resp = requests.post(influx_uri, data=payload)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to local influxdb failed")
        sys.exit(5)
