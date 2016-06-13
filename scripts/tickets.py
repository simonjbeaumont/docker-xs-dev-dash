#!/usr/bin/env python

import sys
import time
import requests
import argparse
from jira import JIRA, JIRAError

JIRA_ENDPOINT = "https://issues.citrite.net"

QUERIES = {
    "dc_inbox": "R3 Dash: DC Inbox",
    "CA,priority=Blocker": "R3 Dash: CA Blocker",
    "CA,priority=Critical": "R3 Dash: CA Critical",
    "CA,priority=Major": "R3 Dash: CA Major",
    "CA,priority=Minor": "R3 Dash: CA Minor",
    "CA,priority=Trivial": "R3 Dash: CA Trivial",
    "CA,priority=Unset": "R3 Dash: CA Unset",
    "CA,priority=Non-bug": "R3 Dash: CA Non-bug",
    "CA,priority=Dundee-BCM": "R3 Dash: Dundee BCM",
    "SCTX": "R3 Dash: SCTX",
    "XOP": "R3 Dash: XOP",
    "PAR": "R3 Dash: PAR",
    "Hotlist": "R3 Dash: Hotlist",
    "Staging": "R3 Dash: Staging",
}

QRF_DB_KEY = "CA,priority=QRF"
QRF_JIRA_FILTER = "R3 Dash: Unresolved CA"


def retrieve_qrf(jira):
    try:
        jql = "filter='%s'" % QRF_JIRA_FILTER
        # The field DRV is custom and has custom field ID 18131 (urgh)
        response = jira.search_issues(jql, maxResults=False,
                                      fields="customfield_18131")
        return sum([issue.fields.customfield_18131 for issue in response])
        exit(1)
    except JIRAError as e:
        sys.stderr.write("error: Could not retrieve_qrf from JIRA: %s" % e)
        exit(3)


def retrieve_counts(jira):
    counts = {}
    try:
        for (name, jira_filter) in QUERIES.iteritems():
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
            payload = "%s value=%.3f %d" % (key, count, timestamp)
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
    jira = JIRA({"server": JIRA_ENDPOINT})
    ticket_counts = retrieve_counts(jira)
    ticket_counts[QRF_DB_KEY] = retrieve_qrf(jira)
    if args.dry_run:
        print "Retrieved the following counts: %s" % ticket_counts
        exit(0)
    update_db(ticket_counts)
