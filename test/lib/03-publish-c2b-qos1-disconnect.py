#!/usr/bin/env python3

# Test whether a client sends a correct PUBLISH to a topic with QoS 1, then responds correctly to a disconnect.

from mosq_test_helper import *

port = mosq_test.get_lib_port()

rc = 1
keepalive = 60
connect_packet = mosq_test.gen_connect("publish-qos1-test", keepalive=keepalive)
connack_packet = mosq_test.gen_connack(rc=0)

disconnect_packet = mosq_test.gen_disconnect()

mid = 1
publish_packet = mosq_test.gen_publish("pub/qos1/test", qos=1, mid=mid, payload="message")
publish_packet_dup = mosq_test.gen_publish("pub/qos1/test", qos=1, mid=mid, payload="message", dup=True)
puback_packet = mosq_test.gen_puback(mid)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(10)
sock.bind(('', port))
sock.listen(5)

client_args = sys.argv[1:]
client = mosq_test.start_client(filename=sys.argv[1].replace('/', '-'), cmd=client_args, port=port)

try:
    (conn, address) = sock.accept()
    conn.settimeout(15)

    mosq_test.expect_packet(conn, "connect", connect_packet)
    conn.send(connack_packet)

    mosq_test.expect_packet(conn, "publish", publish_packet)
    # Disconnect client. It should reconnect.
    conn.close()

    (conn, address) = sock.accept()
    conn.settimeout(15)

    mosq_test.do_receive_send(conn, connect_packet, connack_packet, "connect")
    mosq_test.do_receive_send(conn, publish_packet_dup, puback_packet, "retried publish")
    mosq_test.expect_packet(conn, "disconnect", disconnect_packet)
    rc = 0

    conn.close()
except mosq_test.TestError:
    pass
finally:
    if mosq_test.wait_for_subprocess(client):
        print("test client not finished")
        rc=1
    sock.close()

exit(rc)
