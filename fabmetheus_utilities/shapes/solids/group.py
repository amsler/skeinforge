"""
Boolean geometry group of solids.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.shapes.shape_tools.dictionary import Dictionary
from fabmetheus_utilities.shapes.shape_tools import path
from fabmetheus_utilities.shapes.shape_utilities import evaluate
from fabmetheus_utilities import euclidean
from fabmetheus_utilities.shapes.shape_tools import matrix4x4
from fabmetheus_utilities import xml_simple_parser


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def convertXMLElement( geometryOutput, xmlElement, xmlProcessor ):
	"Convert the xml element to a group xml element."
	xmlProcessor.createChildren( geometryOutput, xmlElement )

def convertXMLElementRenameByPaths( geometryOutput, xmlElement, xmlProcessor ):
	"Convert the xml element to a group xml element and add paths."
	xmlElement.className = 'group'
	for geometryOutputChild in geometryOutput:
		pathElement = xml_simple_parser.XMLElement().getByParent( xmlElement )
		path.convertXMLElementRename( geometryOutputChild, pathElement, xmlProcessor )

def processShape( archivableClass, xmlElement, xmlProcessor ):
	"Get any new elements and process the shape."
	if xmlElement == None:
		return
	archivableObject = evaluate.getArchivableObject( archivableClass, xmlElement )
	matrix4x4.setXMLElementDictionaryToOtherElementDictionary( xmlElement, xmlElement.object.matrix4X4, xmlElement )
	xmlProcessor.processChildren( xmlElement )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	processShape( Group, xmlElement, xmlProcessor )


class Group( Dictionary ):
	"A group."
	def __init__( self ):
		"Add empty lists."
		Dictionary.__init__( self )
		self.matrix4X4 = matrix4x4.Matrix4X4()

	def addXMLInnerSection( self, depth, output ):
		"Add xml inner section for this object."
		if self.matrix4X4 != None:
			self.matrix4X4.addXML( depth, output )
		self.addXMLSection( depth, output )

	def addXMLSection( self, depth, output ):
		"Add the xml section for this object."
		pass

	def getLoops( self, importRadius, z ):
		"Get loops sliced through shape."
		visibleObjects = evaluate.getVisibleObjects( self.archivableObjects )
		loops = []
		for visibleObject in visibleObjects:
			loops += visibleObject.getLoops( importRadius, z )
		return loops

	def getMatrixChain( self ):
		"Get the matrix chain."
		return self.matrix4X4.getOtherTimesSelf( self.xmlElement.parent.object.getMatrixChain() )

	def getVertices( self ):
		"Get all vertices."
		return evaluate.getVerticesFromArchivableObjects( self.archivableObjects )

	def getVisible( self ):
		"Get visible."
		return euclidean.getBooleanFromDictionary( self.getAttributeDictionary(), 'visible' )
