# coding: utf-8
from parkworker3 import settings
import zmq


def emit_event(topic_filter: str, msg: str = ''):
    msg = msg.encode('utf-8')

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://%s:%s" % (settings.ZMQ_SERVER_ADDRESS, settings.ZMQ_EVENT_RECEIVER_PORT))
    socket.send_multipart([topic_filter, msg])
    socket.close()
