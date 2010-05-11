"""
Boolean geometry cylinder.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.solids import cube
from fabmetheus_utilities.solids import group
from fabmetheus_utilities.solids import trianglemesh
from fabmetheus_utilities import euclidean
import math

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement ):
	"Process the xml element."
	group.processShape( Cylinder, xmlElement )


class Cylinder( cube.Cube ):
	"A cylinder object."
	def __init__( self ):
		"Add empty lists."
		self.radiusZ = None
		cube.Cube.__init__( self )

	def createShape( self ):
		"Create the shape."
		halfHeight = 0.5 * self.height
		polygonBottom = []
		polygonTop = []
		imaginaryRadius = self.radiusZ
		if self.radiusZ == None:
			imaginaryRadius = self.radiusY
		sides = max( int( geomancer.getSides( max( imaginaryRadius, self.radiusX ), self.xmlElement ) ), 3 )
		sideAngle = 2.0 * math.pi / float( sides )
		for side in xrange( sides ):
			angle = float( side ) * sideAngle
			unitComplex = euclidean.getWiddershinsUnitPolar( angle )
			pointBottom = complex( unitComplex.real * self.radiusX, unitComplex.imag * imaginaryRadius )
			polygonBottom.append( pointBottom )
			if self.topOverBottom > 0.0:
				polygonTop.append( pointBottom * self.topOverBottom )
		if self.topOverBottom <= 0.0:
			polygonTop.append( complex() )
		bottomTopPolygon = [ trianglemesh.getAddIndexedLoop( polygonBottom, self.vertices, - halfHeight ), trianglemesh.getAddIndexedLoop( polygonTop, self.vertices, halfHeight ) ]
		trianglemesh.addPillarFromConvexLoops( self.faces, bottomTopPolygon )
		if self.radiusZ != None:
			for vertex in self.vertices:
				oldY = vertex.y
				vertex.y = vertex.z
				vertex.z = oldY

	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object info."
		self.height = geomancer.getEvaluatedFloatOne( 'height', self.xmlElement )
		radius = geomancer.getEvaluatedFloatOne( 'radius', self.xmlElement )
		self.radiusX = geomancer.getEvaluatedFloatDefault( radius, 'radiusx', self.xmlElement )
		self.radiusY = geomancer.getEvaluatedFloatDefault( radius, 'radiusy', self.xmlElement )
		self.radiusZ = geomancer.getEvaluatedFloatDefault( radius, 'radiusz', self.xmlElement )
		self.topOverBottom = geomancer.getEvaluatedFloatOne( 'topoverbottom', self.xmlElement )
		if 'radiusz' not in self.xmlElement.attributeDictionary:
			self.radiusZ = None
		self.xmlElement.attributeDictionary[ 'height' ] = self.height
		self.xmlElement.attributeDictionary[ 'radiusx' ] = self.radiusX
		if self.radiusZ == None:
			self.xmlElement.attributeDictionary[ 'radiusy' ] = self.radiusY
		else:
			self.xmlElement.attributeDictionary[ 'radiusz' ] = self.radiusZ
		self.xmlElement.attributeDictionary[ 'topoverbottom' ] = self.topOverBottom
		self.createShape()
