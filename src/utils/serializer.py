""" Serializer to read Instagrapi Data """

import json
from datetime import datetime

from instagrapi.types import HttpUrl, Story, User


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, HttpUrl):
            return o.url

        if isinstance(o, User):
            return o.__dict__

        return json.JSONEncoder.default(self, o)
