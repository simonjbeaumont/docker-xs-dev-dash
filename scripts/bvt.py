#!/usr/bin/env python

import sys
import time
import argparse
import urllib
import urllib2

from common import db_write

DB_URI = "http://localhost:8086/write?db=inforad"


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


def parse_args_or_exit(argv=None):
    parser = argparse.ArgumentParser(
        description='Get latest build and BVT status and add to dashboard DB')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Just retrieve and print the status, then exit')
    return parser.parse_args(argv)


def main():
    args = parse_args_or_exit(sys.argv[1:])
    build_status = is_build_action_ok("trunk-ring3", "xe-phase-1-build")
    bvt_status = is_build_action_ok("trunk-ring3", "xe-phase-1-test-ring3")
    if args.dry_run:
        print "Build status: %s" % ("PASSED" if build_status else "FAILED")
        print "BVT status: %s" % ("PASSED" if bvt_status else "FAILED")
        exit(0)
    timestamp = int(time.time()) * 10**9
    db_write(DB_URI, "build_status", (1 if build_status else 0), timestamp)
    db_write(DB_URI, "bvt_status", (1 if bvt_status else 0), timestamp)

if __name__ == "__main__":
    main()
