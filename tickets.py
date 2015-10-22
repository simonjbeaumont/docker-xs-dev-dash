#!/usr/bin/env python

import sys
import time
import requests
import argparse
from jira import JIRA, JIRAError

queries = {
    "dc_inbox": "R3 Dash: DC Inbox",
    "CA,priority=Blocker": "R3 Dash: CA Blocker",
    "CA,priority=Critical": "R3 Dash: CA Critical",
    "CA,priority=Major": "R3 Dash: CA Major",
    "SCTX": "R3 Dash: SCTX",
    "XOP": "R3 Dash: XOP",
    "PAR": "R3 Dash: PAR",
    "Hotlist": "R3 Dash: Hotlist",
}


def retrieve_counts():
    jira = JIRA({"server": "https://issues.citrite.net"})
    counts = {}
    try:
        for (name, jira_filter) in queries.iteritems():
            jql = "filter='%s'" % jira_filter
            response = jira.search_issues(jql, maxResults=1, fields='key',
                                          json_result=True)
            counts[name] = response['total']
    except JIRAError as e:
        sys.stderr.write("error: Could not retrieve_counts from JIRA: %s" % e)
        exit(3)
    return counts


def update_db(counts):
    influx_uri = "http://localhost:8086/write?db=inforad"
    timestamp = int(time.time()) * 10**9
    try:
        for (key, count) in counts.iteritems():
            payload = "%s value=%d %d" % (key, count, timestamp)
            requests.post(influx_uri, data=payload)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to local influxdb failed")
        exit(5)


def parse_args_or_exit(argv=None):
    parser = argparse.ArgumentParser(
        description='Get number of open ring3 tickets and add to dashboard DB')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Just retrieve and print the counts, then exit')
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args_or_exit(sys.argv[1:])
    ticket_counts = retrieve_counts()
    if args.dry_run:
        print "Retrieved the following counts: %s" % ticket_counts
        exit(0)
    update_db(ticket_counts)
