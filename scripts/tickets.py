#!/usr/bin/env python

import sys
import time
import argparse
from jira import JIRA, JIRAError

from common import db_write
from common import add_common_parser_args

DB_URI = "http://localhost:8086/write?db=inforad"

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
        qrf = sum([issue.fields.customfield_18131 for issue in response])
        return round(qrf, 3)
    except JIRAError as exn:
        sys.stderr.write("error: Connection to JIRA failed: %s\n" % exn)
        exit(3)


def retrieve_counts(jira):
    counts = {}
    try:
        for (name, jira_filter) in QUERIES.iteritems():
            jql = "filter='%s'" % jira_filter
            response = jira.search_issues(jql, maxResults=1, fields='key',
                                          json_result=True)
            counts[name] = response['total']
    except JIRAError as exn:
        sys.stderr.write("error: Connection to JIRA failed: %s\n" % exn)
        exit(3)
    return counts


def parse_args_or_exit(argv=None):
    parser = argparse.ArgumentParser(
        description='Get number of open ring3 tickets and add to dashboard DB')
    add_common_parser_args(parser)
    return parser.parse_args(argv)


def main():
    args = parse_args_or_exit(sys.argv[1:])
    jira = JIRA({"server": JIRA_ENDPOINT})
    ticket_counts = retrieve_counts(jira)
    ticket_counts[QRF_DB_KEY] = retrieve_qrf(jira)
    if args.dry_run:
        print "Retrieved the following counts: %s" % ticket_counts
        exit(0)
    # use same timestamp for all database writes for consistent key
    tstamp = int(time.time()) * 10**9
    for (key, count) in ticket_counts.iteritems():
        db_write(DB_URI, key, count, tstamp)

if __name__ == "__main__":
    main()
