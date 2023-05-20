""" Serializer to read Instagrapi Data """

import json
from datetime import datetime

from instagrapi.types import HttpUrl, Location, Media, Story, User, UserShort


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, HttpUrl):
            return o.url

        if isinstance(o, User):
            return o.__dict__

        if isinstance(o, UserShort):
            return o.__dict__

        if isinstance(o, Location):
            return o.__dict__

        if isinstance(o, Media):
            return {
                "pk": o.pk,
                "taken_at": json.loads(json.dumps(o.taken_at, cls=CustomJSONEncoder)),
                "media_type": o.media_type,
                "product_type": o.product_type,
                "thumbnail_url": json.loads(
                    json.dumps(o.thumbnail_url, cls=CustomJSONEncoder)
                ),
                "location": json.loads(json.dumps(o.location, cls=CustomJSONEncoder)),
                "user_id": o.user.pk,
                "comment_count": o.comment_count,
                "comments_disabled": o.comments_disabled,
                "commenting_disabled_for_viewer": o.commenting_disabled_for_viewer,
                "like_count": o.like_count,
                "play_count": o.play_count,
                "has_liked": o.has_liked,
                "caption_text": o.caption_text,
                "usertags": dict(
                    zip(
                        [f"user_{i+1}" for i in range(0, len(o.usertags))],
                        [i.user.pk for i in o.usertags],
                    )
                ),
                "sponsor_tags": dict(
                    zip(
                        [f"user_{i+1}" for i in range(0, len(o.sponsor_tags))],
                        [i.pk for i in o.sponsor_tags],
                    )
                ),
                "video_url": json.loads(json.dumps(o.video_url, cls=CustomJSONEncoder)),
                "view_count": o.view_count,
                "video_duration": o.video_duration,
                "title": o.title,
            }

        return json.JSONEncoder.default(self, o)
