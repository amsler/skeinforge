"""
Boolean geometry dictionary object.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.manipulation_evaluator_tools import matrix
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import xml_simple_writer
import cStringIO


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	evaluate.processArchivable( Dictionary, xmlElement, xmlProcessor )


class Dictionary:
	"A dictionary object."
	def __init__( self ):
		"Add empty lists."
		self.archivableObjects = []
		self.xmlElement = None

	def __repr__( self ):
		"Get the string representation of this object info."
		output = xml_simple_writer.getBeginGeometryXMLOutput( self.xmlElement )
		self.addXML( 1, output )
		return xml_simple_writer.getEndGeometryXMLString( output )

	def addXML( self, depth, output ):
		"Add xml for this object."
		attributeCopy = {}
		if self.xmlElement != None:
			attributeCopy = evaluate.getEvaluatedDictionary( [], self.xmlElement )
		euclidean.removeListFromDictionary( attributeCopy, matrix.getMatrixKeys() )
		euclidean.removeTrueFromDictionary( attributeCopy, 'visible' )
		innerOutput = cStringIO.StringIO()
		self.addXMLInnerSection( depth + 1, innerOutput )
		self.addXMLArchivableObjects( depth + 1, innerOutput )
		xml_simple_writer.addBeginEndInnerXMLTag( attributeCopy, self.getXMLClassName(), depth, innerOutput.getvalue(), output )

	def addXMLArchivableObjects( self, depth, output ):
		"Add xml for this object."
		xml_simple_writer.addXMLFromObjects( depth, self.archivableObjects, output )

	def addXMLInnerSection( self, depth, output ):
		"Add xml section for this object."
		pass

	def createShape( self ):
		"Create the shape."
		pass

	def getAttributeDictionary( self ):
		"Get attribute table."
		if self.xmlElement == None:
			return {}
		return self.xmlElement.attributeDictionary

	def getComplexPathLists( self ):
		"Get complex path lists."
		complexPathLists = []
		for archivableObject in self.archivableObjects:
			complexPathLists.append( euclidean.getComplexPaths( archivableObject.getPaths() ) )
		return complexPathLists

	def getMatrixChainTetragrid( self ):
		"Get the matrix chain tetragrid."
		return self.xmlElement.parent.object.getMatrixChainTetragrid()

	def getPaths( self ):
		"Get all paths."
		paths = []
		for archivableObject in self.archivableObjects:
			paths += archivableObject.getPaths()
		return paths

	def getType( self ):
		"Get type."
		return self.__class__.__name__

	def getVertices( self ):
		"Get all vertices."
		return []

	def getVisible( self ):
		"Get visible."
		return False

	def getXMLClassName( self ):
		"Get xml class name."
		return self.__class__.__name__.lower()

	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object info."
		pass
