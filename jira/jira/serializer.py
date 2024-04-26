from datetime import datetime
from json import JSONEncoder


class JiraEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)
