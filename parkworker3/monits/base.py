# coding: utf-8
import parkworker.monits.base


class Monit(parkworker.monits.base.Monit):
    def check(self, host, **kwargs):
        raise Exception('Use async_check() method instead.')

    async def async_check(self, host: str, **kwargs) -> parkworker.monits.base.CheckResult:
        raise NotImplemented()
