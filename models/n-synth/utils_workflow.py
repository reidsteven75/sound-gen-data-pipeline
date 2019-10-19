import os
import shutil
import zipfile
import re
from utils_common import *

def inject_file(util_file, job_dir):
  shutil.copy(util_file, job_dir)

def inject_config_sound(config_file, job_dir):
  shutil.copy(config_file, job_dir)
  os.rename(job_dir + '/' + config_file, job_dir + '/config-sound.json')

def inject_config_job(config_file, job_dir):
  shutil.copy(config_file, job_dir)
  os.rename(job_dir + '/' + config_file, job_dir + '/config-job.json')

def prepare_batch(dir_batches, dataset, num_batches):
  create_dir(dir_batches)
  batch_dir = dir_batches + '/' + unique_id()
  batch_size = len(get_only_files(dataset)) / num_batches

  copy_files(dataset, batch_dir)

  # create batch folders
  for i in range(0, num_batches):
    batch_folder = batch_dir + '/batch%i' % i
    create_dir(batch_folder)

  #	move files into batch folders
  batch = 0
  files = get_only_files(batch_dir) 
  for filename in files:
    target_folder = batch_dir + '/batch%i' % batch
    batch += 1
    if batch >= num_batches:
      batch = 0
    shutil.move(batch_dir + '/' + filename, target_folder)

  return batch_dir

def zip_job(source, target):

  '''
  1) zips entire job directory in 'source' directory
  2) puts zipfile in 'target' directory
  3) returns path to zip file in 'target' directory
  '''

  create_dir(target)
  zip_name = unique_id() + '.zip'
  zip_path = target + '/' + zip_name
  file_paths = [] 
  for root, directories, files in os.walk(source): 
    for filename in files: 
      filepath = os.path.join(root, filename) 
      file_paths.append(filepath)

  with zipfile.ZipFile(zip_path, 'a') as file:
    for file_to_zip in file_paths:
      arcname = file_to_zip.replace(source, '')
      file.write(file_to_zip, arcname)
    file.close()

  return(zip_path)

def parse_latent_space(string, vector):
  match = re.search(vector + r'_(...)', string)
  if match:
    return float(match.group(1))
  else:
    return None