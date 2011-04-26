__all__ = ['euclidean', 'gcodec', 'intercircle', 'preferences', 'trianglemesh', 'vec3']

#This is required to workaround the python import bug where relative imports don't work if the module is imported as a main module.

import os
import sys

numberOfLevelsDeepInPackageHierarchy = 1
packageFilePath = os.path.abspath(__file__)
for level in range( numberOfLevelsDeepInPackageHierarchy + 1 ):
	packageFilePath = os.path.dirname( packageFilePath )
if packageFilePath not in sys.path:
	sys.path.insert( 0, packageFilePath )
