"""
Meta is a script to access the plugins which handle meta information.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.fabmetheus_utilities import gcodec
from skeinforge_tools.fabmetheus_utilities import settings
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getPluginFileNames():
	"Get meta plugin file names."
	return gcodec.getPluginFileNamesFromDirectoryPath( getPluginsDirectoryPath() )

def getPluginsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( os.path.dirname( __file__ ), os.path.join( 'skeinforge_tools', 'meta_plugins' ) )

def getNewRepository():
	"Get the repository constructor."
	return MetaRepository()


class MetaRepository:
	"A class to handle the meta settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_utilities.skeinforge_meta.html', '', self )
		importantFileNames = [ 'polyfile' ]
		settings.getRadioPluginsAddPluginFrame( getPluginsDirectoryPath(), importantFileNames, getPluginFileNames(), self )
