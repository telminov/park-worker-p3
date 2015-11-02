# coding: utf-8
import time
import json
import multiprocessing
import socket
import uuid
import zmq

from parkworker3 import settings
from parkworker3.const import MONIT_WORKER_HEART_BEAT_PERIOD
from parkworker3.event import emit_event
from parkworker3.monits.base import Monit
from parkworker3.utils import now, json_default
from parkworker3 import const


class MonitWorker(multiprocessing.Process):
    id = None
    uuid = None
    created_dt = None
    host_name = None
    tasks = None

    def setup(self, worker_id=None):
        if worker_id is None:
            self.id = self.uuid
        else:
            self.id = worker_id

        self.uuid = str(uuid.uuid4())
        self.created_dt = now()
        self.host_name = socket.gethostname()
        self.tasks = dict()

        monit_names = [n for n, _ in Monit.get_all_monits()]
        self._emit_worker({'monit_names': monit_names})

    def run(self):
        context = zmq.Context()

        task_socket = context.socket(zmq.PULL)
        task_socket.connect("tcp://%s:%s" % (settings.ZMQ_SERVER_ADDRESS, settings.ZMQ_MONIT_SCHEDULER_PORT))

        print('Worker start %s' % self.id)

        heart_beat_process = multiprocessing.Process(target=self._heart_beat)
        heart_beat_process.daemon = True
        heart_beat_process.start()

        try:
            while True:
                task_json = task_socket.recv_json()
                task = json.loads(task_json)
                monit_name = task['monit_name']
                host_address = task['host_address']
                task_options = task['options']

                print("Worker %s. Received request: %s for %s" % (self.id, monit_name, host_address))

                monit_class = Monit.get_monit(monit_name)
                monit = monit_class()

                self._register_start_task(task)

                result = monit.check(
                    host=host_address,
                    options=task_options,
                )

                self._register_complete_task(task, result)

                # get new monitoring results
                emit_event(const.MONIT_STATUS_EVENT, json.dumps(task, default=json_default))
        finally:
            self._emit_worker({'stop_dt': now()})

    def _register_start_task(self, task):
        self._add_current_task(task)

        task['start_dt'] = now()
        task['worker'] = self._get_worker()
        emit_event(const.MONIT_TASK_EVENT, json.dumps(task, default=json_default))

    def _register_complete_task(self, task, result):
        self._rm_current_task(task)
        task['result'] = result.get_dict()
        emit_event(const.MONIT_TASK_EVENT, json.dumps(task, default=json_default))

    def _add_current_task(self, task):
        task_id = self._get_task_id(task)
        self.tasks[task_id] = task
        self._emit_worker({'tasks': list(self.tasks.keys())})

    def _rm_current_task(self, task):
        task_id = self._get_task_id(task)
        del self.tasks[task_id]
        self._emit_worker({'tasks': list(self.tasks.keys())})

    def _get_worker(self):
        return {
            'id': str(self.id),
            'uuid': self.uuid,
            'created_dt': self.created_dt,
            'host_name': self.host_name,
        }

    def _emit_worker(self, data: dict = None):
        worker_data = {
            'main': self._get_worker(),
            'heart_beat_dt': now(),
        }

        if data:
            worker_data.update(data)

        worker_data_json = json.dumps(worker_data, default=json_default)
        emit_event(const.MONIT_WORKER_EVENT, worker_data_json)

    def _heart_beat(self):
        while True:
            self._emit_worker()
            time.sleep(MONIT_WORKER_HEART_BEAT_PERIOD)

    @staticmethod
    def _get_task_id(task):
        return task['_id']['$oid']


