"""
Polyfile is a script to choose whether the skeinforge toolchain will operate on one file or all the files in a directory.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.fabmetheus_utilities import gcodec
from skeinforge_tools.fabmetheus_utilities import settings


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getFileOrGcodeDirectory( fileName, wasCancelled, words = [] ):
	"Get the gcode files in the directory the file is in if directory setting is true.  Otherwise, return the file in a list."
	if isEmptyOrCancelled( fileName, wasCancelled ):
		return []
	if isDirectorySetting():
		return gcodec.getFilesWithFileTypeWithoutWords( 'gcode', words, fileName )
	return [ fileName ]

def getFileOrDirectoryTypes( fileName, fileTypes, wasCancelled ):
	"Get the gcode files in the directory the file is in if directory setting is true.  Otherwise, return the file in a list."
	if isEmptyOrCancelled( fileName, wasCancelled ):
		return []
	if isDirectorySetting():
		return gcodec.getFilesWithFileTypesWithoutWords( fileTypes, [], fileName )
	return [ fileName ]

def getFileOrDirectoryTypesUnmodifiedGcode( fileName, fileTypes, wasCancelled ):
	"Get the gcode files in the directory the file is in if directory setting is true.  Otherwise, return the file in a list."
	if isEmptyOrCancelled( fileName, wasCancelled ):
		return []
	if isDirectorySetting():
		return gcodec.getFilesWithFileTypesWithoutWords( fileTypes, [], fileName ) + gcodec.getUnmodifiedGCodeFiles( fileName )
	return [ fileName ]

def getNewRepository():
	"Get the repository constructor."
	return PolyfileRepository()

def isDirectorySetting():
	"Determine if the directory setting is true."
	return settings.getReadRepository( PolyfileRepository() ).directorySetting.value

def isEmptyOrCancelled( fileName, wasCancelled ):
	"Determine if the fileName is empty or the dialog was cancelled."
	return str( fileName ) == '' or str( fileName ) == '()' or wasCancelled


class PolyfileRepository:
	"A class to handle the polyfile settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_utilities.skeinforge_plugins.polyfile.html', '', self )
		self.directoryOrFileChoiceLabel = settings.LabelDisplay().getFromName( 'Directory or File Choice: ', self )
		directoryLatentStringVar = settings.LatentStringVar()
		self.directorySetting = settings.Radio().getFromRadio( directoryLatentStringVar, 'Execute All Unmodified Files in a Directory', self, False )
		self.fileSetting = settings.Radio().getFromRadio( directoryLatentStringVar, 'Execute File', self, True )
