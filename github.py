#!/usr/bin/env python

import os
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
additional_repos = [
    "xenserver/perf-tools",
    "xenserver/rrdd-plugins",
    "xenserver/gpumon",
    "xenserver/xsiostat",
    "xenserver/xen-api-backports",
    "xenserver/buildroot",
    "xenserver/xen-api-libs-specs",
    "xenserver/xen-api",
    "xenserver/xenserver-build-env",
    "xenserver/planex",
    "xenserver/xs-pull-request-build-scripts",
    "xenserver/xen-api-libs",
    "xenserver/filesystem-summarise",
]
additional_repo_params = ["repo:" + repo for repo in additional_repos]
query = "+".join(params + additional_repo_params)

headers = {}
if 'GH_TOKEN' in os.environ:
    headers['Authorization'] = "token %s" % os.environ['GH_TOKEN']

search_uri = "https://api.github.com/search/issues?q=" + query

repos_uri = "https://api.github.com/orgs/xapi-project/repos"


def get_all_responses(uri, headers):
    r = requests.get(uri, headers=headers)
    responses = [r]
    while 'next' in r.links:
        r = requests.get(r.links['next']['url'], headers=headers)
        responses.append(r)
    return responses


if __name__ == "__main__":
    try:
        repo_responses = get_all_responses(repos_uri, headers)
        pull_responses = get_all_responses(search_uri, headers)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to Github failed")
        sys.exit(3)
    except ValueError:
        sys.stderr.write("error: Response from Github API was not JSON")
        sys.exit(4)

    repos_json = sum([r.json() for r in repo_responses], [])
    counts = {r['full_name']: 0 for r in repos_json}
    counts.update({r: 0 for r in additional_repos})
    pull_reqs = sum([r.json()['items'] for r in pull_responses], [])
    urls = [pr["html_url"] for pr in pull_reqs]
    repos = ['/'.join(url.split('/')[3:5]) for url in urls]
    for repo in repos:
        counts[repo] += 1

    influx_uri = "http://localhost:8086/write?db=inforad"
    tstamp = int(time.time()) * 10**9
    try:
        for (repo, count) in counts.iteritems():
            data = "open_pull_requests,repo=%s value=%d %d" % (repo, count,
                                                               tstamp)
            resp = requests.post(influx_uri, data=data)
        data = "total_open_pull_requests value=%d" % len(pull_reqs)
        resp = requests.post(influx_uri, data=data)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to local influxdb failed")
        sys.exit(5)
