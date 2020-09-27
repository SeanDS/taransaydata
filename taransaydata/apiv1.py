"""Taransay data service REST API v1"""

import json
from flask import Blueprint, Response, jsonify, make_response, url_for
from webargs import fields
from werkzeug.exceptions import NotFound, UnprocessableEntity
from .data import (
    tags_config,
    groups,
    group_config,
    devices,
    device_config,
    device_channel_index,
    device_query,
    device_write,
)
from .tools import js_array_stream, GzippedJsonFlaskParser

app = Blueprint("apiv1", __name__)

parser = GzippedJsonFlaskParser()

# Schema for reading data.
DATA_QUERY_SCHEMA = {
    "start": fields.DateTime(required=True),
    "stop": fields.DateTime(),
    "step": fields.Int(),
}

# Schema for writing data (not used directly)
_DATA_INPUT = fields.List(
    fields.Tuple((fields.DateTime(), fields.List(fields.Float()),), required=True),
)

# Schema for submitting data.
SINGLE_DATA_INPUT_SCHEMA = {
    "sent": fields.DateTime(required=True),
    "data": _DATA_INPUT,
}

BULK_DATA_INPUT_SCHEMA = {
    "sent": fields.DateTime(required=True),
    "data": fields.Dict(
        keys=fields.Str(required=True),  # Group.
        values=fields.Dict(
            keys=fields.Str(required=True), values=_DATA_INPUT  # Device.  # Data.
        ),
    ),
}


def tags_info():
    return tags_config()


def groups_info():
    return [group_info(group) for group in groups()]


def group_info(group):
    info = group_config(group)

    extra = {
        "devices": [device_info(group, device) for device in devices(group)],
        "url": url_for("apiv1.group_devices_list", group=info["slug"], _external=True),
    }
    info.update(extra)

    return info


def devices_info(group):
    return [device_info(group, device) for device in devices(group)]


def device_info(group, device):
    info = device_config(group, device)

    for channel in info["channels"]:
        channel["group"] = group
        channel["device"] = device

    url_endpoints = {
        "url": url_for(
            "apiv1.group_device_info", group=group, device=device, _external=True
        ),
        "data_url": url_for(
            "apiv1.group_device_data", group=group, device=device, _external=True
        ),
    }
    info.update(url_endpoints)

    return info


@app.errorhandler(NotFound)
@app.errorhandler(UnprocessableEntity)
def handle_error(error):
    """Return JSON instead of HTML for HTTP errors."""
    # Start with the correct headers and status code from the error.
    response = error.get_response()
    # Replace the body with JSON.
    response.data = json.dumps(
        {"code": error.code, "name": error.name, "description": error.description}
    )
    response.content_type = "application/json"
    return response


@parser.error_handler
def handle_parser_error(error, *args, **kwargs):
    raise UnprocessableEntity(error.messages)


@app.route("/")
def directory():
    """List server directory."""
    directory = {
        "tags": url_for("apiv1.tags_list", _external=True),
        "devices": url_for("apiv1.devices_list", _external=True),
    }
    return make_response(jsonify(directory=directory), 200)


@app.route("/info/tags")
def tags_list():
    tags = tags_info()
    return make_response(jsonify(tags), 200)


@app.route("/info/groups")
def devices_list():
    """List groups and their devices."""
    groups = groups_info()
    return make_response(jsonify(groups=groups), 200)


@app.route("/info/groups/<group>/")
def group_devices_list(group):
    """List group devices."""
    devices = devices_info(group)
    return make_response(jsonify(devices), 200)


@app.route("/info/devices/<group>/<device>")
def group_device_info(group, device):
    """List group device info."""
    info = device_info(group, device)
    return make_response(jsonify(info), 200)


@app.route("/data/<group>/<device>", methods=["GET"])
@app.route("/data/<group>/<device>/<channel>", methods=["GET"])
@parser.use_kwargs(DATA_QUERY_SCHEMA, location="query")
def group_device_data(group, device, channel=None, **kwargs):
    """Display group device data."""
    data = device_query(group, device, **kwargs)

    if channel is not None:
        # Extract the data at the respective channel's index.
        index = device_channel_index(group, device, channel)
        data = map(lambda row: (row[0], row[1][index]), data)

    # Stream data as it is provided by the library.
    return Response(js_array_stream(data), status=200, content_type="application/json")


@app.route("/data/<group>/<device>", methods=["POST"])
@parser.use_kwargs(SINGLE_DATA_INPUT_SCHEMA, location="json")
def group_device_input(group, device, sent, data=None):
    """Record group device data."""
    device_write(group, device, data)

    return make_response(jsonify(message="created"), 201)


@app.route("/data", methods=["POST"])
@parser.use_kwargs(BULK_DATA_INPUT_SCHEMA, location="json")
def bulk_input(sent, data):
    """Record data for many group devices at once."""
    for group, group_data in data.items():
        for device, device_data in group_data.items():
            device_write(group, device, device_data)

    return make_response(jsonify(message="created"), 201)
