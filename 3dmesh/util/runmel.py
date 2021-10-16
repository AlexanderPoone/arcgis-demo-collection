import sys
from subprocess import check_output, DEVNULL

if __name__ == '__main__':
	mel = f'''
	import maya.cmds as cmds
	import maya.mel as mel

	mel.eval('file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "chopchop5" -options "mo=1"  -pr  -importFrameRate true  -importTimeRange "override" "{sys.argv[1]}";')
	mel.eval('SelectAll;')
	mel.eval('if(!`exists MTselAll`) source MTprocs.mel; select -cl; MTselAll;');
	'''
