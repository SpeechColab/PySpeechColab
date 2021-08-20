import urllib3
import ftplib
from urllib.parse import urlparse


def download_from_http_to_buffer(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    return response.data


def download_from_ftp_to_buffer(host, remote_path, username=None, password=None, port=None):
    ftp = ftplib.FTP()

    if port is None:
        port = 21
    ftp.connect(host, port)

    if username is not None:
        ftp.login(username, password)
    else:
        ftp.login()

    data = []

    def handle_binary(x):
        data.append(x)

    ftp.retrbinary('RETR ' + remote_path, callback=handle_binary)
    return b''.join(data)


def download_to_buffer(url):
    if url.startswith('http://') or url.startswith('https://'):
        return download_from_http_to_buffer(url)
    elif url.startswith('ftp://'):
        url_info = urlparse(url)
        return download_from_ftp_to_buffer(url_info.hostname, url_info.path, url_info.username,
                                           url_info.password.replace('<SLASH>', '/'), url_info.port)
    else:
        raise ValueError('URL must starts with "http://", "https://", or "ftp://"')
