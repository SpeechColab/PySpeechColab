import os

from speechcolab.datasets import gigaspeech

target_dir = './env/data/'


def test_gigaspeech():
    gigaspeech_data = gigaspeech.GigaSpeech(target_dir)
    gigaspeech_data.download()
    assert os.path.isdir(target_dir)
