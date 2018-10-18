import os
import re
import stat

from celery import chord, shared_task

from .models import DataModel
from ..corpus.models import insert_urlobj, insert_many_data_objects, set_crawl_ready


@shared_task(bind=True)
def call_data_create(self, **kwds):
    """ Task that calls DataModel.create.
    expected kwds:
    {
        'links': list,
        'corpus_file_path': /corpus/file/path,
        'data': list[str],
        'endpoint': endpoint,
        'corpus_id': str
    }
    """
    doc, file_id = DataModel.create(**kwds)
    if isinstance(doc, DataModel) and file_id:
        insert_urlobj(
            kwds.get('corpus_id'),
            {
                'data_id': str(doc.get('_id')),
                'url': doc.get('url'),
                'texthash': doc.get('hashtxt'),
                'file_id': file_id,
                'title': doc.get('title') or doc.get('url')
            })
        return str(doc.get_id()), file_id
    return None, None


@shared_task(bind=True)
def file_uploads_to_data(self, corpusid: str = None, files: dict = None,
                         encoding: str = "utf-8",
                         corpus_file_path: str = None):

    chord([create_data_fromtxt.s(
        **{
            'corpusid': corpusid,
            'orig_filename': k,
            'tmp_filename': v,
            'encoding': encoding,
            'corpus_file_path': corpus_file_path
        }
    ) for k, v in files.items()])(file_uploads_callback.s())


@shared_task(bind=True)
def file_uploads_callback(self, results):

    corpusid = None
    out = []
    for docid, fileid, corpusid, title, file_path in results:
        out.append({
            'data_id': docid,
            'file_id': fileid,
            'title': title,
            'file_path': file_path
        })
    insert_many_data_objects(corpusid=corpusid, data_objs=out)
    set_crawl_ready(corpusid, True)


@shared_task(bind=True)
def create_data_fromtxt(self, corpusid: str = None, orig_filename: str = None,
                        tmp_filename: str = None, encoding: str = "utf-8",
                        corpus_file_path: str = None):
    """Creates a Data object from a text file."""
    doc, file_id = DataModel.create_empty(
        corpus_id=corpusid,
        title=orig_filename)
    docid = str(doc.get('_id'))
    file_on_disk = process_screenplay(
        filename=orig_filename,
        encoding=encoding,
        data_id=docid,
        destination=os.path.normpath(
            os.path.join(corpus_file_path, file_id)),
        tmp=tmp_filename,
        check_out=False,
    )
    if not os.path.isfile(file_on_disk):
        raise RuntimeError('{} - {}'.format(docid, file_on_disk))
    return (docid, file_id, corpusid, orig_filename, file_on_disk, )


def process_screenplay(data_id: str = None, tmp: str = None,
                       check_out=True, filename: str = None,
                       destination: str = None, encoding: str = 'utf-8'):

    with open(tmp, 'rb') as _:
        txt = _.read().decode(encoding=encoding)
    os.remove(tmp)

    txt = re.sub(r'\t', ' ', txt, flags=re.M)
    txt = re.sub(r'^\s+', '', txt, flags=re.M)

    start, end = 0, 0
    nextstart = 0
    prevend = 0
    regex = re.compile(r"([^.?!]|(?<=\b[A-Za-z0-9]|\s)[.!?])+[.?!]?")

    with open(destination, '+a') as dest:
        dest.write("%s\n\n" % data_id)
        while True:
            match = regex.search(txt, nextstart)
            if not match:
                if prevend < len(txt):
                    dest.write("%s\n" % txt[prevend:])

                break
            start = match.start()
            end = match.end()
            nextstart = end

            if start > prevend:
                dest.write("%s\n" % txt[prevend: start])

            sentence = match.group(0).replace('\n', ' ').strip()
            sentence = re.sub(r'\s{2,}', ' ', sentence)
            dest.write("%s\n" % sentence)
            prevend = end

    # permissions 'read, write, execute' to user, group, other (777)
    os.chmod(destination, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    if check_out:
        check_validity(destination, txt, filename)
    return destination


def check_validity(destination: str, txt: str, filename: str):

    old_count = {}
    new_count = {}

    with open(destination, 'r') as _:
        for i in _.readlines():
            for _word in re.findall(r'\b\w+\b', i):
                _word = _word.lower()
                if _word in new_count:
                    new_count[_word] += 1
                else:
                    new_count[_word] = 1
    for i in re.findall(r'\b\w+\b', txt):

        i = i.lower()
        if i in old_count:
            old_count[i] += 1
        else:
            old_count[i] = 1
    error_msg = {'file_name': filename}
    if new_count != old_count:
        # print('{} was not processed correclty.'.format(filename))
        difference = set(old_count.keys()) - set(new_count.keys())
        # print('Words in the old text, missing in the new text: %r' %
        #       difference)
        error_msg['old_keys__diff__new_keys'] = difference

        # for k, v in old_count.items():
        #     if new_count[k] != v:
        #         print('in original: "{}" - {}; in sentences: "{}" - {}'.format(
        #             k, v, k, new_count[k]))
        # print('Words present in sentences, missing in the original text.')
        # for k, v in new_count.items():
        #     if k not in old_count:
        #         print('{} - {} is present in the sentences'.format(k, v))

        raise RuntimeError(error_msg)
    return True
