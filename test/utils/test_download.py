from tempfile import NamedTemporaryFile
from speechcolab.utils import download


def test_download_from_http_to_buffer():
    url = 'https://raw.githubusercontent.com/SpeechColab/PySpeechColab/main/LICENSE'
    with NamedTemporaryFile(delete=True) as f:
        download.download_from_http(f.name, url)
        data = f.read().decode()
    assert data.strip().startswith('Apache License')


def test_download_from_ftp_to_buffer():
    host, username, password = 'test.rebex.net', 'demo', 'password'
    remote_path = '/pub/example/readme.txt'
    with NamedTemporaryFile(delete=True) as f:
        download.download_from_ftp(f.name, host, remote_path, username, password)
        data = f.read().decode()

    assert data.startswith('Welcome')
