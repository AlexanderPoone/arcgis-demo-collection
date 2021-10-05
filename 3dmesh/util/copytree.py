from glob import glob
from os import mkdir,chdir
from os.path import exists
from shutil import copytree

w=4
h=3

chdir('Z:/Shares/Data/OBJ')
cnt=0
for x in range(3, 61, w):
	for y in range(0, 34, h):
		folderToCopy = []
		for z in range(x, x+w):
			for zz in range(y, y+h):
				folder = f'tile_{z}_{zz}'
				if exists(folder):
					folderToCopy.append(folder)
		if len(folderToCopy) > 0:
			mkdir(f'{cnt}')
			for f in folderToCopy:
				copytree(f'{f}', f'{cnt}/{f}')
			cnt+=1