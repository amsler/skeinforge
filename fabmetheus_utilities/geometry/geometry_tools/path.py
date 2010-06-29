"""
Face of a triangle mesh.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_tools.dictionary import Dictionary
from fabmetheus_utilities.geometry.geometry_tools import vertex
from fabmetheus_utilities.geometry.geometry_tools import matrix4x4
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities import xml_simple_writer


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def convertXMLElement( geometryOutput, xmlElement, xmlProcessor ):
	"Convert the xml element to a path xml element."
	vertex.addGeometryList( geometryOutput, xmlElement )

def convertXMLElementRename( geometryOutput, xmlElement, xmlProcessor ):
	"Convert the xml element to a path xml element."
	xmlElement.className = 'path'
	convertXMLElement( geometryOutput, xmlElement, xmlProcessor )

def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	evaluate.processArchivable( Path, xmlElement, xmlProcessor )


class Path( Dictionary ):
	"A path."
	def __init__( self ):
		"Add empty lists."
		Dictionary.__init__( self )
		self.matrix4X4 = matrix4x4.Matrix4X4()
		self.transformedVertices = None
		self.vertices = []

	def addXMLInnerSection( self, depth, output ):
		"Add the xml section for this object."
		if self.matrix4X4 != None:
			self.matrix4X4.addXML( depth, output )
		xml_simple_writer.addXMLFromVertices( depth, output, self.vertices )

	def getMatrixChain( self ):
		"Get the matrix chain."
		return self.matrix4X4.getOtherTimesSelf( self.xmlElement.parent.object.getMatrixChain() )

	def getPaths( self ):
		"Get all vertices."
		return [ self.getVertices() ]

	def getVertices( self ):
		"Get all vertices."
		if self.xmlElement == None:
			return self.vertices
		if self.transformedVertices == None:
			self.transformedVertices = matrix4x4.getTransformedVector3s( self.getMatrixChain().matrixTetragrid, self.vertices )
		return self.transformedVertices

