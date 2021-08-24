import ftplib
from urllib.parse import urlparse
from urllib.request import urlopen


def download_from_http(local_filename, url):
    response = urlopen(url)
    chunk_size = 16 * 1024 * 1024
    with open(local_filename, 'wb') as f:
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)


def download_from_ftp(local_filename, host, remote_path, username=None, password=None, port=None):
    ftp = ftplib.FTP()

    if port is None:
        port = 21
    ftp.connect(host, port)

    if username is not None:
        ftp.login(username, password)
    else:
        ftp.login()

    with open(local_filename, 'wb') as f:
        ftp.retrbinary('RETR ' + remote_path, f.write)


def download(local_filename, url):
    if url.startswith('http://') or url.startswith('https://'):
        return download_from_http(local_filename, url)
    elif url.startswith('ftp://'):
        url_info = urlparse(url)
        return download_from_ftp(local_filename, url_info.hostname, url_info.path, url_info.username,
                                 url_info.password.replace('<SLASH>', '/'), url_info.port)
    else:
        raise ValueError('URL must starts with "http://", "https://", or "ftp://"')
