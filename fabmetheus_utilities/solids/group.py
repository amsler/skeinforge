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


def processXMLElement( xmlElement ):
	"Process the xml element."
	geomancer.processShape( Group, xmlElement )


class Group( Dictionary ):
	"A group."
	def __init__( self ):
		"Add empty lists."
		Dictionary.__init__( self )
		self.matrix4X4 = matrix4x4.Matrix4X4()
		self.visible = True

	def addXMLInnerSection( self, depth, output ):
		"Add xml inner section for this object."
		if self.matrix4X4 != None:
			self.matrix4X4.addXML( depth, output )
		self.addXMLSection( depth, output )

	def addXMLSection( self, depth, output ):
		"Add the xml section for this object."
		pass

	def createShape( self, matrixChain ):
		"Create the shape."
		newMatrix4X4 = self.matrix4X4.getOtherTimesSelf( matrixChain )
		visibleObjects = geomancer.getVisibleObjects( self.archivableObjects )
		for visibleObject in visibleObjects:
			visibleObject.createShape( newMatrix4X4 )
		self.bottom = 999999999.9
		self.top = - 999999999.9
		for visibleObject in visibleObjects:
			self.bottom = min( self.bottom, visibleObject.bottom )
			self.top = max( self.top, visibleObject.top )

	def getLoops( self, importRadius, z ):
		"Get loops sliced through shape."
		visibleObjects = geomancer.getVisibleObjects( self.archivableObjects )
		loops = []
		for visibleObject in visibleObjects:
			loops += visibleObject.getLoops( importRadius, z )
		return loops

	def getVertices( self ):
		"Get all vertices."
		vertices = []
		for visibleObject in geomancer.getVisibleObjects( self.archivableObjects ):
			vertices += visibleObject.getVertices()
		return vertices

	def getVisible( self ):
		"Get visible."
		attributeDictionary = self.getAttributeDictionary()
		if 'visible' not in attributeDictionary:
			return True
		return euclidean.getBooleanFromValue( attributeDictionary[ 'visible' ] )
