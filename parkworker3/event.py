# coding: utf-8
import asyncio

from . import settings
import zmq


def emit_event(topic_filter: str, msg: str = ''):
    msg = msg.encode('utf-8')

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://%s:%s" % (settings.ZMQ_SERVER_ADDRESS, settings.ZMQ_EVENT_RECEIVER_PORT))
    socket.send_multipart([topic_filter, msg])
    socket.close()


async def async_recv_pull_msg(subscriber_socket: zmq.Socket) -> str:
    while True:
        try:
            msg = subscriber_socket.recv_json(flags=zmq.NOBLOCK)
            return msg
        except zmq.error.Again:
            pass
        await asyncio.sleep(0.1)
