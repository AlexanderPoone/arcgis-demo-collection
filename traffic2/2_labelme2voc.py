'''
LabelMe to VOC2012
'''

from glob import glob
from json import loads, dumps
from os import remove
from os.path import basename, exists
from shutil import move, rmtree, copytree
from subprocess import check_output

if __name__ == '__main__':
	if exists('build'):
		rmtree('build')

	if exists('_internal/CUH-Dataset/Annotations'):
		rmtree('_internal/CUH-Dataset/Annotations')

	for f in glob('_internal/CUH-Dataset/JPEGImages/*/'):
		try:
			# TODO: Create temporary label.txt from all json files
			track_labels = set()

			for j in glob(f'{f}*.json'):
				with open(j, 'r') as j2:
					j3 = loads(j2.read())
				#print([j4['label'] for j4 in j3['shapes']])
				for j4 in j3['shapes']:
					track_labels.add(j4['label'])

			track_labels = sorted(track_labels)
			track_labels_txt = '__ignore__\n_background_\n' + '\n'.join(track_labels)
			print(track_labels_txt)

			with open(f'{f}label.txt', 'w') as j5:
				j5.write(track_labels_txt)


			f2 = f.replace("\\","/")[:-1]
			#echo "git clone https://github.com/wkentaro/labelme.git"
			print(check_output(f'python "_internal/labelme/examples/semantic_segmentation/labelme2voc.py" --labels "{f}label.txt" "{f2}" build'))

			remove(f'{f}label.txt')

			# move back the annotations to the dataset
			move('build/SegmentationClassPNG', f'_internal/CUH-Dataset/Annotations/{basename(f2)}')
			rmtree('build')
		except Exception as e:
			print(e)
			pass
		print('---------------------------------------')