from glob import glob
from os.path import expanduser
from subprocess import run

g=glob('C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgis-api-env/Scripts/conda.bat')+glob(expanduser('~/AppData/Local/ESRI/conda/envs/*/Scripts/conda.bat'))
run('"'+g[0]+'" env create --file "C:/Program Files/Preprocessing Utility for Oriented Images/environment.yml" -y')

# run('"" requirements.txt')