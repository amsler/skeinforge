"""
Boolean geometry group of solids.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_tools.dictionary import Dictionary
from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities import euclidean
from fabmetheus_utilities.solids.solid_tools import matrix4x4


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def convertXMLElement( geometryOutput, xmlElement ):
	"Convert the xml element to a group xml element."
	xmlElement.getRootElement().xmlProcessor.createChildren( geometryOutput, xmlElement )

def processShape( archivableClass, xmlElement ):
	"Get any new elements and process the shape."
	if xmlElement == None:
		return
	archivableObject = geomancer.getArchivableObject( archivableClass, xmlElement )
	matrix4x4.setXMLElementMatrixToMatrixAttributeDictionary( xmlElement, xmlElement.object.matrix4X4, xmlElement )
	xmlElement.getRootElement().xmlProcessor.processChildren( xmlElement )

def processXMLElement( xmlElement ):
	"Process the xml element."
	processShape( Group, xmlElement )


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
		visibleObjects = geomancer.getVisibleObjects( self.archivableObjects )
		loops = []
		for visibleObject in visibleObjects:
			loops += visibleObject.getLoops( importRadius, z )
		return loops

	def getMatrixChain( self ):
		"Get the matrix chain."
		return self.matrix4X4.getOtherTimesSelf( self.xmlElement.parent.object.getMatrixChain() )

	def getVertices( self ):
		"Get all vertices."
		return geomancer.getVerticesFromArchivableObjects( self.archivableObjects )

	def getVisible( self ):
		"Get visible."
		return euclidean.getBooleanFromDictionary( self.getAttributeDictionary(), 'visible' )
