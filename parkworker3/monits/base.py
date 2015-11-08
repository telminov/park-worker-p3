# coding: utf-8
import parkworker.monits.base


class Monit(parkworker.monits.base.Monit):

    def start(self, host, **kwargs):
        raise Exception('Use async_start() method instead.')

    def check(self, host, **kwargs):
        raise Exception('Use async_check() method instead.')

    async def async_start(self, host, **kwargs):
        try:
            result = await self.async_check(host, **kwargs)
        except Exception as ex:
            result = self._get_exp_result(ex)
        return result

    async def async_check(self, host: str, **kwargs) -> parkworker.monits.base.CheckResult:
        raise NotImplemented()
