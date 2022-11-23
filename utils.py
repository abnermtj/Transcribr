"""
Helper functions
"""

import os
import time


def get_file_size(file):
    """
    Input a file object and you get integer file size in megabytes
    """
    old_file_position = file.tell()
    file.seek(0, os.SEEK_END)
    getsize = file.tell()
    file.seek(old_file_position, os.SEEK_SET)
    return round((getsize / 1000000), 1)


def get_pretty_date(seconds):
    """
    seconds - seconds from epoch to a date
    """
    return time.ctime(seconds)


def get_pretty_duration(seconds):
    """
    Coverts to [hours], minutes, seconds
    """
    seconds = seconds % (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    if hours != 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"
