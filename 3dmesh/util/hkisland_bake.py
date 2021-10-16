############################################
#
#   Remove polygons under sea level
#
############################################

from pickle import load

import bpy
from subprocess import run
from glob import glob
from math import radians
# import arcpy
#from os import stat
from os.path import basename, dirname


mydict = load('F:/workspace/addvalue_isl.pickle')

for g in glob(f'F:/workspace/OBJ/*/*.obj'):
    obj = bpy.ops.import_scene.obj(filepath=g, axis_forward='Y', axis_up='Z')

    x,y = mydict[dirname(g)]
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
    print(obs[0].location)

    # obs[0].location.x = 0
    # obs[0].location.y = 0
    # obs[0].location.z = 0

    ############################################
    # Center to bounds, apply pickle
    ############################################


import bpy

scene = bpy.context.scene
obj = [ob for ob in scene.objects if ob.type == 'MESH' and not ob.hide_get()][0]
ctx = bpy.context.copy()
ctx['active_object'] = obj

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object
bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type = 'VERT')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')


for v in obj.data.vertices:
    if v.co.z < 0:
        v.select = True

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type = 'VERT')

############################################


import bpy
for material in bpy.data.materials:
    material.user_clear()
    bpy.data.materials.remove(material)



for a in range(500):
    bpy.ops.object.material_slot_remove()
