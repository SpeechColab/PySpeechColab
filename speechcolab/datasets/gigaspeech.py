import gzip
import hashlib
import io
import tarfile
import time
from hashlib import pbkdf2_hmac
from pathlib import Path

import ijson
import urllib3
import yaml
from Crypto.Cipher import AES

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
        """
        Download and extract the dataset files.

        :param password: string, the password issued by GigaSpeech.
        :param subset: string, the subset name.
        :param host: string, hostname, which should be in ('tsinghua', 'speechocean', 'magicdata').
        :param with_dict: bool, whether to download the dict.
        """
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
                self.download_and_process_object_from_release(aes_list[category][path], path)

        # Download metadata
        prepare_objects_from_release('metadata')

        # Download audio
        for audio_source in ('youtube', 'podcast', 'audiobook'):
            prepare_objects_from_release(audio_source)

        # Download optional dictionary & pretrained g2p model
        if with_dict:
            prepare_objects_from_release('dict')

    def download_and_process_object_from_release(self, remote_md5, obj):
        # Download
        remote_obj = f'{self.gigaspeech_release_url}/{obj}'
        local_obj = self.gigaspeech_dataset_dir / obj
        need_download = True
        data = ''
        if local_obj.exists():
            with open(local_obj, 'rb') as f:
                data = f.read()
                local_md5 = hashlib.md5(data).hexdigest()
            if local_md5 == remote_md5:
                print(f'Skipping {local_obj}, successfully retrieved already.')
                need_download = False

        if need_download:
            print(f'{local_obj} corrupted or out-of-date, start to re-download.')
            local_obj.parent.mkdir(parents=True, exist_ok=True)
            http = urllib3.PoolManager()
            response = http.request('GET', remote_obj)
            data = response.data

        # Decrypt
        bs = AES.block_size
        salt = data[:bs][len('Salted__'):]
        key_length = 32
        d = pbkdf2_hmac('sha256', self.password.encode(), salt, 10000, key_length + bs)
        key, iv = d[:key_length], d[key_length:key_length + bs]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data_dec = cipher.decrypt(data[bs:])

        # Write to disk
        io_bytes = io.BytesIO(data_dec)
        if local_obj.suffixes == ['.tgz', '.aes']:
            # encrypted-gziped-tarball contains contents of a GigaSpeech sub-directory
            subdir = local_obj.parent / Path(local_obj.stem.strip('.tgz'))
            subdir.mkdir(parents=True, exist_ok=True)
            with tarfile.open(fileobj=io_bytes, mode='r') as tar:
                tar.extractall(path=subdir)
        elif local_obj.suffixes == ['.gz', '.aes']:
            # encripted-gziped object represents a regular GigaSpeech file
            out_path = Path(local_obj.stem.strip('.gz.aes'))
            with gzip.open(io_bytes, 'rb') as gz, open(out_path, 'wb') as f:
                f.write(gz.read())
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
