"""Data functions."""

from datetime import datetime
from yaml import safe_load
from taransaydb import FloatDevice
from werkzeug.exceptions import NotFound
from . import DATA_DIR, INFO_FILENAME


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)

        if status_code is not None:
            self.status_code = status_code

        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def meta_config():
    meta_config_file = DATA_DIR / INFO_FILENAME

    if not meta_config_file.is_file():
        raise FileNotFoundError("meta info file not found")

    with meta_config_file.open("r") as info_obj:
        return safe_load(info_obj)


def tags_config():
    return meta_config()["tags"]


def groups():
    return [group_dir.name for group_dir in DATA_DIR.iterdir() if group_dir.is_dir()]


def group_config(group):
    group_dir = DATA_DIR / group

    if not group_dir.is_dir():
        raise FileNotFoundError(f"group {group} directory not found")

    group_info_file = group_dir / INFO_FILENAME

    if not group_info_file.is_file():
        raise FileNotFoundError(f"group {group} info file not found")

    with group_info_file.open("r") as info_obj:
        config = safe_load(info_obj)

    return config


def devices(group):
    group_dir = DATA_DIR / group

    if not group_dir.is_dir():
        raise FileNotFoundError(f"group {group} directory not found")

    return [
        device_dir.name for device_dir in group_dir.iterdir() if device_dir.is_dir()
    ]


def device_config(group, device):
    device_dir = DATA_DIR / group / device

    if not device_dir.is_dir():
        raise FileNotFoundError(f"device {group}/{device} directory not found")

    device_config_file = device_dir / INFO_FILENAME

    if not device_config_file.is_file():
        raise FileNotFoundError(f"device {group}/{device} info file not found")

    with device_config_file.open("r") as info_obj:
        return safe_load(info_obj)


def device_channel_index(group, device, channel):
    device = device_config(group, device)
    for index, channel_info in enumerate(device["channels"]):
        if channel_info["slug"] == channel:
            return index

    raise ValueError(f"Channel {channel} not found")


def device_query(group, device, start, stop=None, **kwargs):
    if stop is None:
        stop = datetime.now()

    device = device_init(group, device)

    with device.reader() as driver:
        yield from driver.query_interval(start, stop, **kwargs)


def device_write(group, device, data):
    device = device_init(group, device)

    with device.writer() as driver:
        # Sort received data by ascending date order.
        for time, values in sorted(data, key=lambda row: row[0]):
            driver.append(time, values)


def device_init(group, device):
    device_dir = DATA_DIR / group / device

    if not device_dir.is_dir():
        raise NotFound(f"Device '{device}' does not exist.")

    return FloatDevice(device_dir)
