"""
Boolean geometry group of solids.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_tools.dictionary import Dictionary
from fabmetheus_utilities.geometry.geometry_tools import path
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities import euclidean
from fabmetheus_utilities.geometry.manipulation_evaluator import matrix
from fabmetheus_utilities import xml_simple_reader


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
		pathElement = xml_simple_reader.XMLElement()
		pathElement.setParentAddToChildren(xmlElement)
		path.convertXMLElementRename( geometryOutputChild, pathElement, xmlProcessor )

def processShape(archivableClass, xmlElement, xmlProcessor):
	"Get any new elements and process the shape."
	if xmlElement == None:
		return
	archivableObject = evaluate.getArchivableObject(archivableClass, xmlElement)
	matrix.setXMLElementDictionaryToOtherElementDictionary(xmlElement, xmlElement.object.matrix4X4, 'matrix.', xmlElement)
	xmlProcessor.processChildren(xmlElement)

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	processShape(Group, xmlElement, xmlProcessor)


class Group( Dictionary ):
	"A group."
	def __init__( self ):
		"Add empty lists."
		Dictionary.__init__( self )
		self.matrix4X4 = matrix.Matrix()

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

	def getMatrixChainTetragrid(self):
		"Get the matrix chain tetragrid."
		return self.matrix4X4.getOtherTimesSelf(self.xmlElement.parent.object.getMatrixChainTetragrid()).matrixTetragrid

	def getVertices( self ):
		"Get all vertices."
		return evaluate.getVerticesFromArchivableObjects( self.archivableObjects )

	def getVisible( self ):
		"Get visible."
		return euclidean.getBooleanFromDictionary( self.getAttributeDictionary(), 'visible')
