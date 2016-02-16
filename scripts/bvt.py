#!/usr/bin/env python

import sys
import time
import argparse
import urllib
import urllib2
import requests


def get_xenbuilder_url(branch, action, success):
    query_params = {
        "query": "latest",
        "format": "number",
        "product": "carbon",
        "branch": branch,
        "job": "core",
        "action": action,
        "site": "cam",
        "status": "succeeded" if success else "failed",
    }
    url_parts = (
        "https",
        "xenbuilder.uk.xensource.com",
        "/search",
        "",
        urllib.urlencode(query_params),
        "",
    )
    return urllib2.urlparse.urlunparse(url_parts)


def is_build_action_ok(branch, action):
    last_failed_url = get_xenbuilder_url(branch, action, False)
    last_passed_url = get_xenbuilder_url(branch, action, True)
    last_failed_build_num = urllib2.urlopen(last_failed_url).read().strip()
    last_passed_build_num = urllib2.urlopen(last_passed_url).read().strip()
    return (last_passed_build_num > last_failed_build_num)


def are_builds_action_ok(branch, actions):
    reduce(lambda ok, action: ok and is_build_action_ok(branch, action), actions)


def update_db(status, table):
    influx_uri = "http://localhost:8086/write?db=inforad"
    timestamp = int(time.time()) * 10**9
    try:
        data = "%s value=%d %d" % (table, (1 if status else 0), timestamp)
        requests.post(influx_uri, data=data)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to local influxdb failed")
        exit(5)


def parse_args_or_exit(argv=None):
    parser = argparse.ArgumentParser(
        description='Get the status of last build and BVT run and add to dashboard DB')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Just retrieve and print the status, then exit')
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args_or_exit(sys.argv[1:])
    build_status = are_builds_action_ok("trunk-ring3", ["xe-phase-1-build", "xe-phase-2-build"])
    bvt_status = are_builds_action_ok("trunk-ring3", ["xe-phase-1-test-ring3"])
    if args.dry_run:
        print "Build status: %s" % ("PASSED" if build_status else "FAILED")
        print "BVT status: %s" % ("PASSED" if bvt_status else "FAILED")
        exit(0)
    update_db(build_status, "build_status")
    update_db(bvt_status, "bvt_status")
