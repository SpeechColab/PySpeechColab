from pathlib import Path

allowed_subsets = ('XS', 'S', 'M', 'L', 'XL')


class GigaSpeech(object):
    def __init__(self, path='.'):
        self.path = path

    def download(self, subset='XL'):
        path = Path(self.path)
        path.mkdir(parents=True, exist_ok=True)

        assert subset in allowed_subsets, \
            f'subset {subset} not in {allowed_subsets}'
