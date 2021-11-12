'''
under construction
'''

from glob import glob
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
			f2 = f.replace("\\","/")[:-1]
			#echo "git clone https://github.com/wkentaro/labelme.git"
			print(check_output(f'python "_internal/labelme/examples/semantic_segmentation/labelme2voc.py" --labels labels.txt "{f2}" build'))

			# move back the annotations to the dataset
			move('build/SegmentationClassPNG', f'_internal/CUH-Dataset/Annotations/{basename(f2)}')
			rmtree('build')
		except Exception as e:
			print(e)
			pass