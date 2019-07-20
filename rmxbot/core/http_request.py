
import requests
from requests.adapters import HTTPAdapter

from ..config import REQUEST_MAX_RETRIES


def _session(session):

    session = session or requests.Session()
    adapter = HTTPAdapter(max_retries=REQUEST_MAX_RETRIES)

    session.mount('http://', adapter)
    return session


def get(endpoint: str = None, session: requests.Session = None, **kwds):

    session = _session(session=session)
    return session.get(endpoint, **kwds)


def post(endpoint: str = None, session: requests.Session = None, **kwds):

    session = _session(session=session)
    return session.post(endpoint, **kwds)
