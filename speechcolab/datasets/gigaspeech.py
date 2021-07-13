from pathlib import Path

import ijson


class GigaSpeech(object):
    def __init__(self, path='.'):
        self.root_path = Path(path)
        self.json_path = self.root_path / 'GigaSpeech.json'
        self.allowed_subsets = ('{XS}', '{S}', '{M}', '{L}', '{XL}', '{DEV}', '{TEST}')

    def download(self, subset='{XL}'):
        self.root_path.mkdir(parents=True, exist_ok=True)

        assert subset in self.allowed_subsets, \
            f'subset {subset} not in {self.allowed_subsets}'

        # TODO: download the data
        raise NotImplementedError

    def audios(self, subset='{XL}'):
        """
        Parses the JSON file "GigaSpeech.json" and yield the metadata of the audios.
        The library `ijson` parses big JSONs iteratively.

        :param subset: string, the subset name.
        :return: a generator of the audio metadata.
        """
        assert subset in self.allowed_subsets, \
            f'subset {subset} not in {self.allowed_subsets}'

        with open(self.json_path, 'rb') as f:  # open in binary mode to make `ijson` happy
            audios = ijson.items(f, 'audios.item')
            for audio in audios:
                if subset in audio['subsets']:
                    # We are filtering out the segments that do not belong to the requested subset
                    audio['segments'] = [s for s in audio['segments'] if subset in s['subsets']]
                    yield audio

    def segments(self, subset='{XL}'):
        """
        The generator of the segment metadata.

        :param subset: string, the subset name.
        :return: a generator of the segment metadata.
        """
        for audio in self.audios(subset):
            for segment in audio['segments']:
                yield segment
