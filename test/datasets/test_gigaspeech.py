import pytest

from speechcolab.datasets import gigaspeech

target_dir = './env/data/'


@pytest.fixture
def gigaspeech_data():
    return gigaspeech.GigaSpeech(target_dir)


def test_gigaspeech_audios(gigaspeech_data):
    for i, audio in enumerate(gigaspeech_data.audios('{XS}')):
        assert audio['source'] in ('podcast', 'audiobook', 'youtube')
        assert len(audio['segments']) > 0
        if i > 5:
            break


def test_gigaspeech_segments(gigaspeech_data):
    for i, segment in enumerate(gigaspeech_data.segments('{XS}')):
        assert len(segment['text_tn']) > 0
        if i > 100:
            break
