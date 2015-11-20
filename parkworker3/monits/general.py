# coding: utf-8
import subprocess
import asyncio
import aiohttp
from parkworker import const
from parkworker.task_processor import TaskResult
from parkworker.asyncio.monit import AsyncMonit


class PingMonit(AsyncMonit):
    name = 'general.ping'
    description = 'Ping host checking.'

    async def async_check(self, host: str, **kwargs):
        # print('Start ping', host)
        process = await asyncio.create_subprocess_exec(
            'ping', host, '-c1',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        await process.wait()

        if process.returncode == 0:
            level = const.LEVEL_OK
        else:
            level = const.LEVEL_FAIL

        stdout = await process.stdout.read()
        check_result = TaskResult(
            level=level,
            extra={'stdout': stdout.decode('utf-8')},
        )

        # import random
        # await asyncio.sleep(random.randint(5, 10))
        # print('End ping', host)
        return check_result


class HttpMonit(AsyncMonit):
    name = 'general.http'
    description = 'Http checking. Options: \n' \
                  ' - protocol. Default "http". \n' \
                  ' - port. Default 80. \n' \
                  ' - path. Default "/". \n' \
                  ' - http_status. Default 200. \n' \
                  ' - contains. Optional. If defined, returned content will be checked on containing text.'

    async def async_check(self, host: str, **kwargs):
        protocol = kwargs.get('protocol', 'http')
        port = kwargs.get('port', '80')
        path = kwargs.get('path', '/')
        url = '%s://%s:%s%s' % (protocol, host, port, path)
        print('Start http', host, url)

        extra = {'url': url}
        level = const.LEVEL_OK
        async with aiohttp.get(url) as response:
            extra['is_http_status_ok'] = response.status == kwargs.get('http_status', 200)
            if not extra['is_http_status_ok']:
                extra['http_status'] = response.status
                level = const.LEVEL_FAIL

            if kwargs.get('contains'):
                content = await response.read()
                content = content.decode('utf-8')
                extra['is_contains_ok'] = kwargs['contains'] in content
                if not extra['is_contains_ok']:
                    extra['content'] = content
                    level = const.LEVEL_FAIL

        check_result = TaskResult(
            level=level,
            extra=extra,
        )

        return check_result
