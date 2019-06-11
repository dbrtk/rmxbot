"""The URL field"""

from ..validate_url import ValidateURL, ValidationError


class UrlField:
    """ Custom class extending the str url field. """
    mongo_type = str
    python_type = str
    init_type = str

    def __init__(self, url):
        """ """
        self.value = url

    def to_bson(self, value=None):
        """
        """
        if not self.value:
            return str(value)
        else:
            return str(self.value)

    def to_python(self, value):
        """
        """
        return str(value)

    def validate(self, value=None, path=None):
        """Validating the url"""
        if value or self.value:
            value = value if value else self.value
            validator = ValidateURL()
            validator(value)
            return value
        return None

    def get_value(self):
        """ returns the field's value """
        return self.value


def validate_url_list(urls):
    """Validating a list of urls. Returns a list of valid urls."""

    validate = ValidateURL()

    for _ in urls:
        if not _:
            continue
        try:
            validate(_)
        except ValidationError:
            continue
        yield _
