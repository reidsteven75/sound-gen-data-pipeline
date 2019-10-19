import os
import shutil
import uuid 
import datetime

def check_dir(dir_path):
  if os.path.exists(dir_path) and os.path.isdir(dir_path):
    if not os.listdir(dir_path):
      return({'err':'dir empty'})
    else:    
      return({'success': True})
  else:
    return({'err':'dir does not exist'})

def get_filetype(file):
  return os.path.splitext(file)[1].replace('.', '')

def get_filename(file):
  return os.path.splitext(file)[0]

def unique_id():
  return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + \
          '_' + \
          uuid.uuid4().hex[:6].upper()

def delete_dir(path):
  if (os.path.exists(path)):
    shutil.rmtree(path)

def create_dir(path):
	os.makedirs(path, exist_ok=True)

def get_only_directories(path):
	return [dI for dI in os.listdir(path) if os.path.isdir(os.path.join(path, dI))]

def get_only_files(path):
	files = []
	for file in os.listdir(path):
		if os.path.isfile(os.path.join(path, file)):
			if not file.startswith('.'):
				files.append(file)
	return files

def list_all_files(directory, extensions=None):
  for root, dirnames, filenames in os.walk(directory):
    for filename in filenames:
      base, ext = os.path.splitext(filename)
      joined = os.path.join(root, filename)
      if extensions is None or ( len(ext) and ext.lower() in extensions ):
        yield joined

def copy_files(source, target):
  create_dir(target)
  files = os.listdir(source)
  for f in files:
    if os.path.isfile(os.path.join(source, f)):
      if not os.path.isfile(target + '/' + f):
        shutil.copy(source + '/' + f, target)