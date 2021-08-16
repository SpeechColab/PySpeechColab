from speechcolab.datasets import gigaspeech

target_dir = './env/data/'

gigaspeech_data = gigaspeech.GigaSpeech(target_dir)
password_ext = '.5/ei5.YwglJbQTrPF4yDMoktSepkm4D5'

gigaspeech_data.download(password_ext, '{XS}')

print('Download successful.')

