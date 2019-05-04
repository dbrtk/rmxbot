
import bson
from werkzeug.routing import BaseConverter


class ObjectidConverter(BaseConverter):
    """A url converter for bson's ObjectId."""

    regex = r"[a-f0-9]{24}"

    def to_python(self, value):

        return bson.ObjectId(value)

    def to_url(self, value):

        if not isinstance(value, bson.ObjectId):
            raise ValueError(value)
        return str(value)
