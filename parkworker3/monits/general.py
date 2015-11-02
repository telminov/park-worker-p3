# coding: utf-8
import subprocess

from parkworker.monits.base import Monit, CheckResult


class PingMonit(Monit):
    name = 'general.ping'
    description = 'Ping host checking.'

    def check(self, host, **kwargs):
        result = subprocess.run(
            ['ping', host, '-c1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        is_success = result.returncode == 0
        stdout = result.stdout.decode('utf-8')

        check_result = CheckResult(
            is_success=is_success,
            extra={'stdout': stdout},
        )
        return check_result
