'''
under construction
'''

from glob import glob
from subprocess import check_output

if __name__ == '__main__':
	for f in glob('_internal/CUH-Dataset/JPEGImages/*/'):
		try:
			f2 = f.replace("\\","/")
			print(check_output(f'python "_internal/Labelme2YOLO/labelme2yolo.py" --json_dir "{f2}"'))
		except:
			pass
	#output = check_output('python "%userprofile%/Desktop/Labelme2YOLO/labelme2yolo.py')