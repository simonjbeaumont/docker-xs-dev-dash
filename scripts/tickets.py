#!/usr/bin/env python

import sys
import time
import argparse
from jira import JIRA, JIRAError

from common import db_write
from common import add_common_parser_args

DB_URI = "http://localhost:8086/write?db=inforad"

JIRA_ENDPOINT = "https://issues.citrite.net"

COUNT_QUERIES = {
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

KEY_FIELD = "key"
DRV_FIELD = "customfield_18131"


def retrieve_issues(jira, jira_filter, fields, limit=None):
    try:
        jql = "filter='%s'" % jira_filter
        max_results = False if limit is None else limit
        if isinstance(fields, list):
            fields = ",".join(fields)
        return jira.search_issues(jql, maxResults=max_results, fields=fields)
    except JIRAError as exn:
        sys.stderr.write("error: Connection to JIRA failed: %s\n" % exn)
        exit(3)


def retrieve_issue_count(jira, jira_filter):
    issues = retrieve_issues(jira, jira_filter, fields=[KEY_FIELD], limit=1)
    return issues.total


def retrieve_qrf(jira):
    issues = retrieve_issues(jira, QRF_JIRA_FILTER, fields=[DRV_FIELD])
    qrf = sum([getattr(issue.fields, DRV_FIELD) for issue in issues])
    return round(qrf, 3)


def parse_args_or_exit(argv=None):
    parser = argparse.ArgumentParser(
        description='Get number of open ring3 tickets and add to dashboard DB')
    add_common_parser_args(parser)
    return parser.parse_args(argv)


def main():
    args = parse_args_or_exit(sys.argv[1:])
    jira = JIRA({"server": JIRA_ENDPOINT})
    values = {}
    for (db_key, jira_filter) in COUNT_QUERIES.iteritems():
        values[db_key] = retrieve_issue_count(jira, jira_filter)
    values[QRF_DB_KEY] = retrieve_qrf(jira)
    if args.dry_run:
        print "Retrieved the following values: %s" % values
        exit(0)
    # use same timestamp for all database writes for consistent key
    tstamp = int(time.time()) * 10**9
    for (key, value) in values.iteritems():
        db_write(DB_URI, key, value, tstamp)

if __name__ == "__main__":
    main()
