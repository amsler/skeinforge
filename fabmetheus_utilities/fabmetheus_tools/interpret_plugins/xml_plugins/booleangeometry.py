"""
This page is in the table of contents.
The xml.py script is an import translator plugin to get a carving from an Art of Illusion xml file.

An import plugin is a script in the interpret_plugins folder which has the function getCarving.  It is meant to be run from the interpret tool.  To ensure that the plugin works on platforms which do not handle file capitalization properly, give the plugin a lower case name.

The getCarving function takes the file name of an xml file and returns the carving.

This example gets a triangle mesh for the xml file boolean.xml.  This example is run in a terminal in the folder which contains boolean.xml and xml.py.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import xml
>>> xml.getCarving().getCarveRotatedBoundaryLayers()
[-1.159765625, None, [[(-18.925000000000001-2.4550000000000001j), (-18.754999999999981-2.4550000000000001j)
..
many more lines of the carving
..


An xml file can be exported from Art of Illusion by going to the "File" menu, then going into the "Export" menu item, then picking the XML choice.  This will bring up the XML file chooser window, choose a place to save the file then click "OK".  Leave the "compressFile" checkbox unchecked.  All the objects from the scene will be exported, this plugin will ignore the light and camera.  If you want to fabricate more than one object at a time, you can have multiple objects in the Art of Illusion scene and they will all be carved, then fabricated together.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.solids.solid_utilities import boolean_carving
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addToNamePathDictionary( directoryPath, namePathDictionary ):
	"Add to the name path dictionary."
	pluginFileNames = gcodec.getPluginFileNamesFromDirectoryPath( directoryPath )
	for pluginFileName in pluginFileNames:
		namePathDictionary[ pluginFileName ] = os.path.join( directoryPath, pluginFileName )

def getCarvingFromParser( xmlParser ):
	"Get the carving for the parser."
	booleanGeometryElement = xmlParser.getRootElement()
	booleanGeometryElement.object = boolean_carving.BooleanGeometry()
	xmlParser.getRootElement().xmlProcessor = XMLBooleanGeometryProcessor()
	xmlParser.getRootElement().xmlProcessor.processChildren( booleanGeometryElement )
	for archivableObject in booleanGeometryElement.object.archivableObjects:
		archivableObject.createShape( None )
	return booleanGeometryElement.object

def getSolidsDirectoryPath():
	"Get the solids directory path."
	return settings.getPathInFabmetheus( os.path.join( 'fabmetheus_utilities', 'solids' ) )

def getSolidToolsDirectoryPath():
	"Get the plugins directory path."
	return os.path.join( getSolidsDirectoryPath(), 'solid_tools' )

def getToolsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( __file__, os.path.join( 'booleangeometry_utilities', 'booleangeometry_tools' ) )


class XMLBooleanGeometryProcessor():
	"A class to process xml boolean geometry elements."
	def __init__( self ):
		"Process the children of the xml element."
		self.namePathDictionary = {}
		addToNamePathDictionary( getSolidsDirectoryPath(), self.namePathDictionary )
		addToNamePathDictionary( getSolidToolsDirectoryPath(), self.namePathDictionary )
		addToNamePathDictionary( getToolsDirectoryPath(), self.namePathDictionary )

	def processChildren( self, xmlElement ):
		"Process the children of the xml element."
		for child in xmlElement.children:
			self.processXMLElement( child )

	def processXMLElement( self, xmlElement ):
		"Process the xml element."
		lowerClassName = xmlElement.className.lower()
		if lowerClassName not in self.namePathDictionary:
			return []
		pluginModule = gcodec.getModuleWithPath( self.namePathDictionary[ lowerClassName ] )
		if pluginModule == None:
			return []
		geomancer.getEvaluatedDictionary( xmlElement )
		return pluginModule.processXMLElement( xmlElement )

