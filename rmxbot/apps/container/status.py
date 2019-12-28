

def status_text(status):

    if not status:
        return None, None

    _ = Status(status=status)

    if status == 'newly-created':
        return _.newly_created
    elif status == 'file-upload':
        return _.file_upload
    elif status == 'crawling':
        return _.crawling
    elif status == 'remove-files':
        return _.remove_files
    elif status == 'integrity-check':
        return _.integrity_check
    elif status == 'busy':
        return _.busy
    else:
        return _.nosuch_msg


class Status(object):

    def __init__(self, status):

        self.status = status

    @property
    def newly_created(self):

        return self.status, 'Container with texts being created...'

    @property
    def busy(self):

        return self.status, 'The server is busy...'

    @property
    def file_upload(self):

        return self.status, 'File upload in progress...'

    @property
    def crawling(self):

        return self.status, 'Crawling the web...'

    @property
    def remove_files(self):

        return self.status, 'Files being deleted...'

    @property
    def integrity_check(self):

        return self.status, 'Matrix integrity check...'

    @property
    def nosuch_msg(self):

        return self.status, 'Wait...'
