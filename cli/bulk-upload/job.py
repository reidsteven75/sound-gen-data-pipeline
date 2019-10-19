import os
import json
import requests
import re
import uuid 
import datetime

ENV = 'prod'  # dev, prod

JOB_NAME = 'BULK-SOUND-UPLOAD'
CONFIG_FILE = 'config.json'
with open(CONFIG_FILE, 'r') as infile:
  config = json.load(infile)

API = config[ENV]['api']['http'] + config[ENV]['api']['host'] + config[ENV]['api']['port'] + '/api'
GOOGLE_STORAGE_UPLOAD_PATH = config[ENV]['googleStorage']['uploadPath']
FILE_PATH = './sounds'

def unique_id():
  return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + \
          '_' + \
          uuid.uuid4().hex[:6].upper()

def parse_latent_space(string, vector):
  match = re.search(vector + r'_(...)', string)
  if match:
    return float(match.group(1))
  else:
    return None

def get_filetype(file_name):
  return os.path.splitext(file_name)[1].replace('.', '')

def upload_sound(file_path, file_name, sound_space_id):
  latent_space = {
    'NW': None,
    'NE': None,
    'SW': None,
    'SE': None
  }
  latent_space['NW'] = parse_latent_space(file_name, 'NW')
  latent_space['NE'] = parse_latent_space(file_name, 'NE')
  latent_space['SW'] = parse_latent_space(file_name, 'SW')
  latent_space['SE'] = parse_latent_space(file_name, 'SE')
  file_type = get_filetype(file_name)
  parse_success = True
  for key in latent_space:
    if latent_space[key] == None:
      parse_success = False
  if parse_success == False:
    print('error')
    print('parse result: %s' %(latent_space))
  else:
    print('success')
    record = {
      'soundSpace': sound_space_id,
      'uploadPath': GOOGLE_STORAGE_UPLOAD_PATH + '/' + sound_space_id,
      'fileName': file_name,
      'type': file_type,
      'latentSpaceNW': latent_space['NW'],
      'latentSpaceNE': latent_space['NE'],
      'latentSpaceSW': latent_space['SW'],
      'latentSpaceSE': latent_space['SE']
    }
    print('uploading...')

    file = {
      'file': open(file_path + '/' + file_name, 'rb')
    }

    res = requests.post(API + '/files', files=file, data=record)
    return(res.json())

def bulk_upload():
	record = {
		'name': config['name'],
		'user': config['user'],
		'dimensions': 4,
		'resolution': config['resolution'],
		'labels': {
			'NW': config['labels']['NW'][0],
			'NE': config['labels']['NE'][0],
			'SW': config['labels']['SW'][0],
			'SE': config['labels']['SE'][0]
		}
	}
	res = requests.post(API + '/sound-spaces', json=record)
	res_data = res.json()
	if 'err' in res_data:
		print('error creating sound-space with API')
		status = 'error'
	else:
		sound_space_id = res_data['_id']
		print('sound-space created with ID: %s' %(sound_space_id))
		num_errors = 0
		for file_name in os.listdir(FILE_PATH):
			print('file_name: %s' %(file_name))
			res = upload_sound(FILE_PATH, file_name, sound_space_id)
			if 'err' in res:
				print('error')
				num_errors += 1
			else:
				print('success')

def init():
	print('init')

if __name__ == '__main__':
	print('============================')
	print('JOB:%s:START' %(JOB_NAME))
	print('============================')
	
	init()
	bulk_upload()

	print('===============================')
	print('JOB:%s:COMPLETE' %(JOB_NAME))
	print('===============================')