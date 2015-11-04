# coding: utf-8
import subprocess
import asyncio
import aiohttp

from parkworker.monits.base import CheckResult
from parkworker3.monits.base import Monit


class PingMonit(Monit):
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

        is_success = process.returncode == 0
        stdout = await process.stdout.read()
        check_result = CheckResult(
            is_success=is_success,
            extra={'stdout': stdout.decode('utf-8')},
        )

        # import random
        # await asyncio.sleep(random.randint(5, 10))
        # print('End ping', host)
        return check_result


class HttpMonit(Monit):
    name = 'general.http'
    description = 'Http checking.'

    async def async_check(self, host: str, **kwargs):
        url = kwargs['url']
        print('Start http', host, url)

        extra = {}
        is_success = True
        async with aiohttp.get(url) as response:
            extra['is_http_status_ok'] = response.status == kwargs.get('http_status', 200)
            if not extra['is_http_status_ok']:
                extra['http_status'] = response.status
                is_success = False

            if kwargs.get('contains'):
                content = await response.read()
                content = content.decode('utf-8')
                extra['is_contains_ok'] = kwargs['contains'] in content
                if not extra['is_contains_ok']:
                    extra['content'] = content
                    is_success = False

        check_result = CheckResult(
            is_success=is_success,
            extra=extra,
        )

        return check_result