import os
import subprocess
import sys
import zipfile

storage_dir = '/storage'
if os.environ['STORAGE_DIR']:
	storage_dir = os.environ['STORAGE_DIR']

artifacts_dir = '/artifacts'
if os.environ['ARTIFACTS_DIR']:
	artifacts_dir = os.environ['ARTIFACTS_DIR']

checkpoint_dir = storage_dir + '/all-instruments'
checkpoint_zip_file = storage_dir + '/all-instruments.zip'
output_dir = artifacts_dir
midi_file = os.getcwd() + '/input/sample.mp3'

def init():
	print("compute: %s" %(os.environ['COMPUTE_TYPE']))
	print("python version: %s" %(sys.version))
	print("storage: %s" %(storage_dir))
	print("artifacts: %s" %(artifacts_dir))
	if (os.path.isdir(checkpoint_dir)):
		print ("checkpoint already extracted")

	else:
		print("extracting checkpoint...")

		zip_ref = zipfile.ZipFile(checkpoint_zip_file, 'r')
		zip_ref.extractall(storage_dir)
		zip_ref.close()

		print("extracted")
		print(os.listdir(checkpoint_dir))

def generate():
	subprocess.call(['gansynth_generate', 
									'-ckpt_dir=%s' %(checkpoint_dir),
									'--output_dir=%s' %(output_dir),
									# '--midi_file=%s' %(midi_file),
								])

if __name__ == "__main__":
	print("============================")
	print("GAN SYNTH")
	print("-------------------")
	print("initializing...")
	init()
	print("-------------------")
	print("generating sound...")
	generate()
	print("generated")
	print("-------------------")