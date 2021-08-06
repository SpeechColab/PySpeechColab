import hashlib
import time
from pathlib import Path

import ijson
import urllib3
import yaml

url_of_host = {
    'oss': 'oss://speechcolab/GigaSpeech/release/GigaSpeech',
    'tsinghua': 'http://aidata.tsinghua-ieit.com/GigaSpeech',
    'speechocean': 'ftp://124.207.81.184/GigaSpeech',
    'magicdata': 'https://freedata.oss-cn-beijing.aliyuncs.com/magichub/GigaSpeech'
}

allowed_subsets = ('{XS}', '{S}', '{M}', '{L}', '{XL}', '{DEV}', '{TEST}')


class GigaSpeech(object):
    def __init__(self, path='.'):
        self.gigaspeech_dataset_dir = Path(path)
        self.json_path = self.gigaspeech_dataset_dir / 'GigaSpeech.json'
        self.gigaspeech_release_url = ''
        self.password = ''

    def download(
            self,
            password,
            subset='{XL}',
            host='tsinghua',
            with_dict=False
    ):
        assert subset in allowed_subsets, \
            f'subset {subset} not in {allowed_subsets}'

        if host not in url_of_host:
            raise NotImplementedError(f'Unknown host: {host}')
        self.gigaspeech_release_url = url_of_host[host]

        if self.gigaspeech_release_url.startswith('oss:'):
            raise NotImplementedError('For downloading from OSS, please use: '
                                      'github.com/SpeechColab/GigaSpeech/blob/main/utils/download_gigaspeech.sh')

        self.password = password

        # User agreement
        http = urllib3.PoolManager()
        response = http.request('GET', f'{self.gigaspeech_release_url}/TERMS_OF_ACCESS')
        access_term_text = response.data.decode()
        self.gigaspeech_dataset_dir.mkdir(parents=True, exist_ok=True)
        with open(self.gigaspeech_dataset_dir / 'TERMS_OF_ACCESS', 'w') as f:
            f.write(access_term_text)
            print(access_term_text)
        print('GigaSpeech downloading will start in 5 seconds')
        for t in range(5, 0, -1):
            print(t)
            time.sleep(1)

        # Download the file list
        filelist_path = self.gigaspeech_dataset_dir / 'files.yaml'
        filelist_remote_url = f'{self.gigaspeech_release_url}/files.yaml'
        response = http.request('GET', filelist_remote_url)
        with open(filelist_path, 'w') as f:
            f.write(response.data.decode())
        with open(filelist_path) as f:
            aes_list = yaml.load(f, Loader=yaml.FullLoader)

        def prepare_objects_from_release(category):
            assert category in aes_list, f'No entry for {category} found in files.yaml'
            for path in aes_list[category]:
                self.download_object_from_release(aes_list[category][path], path)
                self.process_downloaded_object(path)

        # Download metadata
        prepare_objects_from_release('metadata')

        # Download audio
        for audio_source in ('youtube', 'podcast', 'audiobook'):
            prepare_objects_from_release(audio_source)

        # Download optional dictionary & pretrained g2p model
        if with_dict:
            prepare_objects_from_release('dict')

    def download_object_from_release(self, remote_md5, obj):
        remote_obj = f'{self.gigaspeech_release_url}/{obj}'
        local_obj = self.gigaspeech_dataset_dir / obj

        if local_obj.exists():
            with open(local_obj, 'rb') as f:
                data = f.read()
                local_md5 = hashlib.md5(data).hexdigest()
            if local_md5 == remote_md5:
                print(f'Skipping {local_obj}, successfully retrieved already.')
                return
            else:
                print(f'{local_obj} corrupted or out-of-date, start to re-download.')

        local_obj.parent.mkdir(parents=True, exist_ok=True)
        http = urllib3.PoolManager()
        response = http.request('GET', remote_obj)
        with open(local_obj, 'wb') as f:
            f.write(response.data)

    def process_downloaded_object(self, obj):
        path = self.gigaspeech_dataset_dir / obj
        location = path.parent
        assert path.suffix == '.aes'
        with open(path, 'rb') as f:
            data = f.read()
            # TODO: decrypt

        if path.suffixes == ['.tgz', '.aes']:
            # encrypted-gziped-tarball contains contents of a GigaSpeech sub-directory
            subdir = location / Path(path.stem.strip('.tgz'))
            subdir.mkdir(parents=True, exist_ok=True)
        elif path.suffixes == ['.gz', '.aes']:
            # encripted-gziped object represents a regular GigaSpeech file
            pass
        else:
            # keep the object as it is
            pass

    def audios(self, subset='{XL}'):
        """
        Parses the JSON file "GigaSpeech.json" and yield the metadata of the audios.
        The library `ijson` parses big JSONs iteratively.

        :param subset: string, the subset name.
        :return: a generator of the audio metadata.
        """
        assert subset in allowed_subsets, \
            f'subset {subset} not in {allowed_subsets}'

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
