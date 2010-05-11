"""
Boolean geometry sphere.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.solids import cube
from fabmetheus_utilities.solids import group
from fabmetheus_utilities.solids import trianglemesh


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def processXMLElement( xmlElement ):
	"Process the xml element."
	group.processShape( Sphere, xmlElement )


class Sphere( cube.Cube ):
	"A sphere object."
	def createShape( self ):
		"Create the shape."
		maximumRadius = max( max( self.radiusX, self.radiusY ), self.radiusZ )
		numberOfInBetweens = max( int( 0.25 * geomancer.getSides( maximumRadius, self.xmlElement ) ), 1 )
		numberOfDivisions = numberOfInBetweens + 1
		bottomLeft = complex( - 1.0, - 1.0 )
		topRight = complex( 1.0, 1.0 )
		extent = topRight - bottomLeft
		elementExtent = extent / numberOfDivisions
		grid = []
		for rowIndex in xrange( numberOfDivisions + 1 ):
			row = []
			grid.append( row )
			for columnIndex in xrange( numberOfDivisions + 1 ):
				point = complex( elementExtent.real * float( columnIndex ), elementExtent.real * float( rowIndex ) ) + bottomLeft
				row.append( point )
		indexedGridBottom = trianglemesh.getAddIndexedGrid( grid, self.vertices, - 1.0 )
		indexedGridBottomLoop = trianglemesh.getIndexedLoopFromIndexedGrid( indexedGridBottom )
		indexedLoops = [ indexedGridBottomLoop ]
		zList = []
		for zIndex in xrange( 1, numberOfDivisions ):
			z = elementExtent.real * float( zIndex ) + bottomLeft.real
			zList.append( z )
		gridLoop = []
		for vertex in indexedGridBottomLoop:
			gridLoop.append( vertex.dropAxis( 2 ) )
		indexedLoops += trianglemesh.getAddIndexedLoops( gridLoop, self.vertices, zList )
		indexedGridTop = trianglemesh.getAddIndexedGrid( grid, self.vertices, 1.0 )
		indexedLoops.append( trianglemesh.getIndexedLoopFromIndexedGrid( indexedGridTop ) )
		trianglemesh.addPillarFromConvexLoopsGrids( self.faces, [ indexedGridBottom, indexedGridTop ], indexedLoops )
		for vertex in self.vertices:
			vertex.normalize()
			vertex.x *= self.radiusX
			vertex.y *= self.radiusY
			vertex.z *= self.radiusZ

	def setToObjectAttributeDictionary( self ):
		"Set the shape of this carvable object info."
		radius = geomancer.getEvaluatedFloatOne( 'radius', self.xmlElement )
		self.radiusX = geomancer.getEvaluatedFloatDefault( radius, 'radiusx', self.xmlElement )
		self.radiusY = geomancer.getEvaluatedFloatDefault( radius, 'radiusy', self.xmlElement )
		self.radiusZ = geomancer.getEvaluatedFloatDefault( radius, 'radiusz', self.xmlElement )
		self.xmlElement.attributeDictionary[ 'radiusx' ] = self.radiusX
		self.xmlElement.attributeDictionary[ 'radiusy' ] = self.radiusY
		self.xmlElement.attributeDictionary[ 'radiusz' ] = self.radiusZ
		self.createShape()
