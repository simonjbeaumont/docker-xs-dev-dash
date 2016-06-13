import sys
import requests


def db_write(db_uri, measurement, value, timestamp):
    try:
        payload = "%s value=%s %d" % (measurement, value, timestamp)
        requests.post(db_uri, data=payload)
    except requests.exceptions.ConnectionError:
        sys.stderr.write("error: Connection to local influxdb failed\n")
        sys.exit(5)
