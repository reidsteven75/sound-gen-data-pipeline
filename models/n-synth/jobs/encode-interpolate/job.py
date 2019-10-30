import sys
import os
import subprocess
import json
import zipfile
import argparse

from tqdm import tqdm
from itertools import product
from os.path import basename
from utils_common import *
from utils_job import *

JOB_NAME = 'ENCODE-INTERPOLATE'

with open('config-job.json', 'r') as infile:
  config_job = json.load(infile)

with open('config-sound.json', 'r') as infile:
  config_sound = json.load(infile)

INPUT_DATASET = 'data/input'
DIR_EMBEDDINGS = 'data/embeddings_raw'
DIR_STORAGE = config_job['dir']['storage']
DIR_ARTIFACTS = config_job['dir']['artifacts']
BATCH_SIZE = config_job['jobs']['encode-interpolate']['batch_size']
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

	if (os.path.isdir(DIR_CHECKPOINT)):
		print ('checkpoint already extracted')

	else:
		print('extracting checkpoint...')

		zip_ref = zipfile.ZipFile(CHECKPOINT_ZIP_FILE, 'r')
		zip_ref.extractall(DIR_STORAGE)
		zip_ref.close()

		print('extracted')
		print(os.listdir(DIR_CHECKPOINT))

def compute_embeddings():

	print('-------------------------')
	print('START: compute embeddings')

	input_path = INPUT_DATASET
	output_path = DIR_EMBEDDINGS
	create_dir(output_path)

	num_input_files = len(os.listdir(input_path))

	subprocess.check_call(['nsynth_save_embeddings', 
		'--checkpoint_path=%s/model.ckpt-200000' %(DIR_CHECKPOINT), 
		'--source_path=%s' %(input_path), 
		'--save_path=%s' %(output_path), 
		'--log=ERROR',
		'--batch_size=%s' %(BATCH_SIZE)])

	num_output_files = len(get_only_files(output_path))
	print('RESULT: compute embeddings')
	print('-------------------------')
	print('# input wav files: %s' %(num_input_files))
	print('# embeddings generated: %s' %(num_output_files))
	print(get_only_files(output_path))
	
	assert num_input_files==num_output_files, '[compute_embeddings]: different quanity of files generated'

def interpolate_embeddings_2_dim():

	print('---------------------------------------')
	print('START: interpolating embeddings - 2 dim')

	input_path = DIR_EMBEDDINGS
	output_path = DIR_ARTIFACTS
	create_dir(output_path)

	grid_name = config_sound['name']
	resolution = config_sound['resolution']
	instrument_groups = [config_sound['labels']['LEFT'], config_sound['labels']['RIGHT']]
	combinations = sorted(product(*instrument_groups))
	xy_grid = make_grid(resolution)

	print('combinations')
	print(combinations)

	print('grid')
	print(xy_grid)

	#	cache all embeddings
	embeddings_lookup = {}

	for filename in os.listdir(input_path):
		if '.npy' in  filename:
			#	cache by name of sound defined in initial file
			parts = basename(filename).split('_')
			reference = parts[0]
			embeddings_lookup[reference] = np.load(input_path + '/' + filename)

	print('embeddings')
	print(embeddings_lookup)

	def get_embedding(instrument):
		return embeddings_lookup[instrument]

	def parse_weight(weight):
		return str(round(weight, 3))

	done = set()
	all_names = []
	all_embeddings = []

	for combination in tqdm(combinations):
		print('combo')
		print(combination[0])

		embedding_left = get_embedding(combination[0])
		embedding_right = get_embedding(combination[1])

		for interpolation_step in range(resolution + 1):
			weight_left = 1 - interpolation_step / resolution
			weight_right = interpolation_step / resolution
			print('weight')
			print(weight_left, weight_right)
			interpolated = embedding_left * weight_left + embedding_right * weight_right

			name = 'LEFT_' +  parse_weight(weight_left) + '_RIGHT_' + parse_weight(weight_right)
			np.save(output_path + '/' + name + '.npy', interpolated.astype(np.float32))

	num_output_files = len(get_only_files(output_path))

	print('RESULT: interpolating embeddings')
	print('--------------------------------')
	print('# interpolated embeddings generated: %s' %(num_output_files))
	print(get_only_files(output_path))


def interpolate_embeddings_4_dim():

	print('---------------------------------------')
	print('START: interpolating embeddings - 4 dim')

	input_path = DIR_EMBEDDINGS
	output_path = DIR_ARTIFACTS
	create_dir(output_path)

	#	constants and rearrangement of config_sound vars for processing
	grid_name = config_sound['name']
	resolution = config_sound['resolution']
	instrument_groups = [config_sound['labels']['NW'], config_sound['labels']['NE'], config_sound['labels']['SE'], config_sound['labels']['SW']]
	combinations = sorted(product(*instrument_groups))
	xy_grid = make_grid(resolution)

	#	cache all embeddings
	embeddings_lookup = {}

	for filename in os.listdir(input_path):
		if '.npy' in  filename:
			#	cache by name of sound defined in initial file
			parts = basename(filename).split('_')
			reference = parts[0]
			embeddings_lookup[reference] = np.load(input_path + '/' + filename)

	def get_embedding(instrument):
		return embeddings_lookup[instrument]

	def parse_weight(weight):
		return str(round(weight, 3))

	done = set()
	all_names = []
	all_embeddings = []

	for combination in tqdm(combinations):
		embeddings = np.asarray([get_embedding(instrument) for instrument in combination])
		
		for xy in xy_grid:
			weights = get_weights(xy)
			interpolated = (embeddings.T * weights).T.sum(axis=0)

			name = 'NW_' +  parse_weight(weights[0]) + '_NE_' + parse_weight(weights[1]) + '_SE_' + parse_weight(weights[2]) + '_SW_' + parse_weight(weights[3])

			#	reshape array
			# interpolated = np.reshape(interpolated, (1,) + interpolated.shape)

			np.save(output_path + '/' + name + '.npy', interpolated.astype(np.float32))
	
	num_output_files = len(get_only_files(output_path))

	print('RESULT: interpolating embeddings')
	print('--------------------------------')
	print('# interpolated embeddings generated: %s' %(num_output_files))
	print(get_only_files(output_path))

if __name__ == '__main__':
	print('============================')
	print('JOB:%s:START' %(JOB_NAME))
	print('============================')
	
	init()
	compute_embeddings()
	interpolate_embeddings_2_dim()

	print('===============================')
	print('JOB:%s:COMPLETE' %(JOB_NAME))
	print('===============================')