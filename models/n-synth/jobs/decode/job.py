import json, os, subprocess
import time
import shutil
import sys
import zipfile
import numpy as np
import argparse

from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm
from itertools import product
from os.path import basename
from utils_common import *
from utils_job import *

JOB_NAME = 'DECODE'

with open('config-job.json', 'r') as infile:
  config_job = json.load(infile)

INPUT_DATASET = 'data/input'
BATCH_PATH = 'data/embeddings_batched' 
OUTPUT_PATH = 'data/audio_output'

DIR_STORAGE = config_job['dir']['storage']
DIR_ARTIFACTS = config_job['dir']['artifacts']
BATCH_SIZE = config_job['jobs']['decode']['batch_size']
SAMPLE_LENGTH = config_job['jobs']['decode']['sample_length']
DIR_CHECKPOINT = DIR_STORAGE + '/%s' %(config_job['checkpoint_name'])
CHECKPOINT_ZIP_FILE = DIR_STORAGE + '/%s.zip' %(config_job['checkpoint_name'])

def create_dir(path):
	os.makedirs(path, exist_ok=True)

def get_only_files(path):
	files = []
	for file in os.listdir(path):
		if os.path.isfile(os.path.join(path, file)):
			if not file.startswith('.'):
				files.append(file)
	return files

def init():
	print('compute: %s' %(os.environ['COMPUTE_TYPE']))
	print('python: %s' %(sys.version))
	print('current working path: %s' %(os.getcwd()))
	print('INPUT_DATASET: %s' %(INPUT_DATASET))
	print('DIR_STORAGE: %s' %(DIR_STORAGE))
	print('DIR_ARTIFACTS: %s' %(DIR_ARTIFACTS))
	print('BATCH_SIZE: %s' %(BATCH_SIZE))

	create_dir(BATCH_PATH)
	create_dir(OUTPUT_PATH)

	if (os.path.isdir(DIR_CHECKPOINT)):
		print ('checkpoint already extracted')

	else:
		print('extracting checkpoint...')

		zip_ref = zipfile.ZipFile(CHECKPOINT_ZIP_FILE, 'r')
		zip_ref.extractall(DIR_STORAGE)
		zip_ref.close()

		print('extracted')
		print(os.listdir(DIR_CHECKPOINT))

def batch_embeddings():

	print('--------------------------')
	print('START: batching embeddings')

	num_embeddings = len(os.listdir(INPUT_DATASET))
	batch_size = num_embeddings / config_job['jobs']['decode']['gpus']
	#	split the embeddings per gpu in folders
	for i in range(0, config_job['jobs']['decode']['gpus']):
		foldername = BATCH_PATH + '/batch%i' % i
		if not os.path.exists(foldername):
			os.mkdir(foldername)
		output_foldername = OUTPUT_PATH + '/batch%i' % i
		if not os.path.exists(output_foldername):
			os.mkdir(output_foldername)

	#	shuffle to the folders
	batch = 0
	for filename in os.listdir(INPUT_DATASET):

		print('debug:batch input')
		print(INPUT_DATASET)

		target_folder = BATCH_PATH + '/batch%i/' % batch
		batch += 1
		if batch >= config_job['jobs']['decode']['gpus']:
			batch = 0

		os.rename(INPUT_DATASET + '/' + filename, target_folder + filename)

		print('debug:batch output')
		print(target_folder + filename)
	
	print('RESULT: batching embeddings')
	print('---------------------------')
	print('success')

def gen_call(gpu):
	return subprocess.call(['nsynth_generate',
		'--checkpoint_path=%s/model.ckpt-200000' %(DIR_CHECKPOINT),
		'--source_path=%s/batch%i' %(BATCH_PATH, gpu),
		'--save_path=%s/batch%i' %(OUTPUT_PATH, gpu),
		'--sample_length=%s' %(SAMPLE_LENGTH),
		'--encodings=true',
		'--log=INFO',
		'--batch_size=%s' %(BATCH_SIZE)])

def generate_audio():

	print('-----------------------')
	print('START: sound generation')

	#  map calls to gpu threads
	pool = ThreadPool(config_job['jobs']['decode']['gpus'])
	results = pool.map_async(gen_call, range(config_job['jobs']['decode']['gpus']))
	while not results.ready():
		time.sleep(1)
	pool.close()
	pool.join()

	for i in range(0, config_job['jobs']['decode']['gpus']):
		source = OUTPUT_PATH + '/batch%i/' % i
		files = os.listdir(source)
		for f in files:
			print('debug:output')
			print(f)
			shutil.move(source + f, DIR_ARTIFACTS)

	print('RESULT: sound generation')
	print('------------------------')
	print('# sounds generated: %s' %(DIR_ARTIFACTS))
	print(get_only_files(DIR_ARTIFACTS))

if __name__ == '__main__':
	print('============================')
	print('JOB:%s:START' %(JOB_NAME))
	print('============================')
	
	init()
	batch_embeddings()
	generate_audio()

	print('===============================')
	print('JOB:%s:COMPLETE' %(JOB_NAME))
	print('===============================')