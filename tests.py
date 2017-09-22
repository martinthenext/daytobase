#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from coverage import coverage

from datetime import datetime
import pytz
import timezone

class User(object):
    "User with a timezone attribute as a string"
    def __init__(self):
        self.timezone = "Europe/London"
        self.time_format = '%Y.%m.%d %H:%M:%S'

class Test_timezone(unittest.TestCase):
    def setUp(self):
        self.user = User()

    def tearDown(self):
        pass

    def test_get_datetime_repr(self):
        """
        Test conversion of UTC time to user's timezone in their chosen time format.
        The output should be a string.
        """
        utcnow = datetime.utcnow()
        dt_user = timezone.get_datetime_repr(dt=utcnow, user=self.user)
        test_dt_user = pytz.timezone(self.user.timezone).fromutc(utcnow).strftime(self.user.time_format)
        assert type(dt_user) == str
        assert dt_user == test_dt_user



run_coverage = False

if run_coverage:
    cov = coverage(branch=True, omit=['env/*'])
    cov.start()


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    if run_coverage:
        cov.stop()
        cov.save()
        print "\n\nCoverage report:\n"
        cov.report()
        cov.erase()
