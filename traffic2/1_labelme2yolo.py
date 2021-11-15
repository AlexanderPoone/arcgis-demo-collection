'''
under construction
'''

from glob import glob
from json import loads, dumps
from os import mkdir, remove
from os.path import basename, exists
from shutil import copy2, copytree, rmtree
from subprocess import check_output

if __name__ == '__main__':
	for f in glob('_internal/CUH-Dataset/JPEGImages/*/'):
		try:
			if not exists('_internal/CUH-Dataset/tmp'):
				mkdir('_internal/CUH-Dataset/tmp')

			copyLocation = f'_internal/CUH-Dataset/tmp/{basename(f[:-1])}'

			copytree(f, copyLocation)

			for g in glob(f'{copyLocation}/*.json'):
				with open(g, 'r+') as g2:
					g3 = loads(g2.read())

					for g4 in range(len(g3['shapes'])):
						g3['shapes'][g4]['label'] = g3['shapes'][g4]['label'].split('_')[0]

					g2.seek(0)

					g2.write(dumps(g3, indent=4))

			copy2('yolodummy/_dummy.json', f'{copyLocation}/_dummy.json')
			copy2('yolodummy/_dummy.png', f'{copyLocation}/_dummy.png')

			copyLocation2 = copyLocation.replace("\\","/")
			print(check_output(f'python "_internal/Labelme2YOLO/labelme2yolo.py" --json_dir "{copyLocation2}"'))  #python "%userprofile%/Desktop/Labelme2YOLO/labelme2yolo.py

			destFolder = f'{f}YOLODataset'
			if exists(destFolder):
				rmtree(destFolder)
			copytree(f'{copyLocation}/YOLODataset', destFolder)		
			rmtree(copyLocation)
		except Exception as e:
			print(e)
			pass
	rmtree('_internal/CUH-Dataset/tmp')
