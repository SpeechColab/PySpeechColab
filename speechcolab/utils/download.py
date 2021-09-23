import ftplib
import hashlib
import ssl
from tqdm import tqdm
from urllib.parse import urlparse
from urllib.request import urlopen


def download_from_http(local_filename, url, show_progress_bar=False):
    response = urlopen(url)
    length = int(response.getheader('content-length'))
    assert length
    chunk_size = 4096
    with open(local_filename, 'wb') as f:
        pbar = tqdm(range(length), unit='B', unit_scale=True, unit_divisor=1024) if show_progress_bar else None
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            if show_progress_bar:
                pbar.update(chunk_size)


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


def download(local_filename, url, show_progress_bar=False):
    ssl._create_default_https_context = ssl._create_unverified_context
    if url.startswith('http://') or url.startswith('https://'):
        return download_from_http(local_filename, url, show_progress_bar)
    elif url.startswith('ftp://'):
        url_info = urlparse(url)
        return download_from_ftp(local_filename, url_info.hostname, url_info.path, url_info.username,
                                 url_info.password.replace('<SLASH>', '/'), url_info.port)
    else:
        raise ValueError('URL must starts with "http://", "https://", or "ftp://"')


def file_md5(filename, chunk_size=40960):
    filehash = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            filehash.update(chunk)
    return filehash.hexdigest()
