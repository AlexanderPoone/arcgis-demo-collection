from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from io import BytesIO
from json import dumps
from math import pi, sinh, asinh, tan, atan, degrees, radians
from os import environ, mkdir, remove
from os.path import abspath, basename, dirname
from PIL import Image
from pyproj import Proj
from pyproj.transformer import Transformer
from re import findall
from subprocess import run, check_output, DEVNULL
from sys import argv, path
from tqdm import tqdm

print(dirname(argv[0]))
print(argv[2])

if argv[2][-1] == '\\' or argv[2][-1] == '/':
	argv[2] = argv[2][:-1]

#path=[abspath('GDAL/bin')]
environ['GDAL_DATA'] = abspath(f'{dirname(argv[0])}/.convert/data')
print(environ['GDAL_DATA'])

#argv = ['', '_internal/DOP5000.tif']#/SVMap.tif'
info = check_output(f'{dirname(argv[0])}/.convert/bin/gdalinfo.exe "{argv[2]}"').decode('utf-8')

#print(info)
lat_deg_min, lon_deg_min = [float(x) for x in findall(r'(?<=Lower Left  \(  ).*?(?=\))',info)[0].split(',  ')]
lat_deg_max, lon_deg_max = [float(x) for x in findall(r'(?<=Upper Right \(  ).*?(?=\))',info)[0].split(',  ')]

# Get number of channels
flagalpha = '' if len(findall('Band 4',info)) == 0 else '-srcalpha'
flagwhite = '-srcnodata 255 -dstnodata 0' if int(argv[1]) == 1 else ''

#print(lon_deg_min, lat_deg_min, lon_deg_max, lat_deg_max)
transformer = Transformer.from_crs(
	"epsg:2326",
	"epsg:4326"
)

lat_deg_min, lon_deg_min = transformer.transform(lon_deg_min, lat_deg_min)
lat_deg_max, lon_deg_max = transformer.transform(lon_deg_max, lat_deg_max)
#print(lon_deg_min, lat_deg_min, lon_deg_max, lat_deg_max)

out_folder = datetime.now().strftime('%Y%m%d_%H%M%S')
mkdir(out_folder)

tuples = []
maxDict = {}

for zoom in range(10, 22):
	n = 2.0 ** zoom

	lat_rad = radians(lat_deg_min)
	ytile_min = int((lon_deg_min + 180.0) / 360.0 * n)
	xtile_max = int((1.0 - asinh(tan(lat_rad)) / pi) / 2.0 * n)

	lat_rad = radians(lat_deg_max)
	ytile_max = int((lon_deg_max + 180.0) / 360.0 * n)
	xtile_min = int((1.0 - asinh(tan(lat_rad)) / pi) / 2.0 * n)

	#print(xtile_min, xtile_max, ytile_min, ytile_max)

	# Should be parallelised
	maxDict[zoom] = [xtile_min, xtile_max, ytile_min, ytile_max]

	for x in range(xtile_min, xtile_max+1):
		for y in range(ytile_min, ytile_max+1):
			tuples.append((zoom, x, y))

	if len(tuples) > 3000:
		break

def chop(zoom, x, y):
	n = 2.0 ** zoom
	lon_deg_min2 = y / n * 360.0 - 180.0
	lat_rad = atan(sinh(pi * (1 - 2 * x / n)))
	lat_deg_max2 = degrees(lat_rad)

	lon_deg_max2 = (y + 1) / n * 360.0 - 180.0
	lat_rad = atan(sinh(pi * (1 - 2 * (x + 1) / n)))
	lat_deg_min2 = degrees(lat_rad)

	bpath = f'{out_folder}/{zoom}_{x}_{y}.tif'
	#print(bpath)
	#print(f'{lon_deg_min2} {lat_deg_min2} {lon_deg_max2} {lat_deg_max2}')

	run(f'{dirname(argv[0])}/.convert/bin/gdalwarp.exe -te {lon_deg_min2} {lat_deg_min2} {lon_deg_max2} {lat_deg_max2} -s_srs EPSG:2326 -te_srs EPSG:4326 -ts 256 256 -of GTiff "{argv[2]}" "{bpath}" -overwrite {flagalpha} -dstalpha {flagwhite}', stdout=DEVNULL, stderr=DEVNULL)

	buffered = BytesIO()
	with Image.open(bpath) as im:
		im.save(buffered, format="WebP", lossless=True)
	remove(bpath)
	img_str = b64encode(buffered.getvalue()).decode('ascii')

	with open(bpath.replace('.tif','.txt'), 'w', encoding='ascii') as f:
		f.write(img_str)

	'''
	with open("image.jpg", "rb") as image_file:
		data = base64.b64encode(image_file.read())
	'''
	# Save as base64
#progress = 0
pbar = tqdm(total=len(tuples))

def callbackProgress(res):
	#global progress
	global tuples
	global pbar

	#progress += 1
	pbar.update(1)
	#print(f'{progress}/{len(tuples)} Done.')

with ThreadPoolExecutor(max_workers=40) as executor:
	futures = [executor.submit(chop, *x) for x in tuples]
	for future in futures:
		future.add_done_callback(callbackProgress)

outjson = {'title': basename(argv[2]), 'extent': [lat_deg_min, lon_deg_min, lat_deg_max, lon_deg_max], 'limits': maxDict}
with open(f'{out_folder}/content.json', 'w') as f:
	f.write(dumps(outjson))
pbar.close()
