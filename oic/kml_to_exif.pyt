##############################################
#
#    KML to EXIF
#
#    Author:        Alex Poon (Esri China (H.K.))
#    Date:          Sep 28, 2021
#    Last update:   Sep 28, 2021
#
##############################################
import arcpy
from subprocess import check_output

class Toolbox(object):
    def __init__(self):
        self.label =  "KML to EXIF"
        self.alias  = "KMLToExif"

        # List of tool classes associated with this toolbox
        self.tools = [KMLToExif] 

class KMLToExif(object):
    def __init__(self):
        self.label       = "KML to EXIF"
        self.description = "Propagate EXIF metadata of image files from a KML file."

    def getParameterInfo(self):
		try:
			a = check_output('conda install -y pil piexif pyproj')
		except:
			pass

		from PIL import Image