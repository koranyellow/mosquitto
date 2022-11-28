#!/usr/bin/env python3

from mosq_test_helper import *

if sys.version < '2.7':
    print("WARNING: SSL not supported on Python 2.6")
    exit(0)

rc = 1

client_args = sys.argv[1:]
client = mosq_test.start_client(filename=sys.argv[1].replace('/', '-'), cmd=client_args)

if mosq_test.wait_for_subprocess(client):
    print("test client not finished")
    rc=1
else:
    rc=client.returncode

exit(rc)
