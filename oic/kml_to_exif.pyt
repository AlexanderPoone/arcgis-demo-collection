from subprocess import check_output


try:
	a = check_output('conda install -y pil piexif pyproj')
except:
	pass

from PIL import Image