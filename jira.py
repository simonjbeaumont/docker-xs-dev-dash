#!/usr/bin/env python

import sys
import time
import requests
from jira import JIRA

queries = {
    "dc_inbox": "R3 Dash: DC Inbox",
    "CA,priority=Blocker": "R3 Dash: CA Blocker",
    "CA,priority=Critical": "R3 Dash: CA Critical",
    "CA,priority=Major": "R3 Dash: CA Major",
    "SCTX": "R3 Dash: SCTX",
    "XOP": "R3 Dash: XOP",
    "PAR": "R3 Dash: PAR",
}

# uses ~/.netrc for credentials
jira = JIRA({"server": "https://issues.citrite.net"})

counts = {}
try:
    for (name, filter) in queries.iteritems():
        jql = "filter='%s'" % filter
        response = jira.search_issues(jql, fields='key', json_result=True)
        counts[name] = response['total']
except requests.exceptions.ConnectionError:
    sys.stderr.write("error: Connection to JIRA failed")
    sys.exit(3)
except ValueError:
    sys.stderr.write("error: Response from JIRA API was not JSON")
    sys.exit(4)

influx_uri = "http://localhost:8086/write?db=inforad"
timestamp = int(time.time()) * 10**9
try:
    for (key, count) in counts.iteritems():
        payload = "%s value=%d %d" % (key, count, timestamp)
        resp = requests.post(influx_uri, data=payload)
except requests.exceptions.ConnectionError:
    sys.stderr.write("error: Connection to local influxdb failed")
    sys.exit(5)
