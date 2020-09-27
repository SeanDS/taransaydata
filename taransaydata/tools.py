"""Tools."""

import zlib
import json
from webargs.flaskparser import FlaskParser


class GzippedJsonFlaskParser(FlaskParser):
    """Flask parser that inflates gzipped JSON payloads."""

    def load_json(self, req, schema):
        body = req.get_data(cache=True)

        if req.content_encoding == "gzip":
            body = zlib.decompress(body)

        return json.loads(body)


def js_array_stream(items):
    def format_item(item):
        item_datetime, item_data = item
        return f'{{"x": "{item_datetime}", "y": {item_data}}}'

    try:
        previous_item = next(items)
    except StopIteration:
        # Empty.
        yield "[]"
        return

    yield "[\n"

    for item in items:
        yield f"\t{format_item(previous_item)},\n"
        previous_item = item

    yield f"\t{format_item(previous_item)}\n"
    yield "]"
