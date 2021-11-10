'''
under construction
'''

from glob import glob
from json import dumps, loads

if __name__ == '__main__':
	glob('build/SegmentationClassPNG/*')
	with open('_internal/CUH-Datasetmeta.json', 'w', encoding='utf-8') as f:
		f.write(loads())