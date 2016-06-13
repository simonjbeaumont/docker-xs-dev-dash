import sys
import requests


def db_write(db_uri, measurement, value, timestamp):
    try:
        payload = "%s value=%s %d" % (measurement, value, timestamp)
        requests.post(db_uri, data=payload)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to local influxdb failed\n")
        sys.exit(5)


def add_common_parser_args(parser):
    """
    Adds the following arguments to an argparse.ArgumentParser:
        * -n/--dry-run
    """
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Just retrieve and print the result, then exit')
