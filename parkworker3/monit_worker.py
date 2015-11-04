# coding: utf-8
import asyncio

from parkworker.const import MONIT_WORKER_HEART_BEAT_PERIOD
from parkworker.monit_worker import BaseMonitWorker
from parkworker.utils import now
from parkworker3.monits.base import Monit
from . import settings
from .event import emit_event, async_recv_pull_msg


class MonitWorker(BaseMonitWorker):
    ZMQ_SERVER_ADDRESS = settings.ZMQ_SERVER_ADDRESS
    ZMQ_WORKER_REGISTRATOR_PORT = settings.ZMQ_WORKER_REGISTRATOR_PORT

    worker_type = 'python3'

    def emit_event(self, *args, **kwargs):
        return emit_event(*args, **kwargs)

    def run(self):
        print('Worker start %s' % self.id)

        loop = asyncio.get_event_loop()
        try:
            loop.create_task(self._heart_beat())
            loop.create_task(self._process_tasks())
            loop.run_forever()
        finally:
            loop.close()

    async def _process_tasks(self):
        task_socket = self._get_task_socket()
        try:
            loop = asyncio.get_event_loop()
            while True:
                task = await async_recv_pull_msg(task_socket)
                self._register_start_task(task)
                loop.create_task(self._check(task))
        finally:
            self._emit_worker({'stop_dt': now()})
            task_socket.close()

    async def _heart_beat(self):
        while True:
            self._emit_worker()
            await asyncio.sleep(MONIT_WORKER_HEART_BEAT_PERIOD)

    async def _check(self, task):
        monit = Monit.get_monit(task['monit_name'])()
        result = await monit.async_check(
            host=task['host_address'],
            **task['options']
        )
        self._after_check(task, result)
        # print('Done check for host', task)
