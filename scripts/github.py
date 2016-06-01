#!/usr/bin/env python

import os
import sys
import time
import datetime
import requests
import argparse

DB_URI = "http://localhost:8086/write?db=inforad"

GITHUB_ORG = "xapi-project"

EXCLUDE_REPOS = [
    "xapi-project/sm",
    "xapi-project/blktap",
    "xapi-project/xapi-storage-datapath-plugins",
    "xapi-project/xen-api-sdk",
]

ADDITIONAL_REPOS = [
    "xenserver/perf-tools",
    "xenserver/rrdd-plugins",
    "xenserver/gpumon",
    "xenserver/xsiostat",
    "xenserver/xen-api-backports",
    "xenserver/buildroot",
    "xenserver/xen-api-base-specs",
    "xenserver/xen-api-libs-specs",
    "xenserver/xen-api",
    "xenserver/xenserver-build-env",
    "xenserver/planex",
    "xenserver/xs-pull-request-build-scripts",
    "xenserver/xen-api-libs",
    "xenserver/filesystem-summarise",
]


def query_all():
    base_params = [
        "user:" + GITHUB_ORG,
        "type:pr",
        "state:open",
    ]
    exclude_repo_params = ["-repo:" + repo for repo in EXCLUDE_REPOS]
    additional_repo_params = ["repo:" + repo for repo in ADDITIONAL_REPOS]
    return "+".join(base_params + exclude_repo_params + additional_repo_params)


def query_only_inactive(query):
    exclude_blocked_param = "-label:blocked"
    now_time = datetime.datetime.now()
    if now_time.isoweekday() == 1:  # today is Mon, last working day is Fri
        before_time = now_time - datetime.timedelta(days=3)
    elif now_time.isoweekday() == 7:  # today is Sun, last working day is Fri
        before_time = now_time - datetime.timedelta(days=2)
    else:  # today is Tue-Sat, last working day is yesterday
        before_time = now_time - datetime.timedelta(days=1)
    before_param = "-updated:>%s" % before_time.strftime("%Y-%d-%dT%H:%M:%S")
    return "+".join([query, exclude_blocked_param, before_param])


repos_uri = "https://api.github.com/orgs/xapi-project/repos"


def search_uri(query):
    return "https://api.github.com/search/issues?q=" + query


def get_all_responses(uri, headers):
    try:
        r = requests.get(uri, headers=headers)
        if not r.ok:
            sys.stderr.write("error: API request failed: %d (%s)" %
                             (r.status_code, r.reason))
            sys.stderr.write("response: %s" % r.text)
            sys.exit(6)
        responses = [r]
        while 'next' in r.links:
            r = requests.get(r.links['next']['url'], headers=headers)
            responses.append(r)
        return responses
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to Github failed")
        sys.exit(3)
    except ValueError:
        sys.stderr.write("error: Response from Github API was not JSON")
        sys.exit(4)


def retreive_counts(query):
    headers = {}
    if 'GH_TOKEN' in os.environ:
        headers['Authorization'] = "token %s" % os.environ['GH_TOKEN']
    repo_responses = get_all_responses(repos_uri, headers)
    pull_responses = get_all_responses(search_uri(query), headers)
    repos_json = sum([r.json() for r in repo_responses], [])
    counts = {r['full_name']: 0 for r in repos_json}
    counts.update({r: 0 for r in ADDITIONAL_REPOS})
    pull_reqs = sum([r.json()['items'] for r in pull_responses], [])
    urls = [pr["html_url"] for pr in pull_reqs]
    repos = ['/'.join(url.split('/')[3:5]) for url in urls]
    for repo in repos:
        counts[repo] += 1
    return counts


def db_write(db_uri, measurement, value, timestamp):
    try:
        payload = "%s value=%s %d" % (measurement, value, timestamp)
        requests.post(db_uri, data=payload)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to local influxdb failed")
        sys.exit(5)


def parse_args_or_exit(argv=None):
    parser = argparse.ArgumentParser(
        description='Add number of open ring3 pull-requests to dashboard DB')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Just retrieve and print the counts, then exit')
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args_or_exit(sys.argv[1:])
    counts = retreive_counts(query_all())
    total = sum(counts.values())
    if args.dry_run:
        print "Retrieved the following counts: %s" % counts
        print "Total: %d" % total
        exit(0)
    # use same timestamp for all database writes for consistent key
    tstamp = int(time.time()) * 10**9
    for (repo, count) in counts.iteritems():
        db_write(DB_URI, "open_pull_requests,repo=%s" % repo, count, tstamp)
    db_write(DB_URI, "total_open_pull_requests", total, tstamp)
