import os
import sys
import subprocess
import requests
import json
import shutil
import time
import paperspace
import urllib.request
import tabulate
from functools import partial
from pydub import AudioSegment
from utils_common import *
from utils_workflow import *
from joblib import Parallel, delayed
import asyncio
from multiprocessing import Process
import concurrent.futures
from multiprocessing.dummy import Pool as ThreadPool

COMPUTE_ENVIRONMENT = os.environ['COMPUTE_ENVIRONMENT']
DATASET_TYPE = os.environ['DATASET_TYPE']

if DATASET_TYPE == 'test':
  CONFIG_WORKFLOW_FILE = 'config-workflow-test.json'
  CONFIG_SOUND_FILE = 'config-sound-test.json'
else:
  CONFIG_WORKFLOW_FILE = 'config-workflow-%s.json' %(COMPUTE_ENVIRONMENT)
  CONFIG_SOUND_FILE = 'config-sound.json'

with open(CONFIG_SOUND_FILE, 'r') as infile:
  config_sound = json.load(infile)
  
with open(CONFIG_WORKFLOW_FILE, 'r') as infile:
  config_workflow = json.load(infile)

if os.environ['HTTPS'] == True:
  HTTP = 'https://'
else:
  HTTP = 'http://'

API = HTTP + os.environ['HOST_ALIAS'] + ':' + os.environ['SERVER_PORT'] + '/api'

GOOGLE_STORAGE_UPLOAD_PATH = os.environ['GOOGLE_STORAGE_UPLOAD_PATH']
UTILS_COMMON_FILE = 'utils_common.py'
UTILS_JOB_FILE = 'utils_job.py'
ARTIFACT_ID = unique_id()
ARTIFACTS = './artifacts/' + ARTIFACT_ID
ARTIFACT_UPLOAD_PATH = GOOGLE_STORAGE_UPLOAD_PATH
ARTIFACT_TYPES = ['.wav','.mp3']
DIR_JOBS = './jobs'
JOB_ENCODE_INTERPOLATE = 'encode-interpolate'
JOB_DECODE = 'decode'
DIR_BATCHES = './batches'
DIR_ZIP = './zip'
FOLDER_DATASET_INTERPOLATIONS = '/interpolations'
FOLDER_DATASET_GENERATIONS = '/generations'
DATASET = './dataset'
STORAGE_COMMON = './storage'
if (COMPUTE_ENVIRONMENT == 'paperspace'):
  PAPERSPACE_API_KEY = config_workflow['paperspace']['api_key']
  PAPERSPACE_URL = config_workflow['paperspace']['url']

job_metrics = []
sound_space = None

def print_job_metrics(job_metrics):
  header = job_metrics[0].keys()
  rows =  [x.values() for x in job_metrics]
  print(tabulate.tabulate(rows, header, tablefmt='fancy_grid'))

def save_job_metrics(job, start, end, status):
  job_time = '{0:.2f}'.format(end - start)
  job_metrics.append({
    'job': job,
    'time':  job_time,
    'status': status
  })
  print('[%s]: %s' %(job, status))

def convert_wav_to_mp3(path, file):
  print('generating mp3...')
  file_name = get_filename(file)
  AudioSegment.from_wav(path + '/' + file).export(path + '/' + file_name + '.mp3', format='mp3')
  print('success')

def generate_mp3(job):
  print('[generate_mp3]: start')
  start = time.time()
  status = 'started'

  file_path = ARTIFACTS + '/' + job
  dir_status = check_dir(file_path)
  if 'err' in dir_status.keys():
    print(dir_status)
    status = 'error'
  else:
    for file in os.listdir(file_path):
      if '.wav' in file:
        print('file: %s' %(file))
        convert_wav_to_mp3(file_path, file)

  # job metrics
  if (status != 'error'):
    status = 'success'
  end = time.time()
  save_job_metrics('generate_mp3', start, end, status)

def run_artifact_upload(job, file, sound_space_id):
  print('parsing...')
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
  file_type = get_filetype(file)
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
      'uploadPath': ARTIFACT_UPLOAD_PATH + '/' + sound_space_id,
      'filePath': ARTIFACTS + '/' + job,
      'file': file,
      'type': file_type,
      'latentSpace': latent_space
    }
    print('uploading...')
    res = requests.post(API + '/files', json=record)
    return(res.json())

def upload_artifacts(job):

  print('[upload_artifacts]: start')

  start = time.time()
  status = 'started'

  file_path = ARTIFACTS + '/' + job
  dir_status = check_dir(file_path)
  if 'err' in dir_status.keys():
    print(dir_status)
    status = 'error'
  else:
    record = {
      'name': config_sound['name'],
      'user': config_sound['user'],
      'dimensions': 4,
      'resolution': config_sound['resolution'],
      'labels': {
        'NW': config_sound['labels']['NW'][0],
        'NE': config_sound['labels']['NE'][0],
        'SW': config_sound['labels']['SW'][0],
        'SE': config_sound['labels']['SE'][0]
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
      for file in os.listdir(file_path):
        if any(x in file for x in ARTIFACT_TYPES):
          print('file: %s' %(file))
          res = run_artifact_upload(job, file, sound_space_id)
          if 'err' in res:
            print('error')
            num_errors += 1
          else:
            print('success')
      
      global sound_space
      sound_space = sound_space_id

      if num_errors != 0:
        status = 'error'

  # job metrics
  if (status != 'error'):
    status = 'success'
  end = time.time()
  save_job_metrics('upload_artifacts', start, end, status)

def job_run(config):
  start = time.time()
  status = 'running'
  print('[%s]: %s' %(config['job'], status))

  if (COMPUTE_ENVIRONMENT == 'local'):
    p = subprocess.call(['python', 'job.py'], cwd=config['job_path'])
    # get job artifacts
    copy_files(config['job_artifacts'], config['workflow_artifacts'])

  if (COMPUTE_ENVIRONMENT == 'paperspace'):
    job_id = None
    try:
      res = paperspace.jobs.create({
        'apiKey': PAPERSPACE_API_KEY,
        'name': config['job'],
        'projectId': config['job_config_workflow']['project_id'],
        'container': config['job_config_workflow']['container'],
        'machineType': config['job_config_workflow']['machine_type'],
        'command': 'python job.py',
        'workspace': config['job_zip_path']
      })
      job_id = res['id']
    except:
      print('[ERROR]: jobs_create')
      print(sys.exc_info())
      status = 'error'
      return
    # get job artifacts
    try:
      paperspace.jobs.artifactsGet({
        'apiKey': PAPERSPACE_API_KEY,
        'jobId': job_id,
        'dest': config['workflow_artifacts']
      })
    except:
      print('[ERROR]: artifacts_get')
      print(sys.exc_info()[0])
      status = 'error'
      return
  
  # job metrics
  if (status != 'error'):
    status = 'success'
      
  end = time.time()
  save_job_metrics(config['job'], start, end, status)

def job_config(job, data_batch, i):

  status = 'configuring'
  print('[%s_%s]: %s' %(job, str(i), status))

  config = {}
  config['job'] = job + '_' + str(i)
  config['job_path'] = DIR_JOBS + '/' + job + '/job_' + str(i)
  config['job_data'] = config['job_path'] + '/data'
  config['job_artifacts'] = config['job_path'] + '/artifacts'
  config['job_config_workflow'] = config_workflow['jobs'][job]
  config['workflow_artifacts'] = ARTIFACTS + '/' + job

  # create concurrent job dir in job
  delete_dir(config['job_path'])
  create_dir(config['job_path'])

  # inject master job files
  copy_files(DIR_JOBS + '/' + job, config['job_path'])

  # inject config & utils
  inject_config_job(CONFIG_WORKFLOW_FILE, config['job_path'])
  inject_config_sound(CONFIG_SOUND_FILE, config['job_path'])
  inject_file(UTILS_COMMON_FILE, config['job_path'])
  inject_file(UTILS_JOB_FILE, config['job_path'])

  # inject data
  delete_dir(config['job_data'])
  create_dir(config['job_data'])
  copy_files(data_batch, config['job_data'] + '/' + 'input')

  if (COMPUTE_ENVIRONMENT == 'local'):
    # replicate paperspace environment
    copy_files(STORAGE_COMMON, config['job_path'] + '/storage')
    delete_dir(config['job_artifacts'])
    create_dir(config['job_artifacts'])
  
  if (COMPUTE_ENVIRONMENT == 'paperspace'):
    print('zipping job...')
    config['job_zip_path'] = zip_job(config['job_path'], DIR_ZIP)
    print('zipped like a fresh coat zipper')

  return(config)
  

def job_schedule(job, dataset):

  status = 'scheduling'
  print('[%s]: %s' %(job, status))

  job_config_workflow = config_workflow['jobs'][job]
  concurrent_jobs = job_config_workflow['concurrent_jobs']

  # job artifacts are gathered into overall workflow artifacts after
  workflow_artifacts = ARTIFACTS + '/' + job
  create_dir(workflow_artifacts)

  # batch dataset for concurrent jobs
  dataset_batch_dir = prepare_batch(DIR_BATCHES, dataset, concurrent_jobs)

  config = {}
  for i in range(int(concurrent_jobs)):
    data_batch = dataset_batch_dir + '/batch' + str(i)
    config[i] = job_config(job, data_batch, i)
  
  # run jobs in parallel
  Parallel(n_jobs=int(concurrent_jobs), verbose=10)(delayed(job_run)(config[i]) for i in range(int(concurrent_jobs)))

def run_workflow():

  job_schedule(JOB_ENCODE_INTERPOLATE, DATASET)
  job_schedule(JOB_DECODE, ARTIFACTS + '/' + JOB_ENCODE_INTERPOLATE)
  generate_mp3(JOB_DECODE)
  upload_artifacts(JOB_DECODE)

if __name__ == "__main__":
  print('~~~~~~~~~~~~~~~')
  print('N-SYNTH: START')
  print('~~~~~~~~~~~~~~~')
  print('ARTIFACT_ID: %s' %(ARTIFACT_ID))
  print('COMPUTE_ENV: %s' %(COMPUTE_ENVIRONMENT))
  print('API: %s' %(API))

  start = time.time()

  create_dir(ARTIFACTS)
  run_workflow()

  end = time.time()
  worflow_time = '{0:.2f}'.format(end - start)

  print('~~~~~~~~~~~~~~~')
  print('N-SYNTH: RESULT')
  print('~~~~~~~~~~~~~~~')
  print('ARTIFACT_ID: %s' %(ARTIFACT_ID))
  print('SOUND SPACE ID: %s' %(sound_space))
  print('ARTIFACT UPLOAD PATH: %s' %(ARTIFACT_UPLOAD_PATH))
  print('WORKFLOW TIME: ' + worflow_time)
  print('JOB METRICS: ')
  print_job_metrics(job_metrics)
  