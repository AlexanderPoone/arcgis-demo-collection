import sys
from subprocess import check_output, DEVNULL

if __name__ == '__main__':
	'''
	import maya.cmds as cmds
	import maya.mel as mel


	mel.eval('file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "chopchop5" -options "mo=1"  -pr  -importFrameRate true  -importTimeRange "override" "{sys.argv[1]}";')
	mel.eval('SelectAll;')
	mel.eval('if(!`exists MTselAll`) source MTprocs.mel; select -cl; MTselAll;');
	'''
	
        mel = f'''
	file -import -type "OBJ"  -ignoreVersion -ra true -mergeNamespacesOnClash false -namespace "chopchop5" -options "mo=1"  -pr  -importFrameRate true  -importTimeRange "override" "{sys.argv[1]}";
	SelectAll;
	if(!`exists MTselAll`) source MTprocs.mel; select -cl; MTselAll;
	'''
	with open('uvfix.mel', 'w', encoding='utf-8') as f:
		f.write(mel)
	out = 'maya -batch -file blank.ma -command uvfix.mel' # 'maya -batch -file blank.ma -command uvfix.mel'
