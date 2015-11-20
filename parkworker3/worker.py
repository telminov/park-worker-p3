# coding: utf-8
from parkworker.asyncio.worker import AsyncBaseWorker
from . import settings
from .event import emit_event, async_recv_pull_msg


class Worker(AsyncBaseWorker):
    ZMQ_SERVER_ADDRESS = settings.ZMQ_SERVER_ADDRESS
    ZMQ_WORKER_REGISTRATOR_PORT = settings.ZMQ_WORKER_REGISTRATOR_PORT

    worker_type = 'python3'

    def emit_event(self, *args, **kwargs):
        return emit_event(*args, **kwargs)

    async def async_recv_pull_msg(self, *args, **kwargs) -> dict:
        return await async_recv_pull_msg(*args, **kwargs)
