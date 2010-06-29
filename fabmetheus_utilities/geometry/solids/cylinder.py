"""
Boolean geometry cylinder.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.geometry.solids import cube
from fabmetheus_utilities.geometry.solids import group
from fabmetheus_utilities.geometry.solids import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement, xmlProcessor ):
	"Process the xml element."
	group.processShape( Cylinder, xmlElement, xmlProcessor )


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
		sides = max( int( evaluate.getSides( max( imaginaryRadius, self.radiusX ), self.xmlElement ) ), 3 )
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
		radius = evaluate.getVector3ByPrefix( 'radius', Vector3( 1.0, 1.0, 1.0 ), self.xmlElement )
		radius = evaluate.getVector3ThroughSizeDiameter( radius, self.xmlElement )
		self.height = evaluate.getEvaluatedFloatDefault( radius.z + radius.z, 'height', self.xmlElement )
		self.radiusX = radius.x
		self.radiusY = radius.y
		self.radiusZ = None
		self.topOverBottom = evaluate.getEvaluatedFloatOne( 'topoverbottom', self.xmlElement )
		self.xmlElement.attributeDictionary[ 'height' ] = self.height
		self.xmlElement.attributeDictionary[ 'radiusx' ] = self.radiusX
		self.xmlElement.attributeDictionary[ 'radiusy' ] = self.radiusY
		self.xmlElement.attributeDictionary[ 'topoverbottom' ] = self.topOverBottom
		self.createShape()
