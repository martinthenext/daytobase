#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import pytz


def get_datetime_repr(dt, user):
    """
    Convets a datetime object to the user's timezone and returns it in
    string representation

    Arguments:
    dt: datetime object

    user: user object.
        Has a `timezone` attribute (a string) and a `time_format` attribute

    Returns:
    dt_str: str
        String representation of time in user's timezone
    """
    user_tz = pytz.timezone(user.timezone)
    dt_user = user_tz.fromutc(dt)
    return dt_user.strftime(user.time_format)
