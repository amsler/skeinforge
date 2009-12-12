"""
This page is in the table of contents.
Analyze is a script to access the plugins which analyze a gcode file.

The plugin buttons which are commonly used are bolded and the ones which are rarely used have normal font weight.

An explanation of the gcodes is at:
http://reprap.org/bin/view/Main/Arduino_GCode_Interpreter

A gode example is at:
http://forums.reprap.org/file.php?12,file=565

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import preferences
from skeinforge_tools.meta_plugins import polyfile
import os
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addToMenu( master, menu, repository, window ):
	"Add a tool plugin menu."
	preferences.addPluginsParentToMenu( getPluginsDirectoryPath(), menu, __file__, getPluginFileNames() )

def getPluginFileNames():
	"Get analyze plugin fileNames."
	return gcodec.getPluginFileNamesFromDirectoryPath( getPluginsDirectoryPath() )

def getPluginsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( __file__, 'analyze_plugins' )

def getNewRepository():
	"Get the repository constructor."
	return AnalyzeRepository()

def writeOutput( fileName, gcodeText = '' ):
	"Analyze a gcode file."
	gcodeText = gcodec.getTextIfEmpty( fileName, gcodeText )
	pluginFileNames = getPluginFileNames()
	for pluginFileName in pluginFileNames:
		analyzePluginsDirectoryPath = getPluginsDirectoryPath()
		pluginModule = gcodec.getModuleWithDirectoryPath( analyzePluginsDirectoryPath, pluginFileName )
		if pluginModule != None:
			pluginModule.writeOutput( fileName, gcodeText )


class AnalyzeRepository:
	"A class to handle the analyze preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		preferences.addListsToRepository( 'skeinforge_tools.analyze.html', '', self )
		self.fileNameInput = preferences.FileNameInput().getFromFileName( [ ( 'Gcode text files', '*.gcode' ) ], 'Open File to be Analyzed', self, '' )
		self.analyzeLabel = preferences.LabelDisplay().getFromName( 'Open Preferences: ', self )
		importantFileNames = [ 'behold', 'skeinview', 'statistic' ]
		preferences.getDisplayToolButtonsRepository( getPluginsDirectoryPath(), importantFileNames, getPluginFileNames(), self )
		self.executeTitle = 'Analyze'

	def execute( self ):
		"Analyze button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, [], self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


def main():
	"Display the analyze dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		preferences.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
