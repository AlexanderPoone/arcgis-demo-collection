############################################
#
#   HK Island Optimisation
#
############################################

from glob import glob
from os.path import basename
from subprocess import check_output, DEVNULL

def runblender_before():
  blender_before = '''
  import bpy
  from subprocess import run
  from glob import glob
  from os.path import basename, dirname
  from pickle import load

  with open('F:/workspace/addvalue_isl.pickle','rb') as f:
    mydict = load(f)


  for f in glob('F:/workspace/partitions/*'):
    # Clear scene
    bpy.context.preferences.filepaths.use_load_ui = False
    bpy.ops.wm.read_homefile(use_empty=True)
    havesetthecontext = False
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            print("area=", area)
            if area.type == 'VIEW_3D':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.screen.screen_full_area(override)   # toggle to maximize
                bpy.ops.screen.screen_full_area()           # toggle back (must not use overridden context, else it will crash!)
                havesetthecontext = True
                break

    if havesetthecontext:
        rrr = bpy.ops.object.select_all(action='DESELECT')
        print("select_all result:", rrr)
        print(">>>>>>>>>> bpy.context:", bpy.context)
        print(">>>>>>>>>> bpy.context.object:", bpy.context.object)
    else:
        print("Could not set the context to 3D View!")
    scene = bpy.context.scene

    # for obj in bpy.context.scene.objects:
    #   if 'select' in dir(obj):
    #       obj.select = True
    # bpy.ops.object.delete()


    myglob = glob(f'{f}/*/*.obj')
    for g in myglob:
        bpy.ops.import_scene.obj(filepath=g, axis_forward='Y', axis_up='Z')


        # Remove artefact vertices - BEGIN

        obj = [ob for ob in scene.objects if ob.type == 'MESH' and not ob.hide_get()][-1]
        bpy.context.view_layer.objects.active = obj
        
        # ctx = bpy.context.copy()
        # ctx['active_object'] = obj
        # ctx['selected_editable_objects'] = obj

        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type = 'VERT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')


        for v in obj.data.vertices:
            if v.co.z < -14:
                v.select = True

        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type = 'VERT')
        bpy.ops.mesh.delete(type = 'VERT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Remove artefact vertices - END

        x,y = mydict[basename(dirname(g))]
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')

        print(x,y)

        obj.location.x = obj.location.x + x
        obj.location.y = obj.location.y + y


    # Merge
    obs = [ob for ob in scene.objects if ob.type == 'MESH']
    ctx = bpy.context.copy()
    ctx['active_object'] = obs[0]
    ctx['selected_editable_objects'] = obs
    bpy.ops.object.join(ctx)

    bpy.ops.export_scene.obj(filepath=f'F:/workspace/{basename(dirname(myglob[0]))}.obj')
  '''

  with open('blend_before.py', 'w', encoding='utf-8') as f:
    f.write(mel)

  check_output('blender -t 0 -p "blend_before.py"')



'''
import maya.cmds as cmds
import maya.mel as mel
mel.eval('file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "chopchop5" -options "mo=1"  -pr  -importFrameRate true  -importTimeRange "override" "{sys.argv[1]}";')
mel.eval('SelectAll;')
mel.eval('if(!`exists MTselAll`) source MTprocs.mel; select -cl; MTselAll;');
'''
def runmel(objName):
  base = basename(objName).split('.')[0]

  mel = f'''
  file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "{base}" -options "mo=1"  -pr  -importFrameRate true  -importTimeRange "override" "{objName}";
  SelectAll;
  if(!`exists MTselAll`) source MTprocs.mel; select -cl; MTselAll;
  polyAutoProjection -lm 0 -pb 0 -ibd 1 -cm 1 -l 2 -sc 2 -o 0 -p 6 -uvSetName uvSet1 -ps 0 -ws 0 {base}:Mesh.f;
  file -force -options "" -type "FBX export" -pr -ea "C:/Users/Alexandre Poon/Desktop/{base}.fbx";
  '''
  # Save as FBX

  with open('uvfix.mel', 'w', encoding='utf-8') as f:
    f.write(mel)

  out = check_output('maya -batch -file blank.ma -script uvfix.mel') # 'maya -batch -file blank.ma -command uvfix.mel')
  print(f'runmel(): {out}')


def runblender_after():
  blender_after = f'''import bpy
from os.path import basename, expanduser

bpy.data.objects.remove(bpy.data.objects['Cube'])
bpy.data.objects.remove(bpy.data.objects['Light'])
bpy.data.objects.remove(bpy.data.objects['Camera'])

fbxPath = 'C:/Users/Alex/Desktop/tile_10_13.fbx'
base = basename(fbxPath).split('.')[0]

bpy.ops.import_scene.fbx(filepath=fbxPath)

scene = bpy.context.scene

obj = [ob for ob in scene.objects if ob.type == 'MESH' and not ob.hide_get()][-1]
bpy.context.view_layer.objects.active = obj

obj.data.uv_layers[0].active_render = True
obj.data.uv_layers[1].active = True

bpy.context.object.scale[0] = 1
bpy.context.object.scale[1] = 1
bpy.context.object.scale[2] = 1

for material in bpy.data.materials:
    try:
        material.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 0
        material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1
    except:
        pass

bpy.ops.texture.new()
image = bpy.data.images.new(base, width=8192, height=8192)
image.filepath = expanduser(f'~/Desktop/{base}.png')
bpy.data.textures["Texture"].use_alpha = False


for x in obj.material_slots:
    mtl = x.material.node_tree.nodes.new('ShaderNodeTexImage')
    mtl.select = True
    mtl.image = image
    x.material.node_tree.nodes.active = mtl


# Bake
obj.select_set(True)
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'

bpy.context.scene.cycles.bake_type = 'DIFFUSE'
bpy.context.scene.render.bake.use_pass_direct = False
bpy.context.scene.render.bake.use_pass_indirect = False

bpy.context.scene.render.bake.use_clear = False

bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_clear=False)

# Bake
image.save()
#image.save_render(f'{base}.png')

for material in bpy.data.materials:
  material.user_clear()
  bpy.data.materials.remove(material)

for a in range(500):
  bpy.ops.object.material_slot_remove()

# Test below
bpy.ops.material.new()
mtl=bpy.data.materials['Material']
bpy.context.object.data.materials.append(mtl)
imn = mtl.node_tree.nodes.new('ShaderNodeTexImage')
imn.image = image
bsdf = mtl.node_tree.nodes['Principled BSDF']
mtl.node_tree.links.new(bsdf.inputs['Base Color'], imn.outputs['Color'])
# obj.active_material = bpy.data.materials['Material']

# Export
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
bpy.ops.export_scene.obj(filepath=expanduser(f'~/Desktop/{base}.obj'))
  '''
  check_output('blender -t 0 -p ')

                     
if __name__ == '__main__':        
    # pipeline
    runblender_before()
    for objName in glob():
      runmel(objName)
    runblender_after()
 
