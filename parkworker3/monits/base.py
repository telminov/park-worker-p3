# coding: utf-8
import datetime
from abc import ABCMeta, abstractmethod
import os
from typing import Dict
import sys

from parkworker3.utils import now


class DuplicatedMonitNameException(Exception):
    pass


class CheckResult:
    def __init__(self, is_success: bool, dt: datetime = None, extra: dict = None):
        self.is_success = is_success
        self.extra = extra
        self.dt = dt or now()

    def get_dict(self):
        return {
            'is_success': self.is_success,
            'extra': self.extra,
            'dt': self.dt,
        }


class Monit(metaclass=ABCMeta):
    name = None
    description = None

    @abstractmethod
    def check(self, host: str, **kwargs) -> CheckResult:
        pass

    @classmethod
    def get_monit(cls, name: str) -> 'Monit':
        monits = cls.get_all_monits()
        for monit_name, monit_module in monits:
            if name == monit_name:
                return monit_module

    @classmethod
    def get_all_monits(cls) -> Dict[str, 'Monit']:
        if not hasattr(cls, '_monits'):
            monits = {}

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            for module_path in os.listdir(base_dir + '/monits'):
                if not module_path.endswith('.py'):
                    continue

                module_name = os.path.splitext(module_path)[0]
                module_full_name = 'parkworker3.monits.%s' % module_name
                __import__(module_full_name)
                monit_module = sys.modules[module_full_name]
                for module_item in monit_module.__dict__.values():
                    if type(module_item) is ABCMeta \
                            and issubclass(module_item, Monit) \
                            and module_item is not Monit:
                        monits.setdefault(module_item.name, []).append(module_item)

            # check no duplicated names
            for monit_name, monit_modules in monits.items():
                if len(monit_modules) > 1:
                    raise DuplicatedMonitNameException('Modules %s have same name "%s"' % (
                        ' and '.join(map(str, monit_modules)),
                        monit_name
                    ))

            # create immutable list of modules
            cls._monits = tuple([(monit_name, monit_modules[0]) for monit_name, monit_modules in monits.items()])

        return cls._monits

