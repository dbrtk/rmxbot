"""Handling json."""

import json
import bson
import datetime
import uuid


class RmxEncoder(json.JSONEncoder):
    """Extending the json.JSONEncoder in order to convert ObjectIds into
       string while encoding.
    """

    def default(self, _o, *args, **kwds):
        """Overriding the default method - it should also be able to deal with
           'datetime' objects

        """
        if isinstance(_o, (bson.ObjectId, uuid.UUID,)):
            return str(_o)
        elif isinstance(_o, (datetime.datetime, datetime.time,)):
            if hasattr(_o, 'isoformat'):
                return _o.isoformat()
            else:
                raise TypeError(_o)
        super(RmxEncoder, self).default(_o, *args, **kwds)
