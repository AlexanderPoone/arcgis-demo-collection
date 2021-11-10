'''
under construction
'''

from glob import glob
from shutil import rmtree, copytree
from subprocess import check_output
# import labelme

if __name__ == '__main__':
	try:
		rmtree('build')
	except:
		pass

	#echo "git clone https://github.com/wkentaro/labelme.git"
	output = check_output('python "%userprofile%/Desktop/labelme/examples/semantic_segmentation/labelme2voc.py" --labels labels.txt "_internal/CUH-Dataset/JPEGImages/two" build')

	# move back the annotations to the dataset
	copytree('build/SegmentationClassPNG', '_internal/CUH-Dataset/Annotations')
	rmtree('build')