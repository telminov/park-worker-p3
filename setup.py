# coding: utf-8
# python setup.py sdist register upload
from distutils.core import setup

setup(
    name='park-worker-p3',
    version='0.1.0',
    description='Workers for park-keeper project for python version 3.',
    author='Telminov Sergey',
    url='https://github.com/telminov/park-worker-p3',
    packages=[
        'parkworker3',
        'parkworker3/bin',
        'parkworker3/monits',
    ],
    license='The MIT License',
    install_requires=[
        'park-worker-base', 'pyzmq', 'pytz', 'aiohttp'
    ],
)
