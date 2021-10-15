from glob import glob
from os import mkdir,chdir
from os.path import exists
from shutil import copytree
from pickle import dump

w=2
h=2

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

####################################
# metadata to pickle

tobepickled = {}

chdir(r'Z:\Shares\Data\OSGB')

lis = [t for t in glob('tile_*') if t[0] == 't']

for l in lis:
	with open(f'{l}/metadata.xml', 'r') as ff:
		coords = ff.read().split('\n')[5][12:-12]
		print(coords)
	x, y, _ = coords.split(',')
	x = float(x) - 800000 # + x
	y = float(y) - 800000 # + y
	tobepickled[l] = [x, y]
print(tobepickled)
with open(r'C:\addvalue_isl.pickle','wb')  as f:
	dump(tobepickled,f)