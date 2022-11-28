#!/usr/bin/env python3

from mosq_test_helper import *

port = mosq_test.get_lib_port()

rc = 1
keepalive = 5
connect_packet = mosq_test.gen_connect("publish-qos2-test", keepalive=keepalive)
connack_packet = mosq_test.gen_connack(rc=0)

disconnect_packet = mosq_test.gen_disconnect()

mid = 13423
pubcomp_packet = mosq_test.gen_pubcomp(mid)
pingreq_packet = mosq_test.gen_pingreq()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(10)
sock.bind(('', port))
sock.listen(5)

client_args = sys.argv[1:]
client = mosq_test.start_client(filename=sys.argv[1].replace('/', '-'), cmd=client_args, port=port)

try:
    (conn, address) = sock.accept()
    conn.settimeout(10)

    if mosq_test.expect_packet(conn, "connect", connect_packet):
        conn.send(connack_packet)
        conn.send(pubcomp_packet)

        if mosq_test.expect_packet(conn, "pingreq", pingreq_packet):
            rc = 0

    conn.close()
finally:
    for i in range(0, 5):
        if client.returncode != None:
            break
        time.sleep(0.1)

    if mosq_test.wait_for_subprocess(client):
        print("test client not finished")
        rc=1
    sock.close()
    if rc != 0 or client.returncode != 0:
        exit(1)

exit(rc)
