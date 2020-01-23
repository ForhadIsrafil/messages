from django.utils import timezone
import pytz
import calendar
import time
from datetime import datetime, timedelta


class Clock(object):
    @classmethod
    def utc_now(cls):
        return datetime.utcnow()

    @classmethod
    def to_utc(cls, native_dt):
        return native_dt.replace(tzinfo=None)

    @classmethod
    def utc_timestamp(cls):
        return int(time.mktime(timezone.now().replace(tzinfo=None).timetuple()))

    @classmethod
    def start_of_year(cls):
        return datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0)

    @classmethod
    def end_of_year(cls):
        return datetime.utcnow().replace(month=12, day=31, hour=23, minute=59, second=59)

    @classmethod
    def last_month(cls):
        today = Clock.utc_now()
        last_30_days = today - timedelta(days=30)
        return last_30_days

    @classmethod
    def days_ago(cls, days):
        today = Clock.utc_now()
        days_ago = today - timedelta(days=int(days))
        return days_ago

    @classmethod
    def convert_local_to_utc(cls, timezone, dt):
        tz = pytz.timezone(timezone)  # "America/Los_Angeles"
        local_dt = tz.localize(dt, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt

    @classmethod
    def utc_to_local_datetime(cls, dt, tz):
        local_tz = pytz.timezone(tz)
        utc_dt = pytz.utc.localize(dt)
        return utc_dt.astimezone(local_tz)

    @classmethod
    def _90_sec_ago(cls):
        now = Clock.utc_now()
        _90_sec_ago = now  - timedelta(minutes=1.5)
        return _90_sec_ago