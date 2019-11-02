import os
import json
import re

JOB_NAME = 'PARSE-FOLDER'
FILE_PATH = './grid_4'
PITCH = [60]

def copy_file(file):
  match = re.findall(r'_(...)', file)
  name = 'gen_NW_' +  match[2] + '_NE_' + match[3] + '_SE_' + match[4] + '_SW_' + match[5] + '.mp3'
  print('copy: %s' %(name))
  os.rename(FILE_PATH + '/input/' + file, FILE_PATH + '/output/' + name)
  
def parse_folder():
  print('copying...')
  for file in os.listdir(FILE_PATH + '/input'):
    if 'pitch_' + str(PITCH[0]) in file: 
      print('file: %s' %(file))
      copy_file(file)

def init():
	print('init')

if __name__ == '__main__':
	print('============================')
	print('JOB:%s:START' %(JOB_NAME))
	print('============================')
	
	init()
	parse_folder()

	print('===============================')
	print('JOB:%s:COMPLETE' %(JOB_NAME))
	print('===============================')