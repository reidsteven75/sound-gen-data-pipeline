import os
import json
import re

JOB_NAME = 'BULK-FILE-RENAMING'
FILE_PATH = './sounds/'

def rename_file(file):
  match = re.findall(r'_(...)', file)
  name = 'gen_NW_' +  match[2] + '_NE_' + match[3] + '_SE_' + match[4] + '_SW_' + match[5] + '.mp3'
  os.rename(FILE_PATH + file, FILE_PATH + name)
  
def bulk_upload():
  print('renaming...')
  for file in os.listdir(FILE_PATH):
    print('file: %s' %(file))
    rename_file(file)

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