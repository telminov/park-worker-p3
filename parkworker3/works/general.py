# coding: utf-8
import json
from bson import json_util
import subprocess
import asyncio
from parkworker import const
from parkworker.task_processor import TaskResult
from parkworker.asyncio.work import AsyncWork


class LocalCommandWork(AsyncWork):
    name = 'general.local_command'
    description = 'Local command work. Options: \n' \
                  ' - command. Script for running. \n' \
                  ' - args. Optional. Array with arguments for command. \n' \
                  ' - is_adapted. Optional. Is output of script adapted for park-keeper ' \
                  '(use TaskResult.get_json() output format). \n' \
                  ' - cwd. Optional. Set current working directory.'

    async def async_work(self, **kwargs):
        command = kwargs['command']
        args = kwargs.get('args', [])
        # print('LocalCommandWork', command, args)
        process = await asyncio.create_subprocess_exec(
            command, *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=kwargs.get('cwd'),
        )

        await process.wait()

        if process.returncode == 0:
            level = const.LEVEL_OK
        else:
            level = const.LEVEL_FAIL

        stdout = await process.stdout.read()

        if kwargs.get('is_adapted') and level == const.LEVEL_OK:
            parsed_stdout = json.loads(stdout.decode('utf-8'), object_hook=json_util.object_hook)
            check_result = TaskResult(**parsed_stdout)

        else:
            check_result = TaskResult(
                level=level,
                extra={'stdout': stdout.decode('utf-8')},
            )

        return check_result
