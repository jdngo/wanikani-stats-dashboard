from datetime import datetime
import pytz

def get_current_timestamp(timezone = "America/Los_Angeles"):
    """
    Insert docstring here...
    """
    return datetime.now(tz = pytz.timezone(timezone))

def parse_timestamp(timestamp, timezone = "America/Los_Angeles"):
    """
    Insert docstring here...
    """
    if timestamp is None:
        return None
    else:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z").astimezone(tz = pytz.timezone(timezone))

def seconds_to_days(seconds):
    """
    Insert docstring here...
    """
    return seconds / 86400
