#!/usr/bin/env python

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['-m', 'not apitest']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)


setup(name='CommCareApi',
      version='0.1',
      description='CommCare API Client',
      install_requires=['drest', 'jsonpath-rw', 'lxml'],
      packages=['commcareapi'],
      tests_require=['pytest', 'mock'],
      cmdclass = {'test': PyTest})
