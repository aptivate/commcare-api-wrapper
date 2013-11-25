#!/usr/bin/env python

from distutils.core import setup

setup(name='CommCareApi',
      version='0.1',
      description='CommCare API Client',
      install_requires=['drest', 'jsonpath', 'lxml'],
      packages=['commcareapi'],)
