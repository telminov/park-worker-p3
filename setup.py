# coding: utf-8
from distutils.core import setup

setup(
    name='django-park-worker-p3',
    version='0.0.1',
    description='Workers for park-keeper project for python version 3.',
    author='Telminov Sergey',
    url='https://github.com/telminov/park-worker-p3',
    packages=['parkworker3',],
    license='The MIT License',
    install_requires=[
        'park-worker-base', 'pyzmq', 'pytz', 'aiohttp'
    ],
)
