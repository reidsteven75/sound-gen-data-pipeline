import os
import requests
import json
import shutil
import re

from utils_common import *

API = 'http://0.0.0.0:4001/api'
ARTIFACT_DIR_TO_UPLOAD = './artifacts/2019-05-20_21-38-26_CF0A86/decode'
UPLOAD_PATH = 'test_sound_uploads/test_3'
# 5ce21e7eeceadfbba5a75431

def parse_latent_space(string, vector):
  match = re.search(vector + r'_(...)', string)
  if match:
    return float(match.group(1))
  else:
    return None

if __name__ == "__main__":
  record = {
    'name': 'funk-grid',
    'user': 'test_user',
    'dimensions': 4,
    'resolution': 6,
    'labels': {
      'NW': 'label-1',
      'NE': 'label-2',
      'SW': 'label-3',
      'SE': 'label-4',
    },
    'fileLocation': {
      'path': UPLOAD_PATH
    }
  }
  res = requests.post(API + '/sound-spaces', json=record)
  res_data = res.json()
  if 'err' in res_data:
    print('error creating sound-space with API')
  else:
    sound_space_id = res_data['_id']
    print('sound-space created with ID: %s' %(sound_space_id))
    num_errors = 0
    for file in os.listdir(ARTIFACT_DIR_TO_UPLOAD):
      if '.wav' in file:
        latent_space = {
          'NW': None,
          'NE': None,
          'SW': None,
          'SE': None
        }
        latent_space['NW'] = parse_latent_space(file, 'NW')
        latent_space['NE'] = parse_latent_space(file, 'NE')
        latent_space['SW'] = parse_latent_space(file, 'SW')
        latent_space['SE'] = parse_latent_space(file, 'SE')
        parse_success = True
        for key in latent_space:
          if latent_space[key] == None:
            parse_success = False
        if parse_success == False:
          print('[ERROR]: parsing file: %s' %(file))
          print('parse result: %s' %(latent_space))
        else:
          record = {
            'soundSpace': sound_space_id,
            'uploadPath': UPLOAD_PATH,
            'filePath': ARTIFACT_DIR_TO_UPLOAD,
            'fileName': file,
            'latentSpace': latent_space
          }
          print('uploading: %s' %(file))
          res = requests.post(API + '/files', json=record)
          res_data = res.json()
          if 'err' in res_data:
            print('error')
            num_errors += 1
          else:
            print('success')
      
      if num_errors != 0:
        print('[ERROR]: there were errors uploading files')
      else:
        print('[SUCCESS]: everything is just fine and dandy')

    