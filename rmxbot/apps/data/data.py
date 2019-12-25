

from .models import DataModel


def webpage(docid):
    """
    Displays the page - the doc and its structure. This object holds all the
    links that have been found on the scraped page.

    :param docid:
    :return:
    """
    document = DataModel.inst_by_id(docid)
    if not isinstance(document, DataModel):
        return {'success': False, 'msg': 'No doc found.'}

    dataid = document.get_id()
    document = dict(document)
    document['dataid'] = dataid
    del document['_id']
    return document
