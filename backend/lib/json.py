from datetime import datetime, timezone
from json import JSONEncoder


class DateTimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.astimezone(timezone.utc).isoformat()

        return super(DateTimeEncoder, self).default(o)
