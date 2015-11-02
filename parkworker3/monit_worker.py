# coding: utf-8
import json
import multiprocessing
import socket
import uuid
import zmq

from parkworker3 import settings
from parkworker3.event import emit_event
from parkworker3.monits.base import Monit
from parkworker3.utils import now, json_default
from parkworker3 import const


# TODO: add worker status publishing (heart beat)
class MonitWorker(multiprocessing.Process):
    id = None
    uuid = None
    created_dt = None
    host_name = None
    current_worker = None
    delete_dt = None
    tasks = None
    monit_names = None

    def setup(self, worker_id=None):
        if worker_id is None:
            self.id = self.uuid
        else:
            self.id = worker_id

        self.uuid = str(uuid.uuid4())
        self.created_dt = now()
        self.host_name = socket.gethostname()
        self.tasks = dict()
        self.monit_names = [n for n, _ in Monit.get_all_monits()]

        emit_event(const.MONIT_WORKER_EVENT, self._get_worker_json())

    def run(self):
        context = zmq.Context()

        task_socket = context.socket(zmq.PULL)
        task_socket.connect("tcp://%s:%s" % (settings.ZMQ_SERVER_ADDRESS, settings.ZMQ_MONIT_SCHEDULER_PORT))

        print('Worker start %s' % self.id)

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
            self.delete_dt = now()
            emit_event(const.MONIT_WORKER_EVENT, self._get_worker_json())

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
        emit_event(const.MONIT_WORKER_EVENT, self._get_worker_json())
        # print('_add_current_task', self._get_worker_json())

    def _rm_current_task(self, task):
        task_id = self._get_task_id(task)
        del self.tasks[task_id]
        emit_event(const.MONIT_WORKER_EVENT, self._get_worker_json())
        # print('_rm_current_task', self._get_worker_json())

    def _get_worker(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'created_dt': self.created_dt,
            'host_name': self.host_name,
            'delete_dt': self.delete_dt,
            'tasks': list(self.tasks.keys()),
            'monit_names': self.monit_names,
        }

    def _get_worker_json(self):
        worker_data = self._get_worker()
        return json.dumps(worker_data, default=json_default)

    @staticmethod
    def _get_task_id(task):
        return task['_id']['$oid']


