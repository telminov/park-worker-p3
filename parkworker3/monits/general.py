# coding: utf-8
import subprocess
import asyncio

from parkworker.monits.base import CheckResult
from parkworker3.monits.base import Monit


class PingMonit(Monit):
    name = 'general.ping'
    description = 'Ping host checking.'

    async def async_check(self, host: str, **kwargs):
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
        return check_result
