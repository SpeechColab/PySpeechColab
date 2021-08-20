from speechcolab.utils import download


def test_download_from_http_to_buffer():
    url = 'https://raw.githubusercontent.com/SpeechColab/PySpeechColab/main/LICENSE'
    data = download.download_from_http_to_buffer(url)
    assert data.decode().strip().startswith('Apache License')


def test_download_from_ftp_to_buffer():
    host, username, password = 'test.rebex.net', 'demo', 'password'
    remote_path = '/pub/example/readme.txt'
    data = download.download_from_ftp_to_buffer(host, remote_path, username, password)
    assert data.decode().startswith('Welcome')
