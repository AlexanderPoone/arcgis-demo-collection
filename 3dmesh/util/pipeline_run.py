from subprocess import check_output, DEVNULL

def runblender_before():
  blender_before = '''
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
  '''

'''
import maya.cmds as cmds
import maya.mel as mel
mel.eval('file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "chopchop5" -options "mo=1"  -pr  -importFrameRate true  -importTimeRange "override" "{sys.argv[1]}";')
mel.eval('SelectAll;')
mel.eval('if(!`exists MTselAll`) source MTprocs.mel; select -cl; MTselAll;');
'''
def runmel(blendName):
  mel = f'''
  file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "chopchop5" -options "mo=1"  -pr  -importFrameRate true  -importTimeRange "override" "{blendName}";
  SelectAll;
  if(!`exists MTselAll`) source MTprocs.mel; select -cl; MTselAll;
  '''
  with open('uvfix.mel', 'w', encoding='utf-8') as f:
    f.write(mel)
  out = check_output('maya -batch -file blank.ma -command uvfix.mel' # 'maya -batch -file blank.ma -command uvfix.mel')
  print(f'runmel(): {out}')

def runblender_after():
  blender_after = f'''import bpy
  # bake
  
  for material in bpy.data.materials:
      material.user_clear()
      bpy.data.materials.remove(material)

  for a in range(500):
      bpy.ops.object.material_slot_remove()
  '''
                     
if __name__ == '__main__':        
    # pipeline
    runblender_before()
    runmel()
    runblender_after()
 
