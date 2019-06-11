
import re


class Error(Exception):
    pass


class ValidationError(Error):
    pass


class ValidateURL(object):
    """Implementing URL validation."""

    ul = '\u00a1-\uffff'  # unicode letters range (must not be a raw string)
    # IP patterns
    ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = r'\[[0-9a-f:\.]+\]'  # (simple regex, validated later)

    # Host patterns
    hostname_re = r'[a-z' + ul + \
        r'0-9](?:[a-z' + ul + r'0-9-]{0,61}[a-z' + ul + r'0-9])?'
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]{1,63}(?<!-))*'
    tld_re = (
        r'\.'                                # dot
        r'(?!-)'                             # can't start with a dash
        r'(?:[a-z' + ul + '-]{2,63}'         # domain label
        r'|xn--[a-z0-9]{1,59})'              # or punycode label
        r'(?<!-)'                            # can't end with a dash
        r'\.?'                               # may have a trailing dot
    )
    host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

    regex = re.compile(
        r'^(?:[a-z0-9\.\-\+]*)://'  # scheme is validated separately
        r'(?:\S+(?::\S*)?@)?'  # user:pass authentication
        r'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
        r'(?::\d{2,5})?'  # port
        r'(?:[/?#][^\s]*)?'  # resource path
        r'\Z', re.IGNORECASE)
    message = 'Enter a valid URL.'
    schemes = ['http', 'https', 'ftp', 'ftps']

    def __init__(self, raise_error: bool = False):

        self.raise_error = raise_error

    def __call__(self, value: str = None) -> bool:

        # check if the scheme is valid.
        scheme = value.split('://')[0].lower()
        if scheme not in self.schemes:
            if self.raise_error:
                raise ValidationError(self.message)
            return False

        match = bool(self.regex.search(str(value)))
        if not match and self.raise_error:
            raise ValidationError(self.message)
        return match


if __name__ == '__main__':

    url = 'http://gnu.org'
    print(ValidateURL()(value=url))
    url = 'gnu.org'
    print(ValidateURL()(value=url))
