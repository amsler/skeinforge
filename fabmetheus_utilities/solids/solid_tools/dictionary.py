"""
Boolean geometry dictionary object.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_tools import matrix4x4
from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import xml_simple_writer
import cStringIO


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement ):
	"Process the xml element."
	geomancer.processArchivable( Dictionary, xmlElement )


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
		attributeDictionaryCopy = self.getAttributeDictionary().copy()
		euclidean.removeListFromDictionary( attributeDictionaryCopy, matrix4x4.getMatrixKeys() )
		euclidean.removeTrueListFromDictionary( attributeDictionaryCopy, [ 'visible' ] )
		xml_simple_writer.addBeginXMLTag( attributeDictionaryCopy, depth, self.getXMLClassName(), output )
		self.addXMLInnerSection( depth + 1, output )
		self.addXMLArchivableObjects( depth + 1, output )
		xml_simple_writer.addEndXMLTag( depth, self.getXMLClassName(), output )

	def addXMLArchivableObjects( self, depth, output ):
		"Add xml for this object."
		xml_simple_writer.addXMLFromObjects( depth, self.archivableObjects, output )

	def addXMLInnerSection( self, depth, output ):
		"Add xml section for this object."
		pass

	def createShape( self, matrixChain ):
		"Create the shape."
		pass

	def getAttributeDictionary( self ):
		"Get attribute table."
		if self.xmlElement == None:
			return {}
		return self.xmlElement.attributeDictionary

	def getType( self ):
		"Get type."
		return self.__class__.__name__

	def getVisible( self ):
		"Get visible."
		return False

	def getXMLClassName( self ):
		"Get xml class name."
		return self.__class__.__name__.lower()

	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object info."
		pass
