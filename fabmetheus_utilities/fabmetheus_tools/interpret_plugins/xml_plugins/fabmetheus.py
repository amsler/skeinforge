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

from fabmetheus_utilities.shapes.shape_utilities import boolean_geometry
from fabmetheus_utilities.shapes.shape_utilities import evaluate
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
from fabmetheus_utilities import xml_simple_parser
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
	booleanGeometryElement = xmlParser.getRoot()
	booleanGeometryElement.object = boolean_geometry.BooleanGeometry()
	root = xmlParser.getRoot()
	root.xmlProcessor = XMLBooleanGeometryProcessor()
	root.xmlProcessor.processChildren( booleanGeometryElement )
	return booleanGeometryElement.object

def getManipulationDirectoryPath():
	"Get the manipulation directory path."
	return os.path.join( evaluate.getShapesDirectoryPath(), 'manipulation' )

def getManipulationPathsDirectoryPath():
	"Get the manipulation paths directory path."
	return os.path.join( evaluate.getShapesDirectoryPath(), 'manipulation_paths' )

def getManipulationShapesDirectoryPath():
	"Get the manipulation shapes directory path."
	return os.path.join( evaluate.getShapesDirectoryPath(), 'manipulation_shapes' )

def getSolidsDirectoryPath():
	"Get the plugins directory path."
	return os.path.join( evaluate.getShapesDirectoryPath(), 'solids' )

def getSolidToolsDirectoryPath():
	"Get the plugins directory path."
	return os.path.join( evaluate.getShapesDirectoryPath(), 'shape_tools' )

def getStatementsDirectoryPath():
	"Get the statements directory path."
	return os.path.join( evaluate.getShapesDirectoryPath(), 'statements' )


class XMLBooleanGeometryProcessor():
	"A class to process xml boolean geometry elements."
	def __init__( self ):
		"Initialize processor."
		self.functions = []
		self.manipulationPathDictionary = {}
		addToNamePathDictionary( getManipulationPathsDirectoryPath(), self.manipulationPathDictionary )
		self.manipulationShapeDictionary = {}
		addToNamePathDictionary( getManipulationShapesDirectoryPath(), self.manipulationShapeDictionary )
		self.namePathDictionary = {}
		addToNamePathDictionary( evaluate.getCreationDirectoryPath(), self.namePathDictionary )
		addToNamePathDictionary( getManipulationDirectoryPath(), self.namePathDictionary )
		self.namePathDictionary.update( self.manipulationPathDictionary )
		self.namePathDictionary.update( self.manipulationShapeDictionary )
		addToNamePathDictionary( getSolidsDirectoryPath(), self.namePathDictionary )
		addToNamePathDictionary( getSolidToolsDirectoryPath(), self.namePathDictionary )
		addToNamePathDictionary( getStatementsDirectoryPath(), self.namePathDictionary )

	def convertXMLElement( self, geometryOutput, xmlElement ):
		"Convert the xml element."
		geometryOutputKeys = geometryOutput.keys()
		if len( geometryOutputKeys ) < 1:
			return None
		firstKey = geometryOutputKeys[ 0 ]
		lowerClassName = firstKey.lower()
		if lowerClassName not in self.namePathDictionary:
			return None
		pluginModule = gcodec.getModuleWithPath( self.namePathDictionary[ lowerClassName ] )
		if pluginModule == None:
			return None
		xmlElement.className = lowerClassName
		return pluginModule.convertXMLElement( geometryOutput[ firstKey ], xmlElement, self )

	def createChildren( self, geometryOutput, parent ):
		"Create children for the parent."
		for geometryOutputChild in geometryOutput:
			self.convertXMLElement( geometryOutputChild, xml_simple_parser.XMLElement().getByParent( parent ) )

	def processChildren( self, xmlElement ):
		"Process the children of the xml element."
		for child in xmlElement.children:
			self.processXMLElement( child )

	def processXMLElement( self, xmlElement ):
		"Process the xml element."
		lowerClassName = xmlElement.className.lower()
		if lowerClassName not in self.namePathDictionary:
			return None
		pluginModule = gcodec.getModuleWithPath( self.namePathDictionary[ lowerClassName ] )
		if pluginModule == None:
			return None
		return pluginModule.processXMLElement( xmlElement, self )
