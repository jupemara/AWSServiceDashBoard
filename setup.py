#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='aws_service_dashboard',
    version='0.1.0',
    description='Get Amazon Web Service Healthes.',
    author='ARASHI, Jumpei',
    author_email='jumpei.arashi@arashike.com',
    url='https://github.com/JumpeiArashi/AWSServiceDashBoard',
    license='WTFPL',
    tests_require=[
        'nose'
    ],
    classifiers=[
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
