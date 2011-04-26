"""
Triangle Mesh holds the faces and edges of a triangular mesh.

It can read from and write to a GNU Triangulated Surface (.gts) file.

The following examples carve the GNU Triangulated Surface file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and triangle_mesh.py.


>python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import carve
>>> carve.main()
File Screw Holder Bottom.stl is being carved.
The carved file is saved as Screw Holder Bottom_carve.gcode
It took 3 seconds to carve the file.


>>> carve.writeOutput( 'Screw Holder Bottom.stl' )
File Screw Holder Bottom.gcode is being carved.
The carved file is saved as Screw Holder Bottom_carve.gcode
It took 3 seconds to carve the file.


>>> carve.getGcode("
54 162 108 Number of Vertices,Number of Edges,Number of Faces
-5.800000000000001 5.341893939393939 4.017841892579603 Vertex Coordinates XYZ
5.800000000000001 5.341893939393939 4.017841892579603
..
many lines of GNU Triangulated Surface vertices, edges and faces
..
")

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.fabmetheus_utilities.vector3 import Vector3
from skeinforge_tools.fabmetheus_utilities import euclidean
from skeinforge_tools.fabmetheus_utilities import gcodec
from skeinforge_tools.fabmetheus_utilities import intercircle
import cmath
import cStringIO
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def addEdgePair( edgePairTable, edges, faceEdgeIndex, remainingEdgeIndex, remainingEdgeTable ):
	"Add edge pair to the edge pair table."
	if faceEdgeIndex == remainingEdgeIndex:
		return
	if not faceEdgeIndex in remainingEdgeTable:
		return
	edgePair = EdgePair().getFromIndexesEdges( [ remainingEdgeIndex, faceEdgeIndex ], edges )
	edgePairTable[ str( edgePair ) ] = edgePair

def addLoopToPointTable( loop, pointTable ):
	"Add the points in the loop to the point table."
	for point in loop:
		pointTable[ point ] = loop

def addPointsAtZ( edgePair, points, radius, vertices, z ):
	"Add point complexes on the segment between the edge intersections with z."
	carveIntersectionFirst = getCarveIntersectionFromEdge( edgePair.edges[ 0 ], vertices, z )
	carveIntersectionSecond = getCarveIntersectionFromEdge( edgePair.edges[ 1 ], vertices, z )
	intercircle.addPointsFromSegment( carveIntersectionFirst, carveIntersectionSecond, points, radius, 0.3 )

def addToZoneTable( point, shape ):
	"Add point to the zone table."
	zoneIndexFloat = point.z / shape.zoneInterval
	shape.zZoneTable[ math.floor( zoneIndexFloat ) ] = None
	shape.zZoneTable[ math.ceil( zoneIndexFloat ) ] = None

def addWithLeastLength( loops, point, shortestAdditionalLength ):
	"Insert a point into a loop, at the index at which the loop would be shortest."
	shortestLoop = None
	shortestPointIndex = None
	for loop in loops:
		if len( loop ) > 2:
			for pointIndex in xrange( len( loop ) ):
				additionalLength = getAdditionalLoopLength( loop, point, pointIndex )
				if additionalLength < shortestAdditionalLength:
					shortestAdditionalLength = additionalLength
					shortestLoop = loop
					shortestPointIndex = pointIndex
	if shortestPointIndex != None:
		afterCenterComplex = shortestLoop[ shortestPointIndex ]
		afterEndComplex = shortestLoop[ ( shortestPointIndex + 1 ) % len( shortestLoop ) ]
		isInlineAfter = isInline( point, afterCenterComplex, afterEndComplex )
		beforeCenterComplex = shortestLoop[ ( shortestPointIndex + len( shortestLoop ) - 1 ) % len( shortestLoop ) ]
		beforeEndComplex = shortestLoop[ ( shortestPointIndex + len( shortestLoop ) - 2 ) % len( shortestLoop ) ]
		isInlineBefore = isInline( point, beforeCenterComplex, beforeEndComplex )
		if isInlineAfter or isInlineBefore:
			shortestLoop.insert( shortestPointIndex, point )

def compareAreaAscending( loopArea, otherLoopArea ):
	"Get comparison in order to sort loop areas in ascending order of area."
	if loopArea.area < otherLoopArea.area:
		return - 1
	return int( loopArea.area > otherLoopArea.area )

def compareAreaDescending( loopArea, otherLoopArea ):
	"Get comparison in order to sort loop areas in descending order of area."
	if loopArea.area > otherLoopArea.area:
		return - 1
	return int( loopArea.area < otherLoopArea.area )

def getAdditionalLoopLength( loop, point, pointIndex ):
	"Get the additional length added by inserting a point into a loop."
	afterPoint = loop[ pointIndex ]
	beforePoint = loop[ ( pointIndex + len( loop ) - 1 ) % len( loop ) ]
	return abs( point - beforePoint ) + abs( point - afterPoint ) - abs( afterPoint - beforePoint )

def getBridgeDirection( belowLoops, layerLoops, layerThickness ):
	"Get span direction for the majority of the overhanging extrusion perimeter, if any."
	if len( belowLoops ) < 1:
		return None
	belowOutsetLoops = []
	overhangInset = 1.875 * layerThickness
	slightlyGreaterThanOverhang = 1.1 * overhangInset
	for loop in belowLoops:
		centers = intercircle.getCentersFromLoopDirection( True, loop, slightlyGreaterThanOverhang )
		for center in centers:
			outset = intercircle.getSimplifiedInsetFromClockwiseLoop( center, overhangInset )
			if intercircle.isLargeSameDirection( outset, center, overhangInset ):
				belowOutsetLoops.append( outset )
	bridgeRotation = complex()
	for loop in layerLoops:
		for pointIndex in xrange( len( loop ) ):
			previousIndex = ( pointIndex + len( loop ) - 1 ) % len( loop )
			bridgeRotation += getOverhangDirection( belowOutsetLoops, loop[ previousIndex ], loop[ pointIndex ] )
	if abs( bridgeRotation ) < 0.75 * layerThickness:
		return None
	else:
		bridgeRotation /= abs( bridgeRotation )
		return cmath.sqrt( bridgeRotation )

def getBridgeLoops( layerThickness, loop ):
	"Get the inset bridge loops from the loop."
	halfWidth = 1.5 * layerThickness
	slightlyGreaterThanHalfWidth = 1.1 * halfWidth
	extrudateLoops = []
	centers = intercircle.getCentersFromLoop( loop, slightlyGreaterThanHalfWidth )
	for center in centers:
		extrudateLoop = intercircle.getSimplifiedInsetFromClockwiseLoop( center, halfWidth )
		if intercircle.isLargeSameDirection( extrudateLoop, center, halfWidth ):
			if euclidean.isPathInsideLoop( loop, extrudateLoop ) == euclidean.isWiddershins( loop ):
				extrudateLoop.reverse()
				extrudateLoops.append( extrudateLoop )
	return extrudateLoops

def getCommonVertexIndex( edgeFirst, edgeSecond ):
	"Get the vertex index that both edges have in common."
	for edgeFirstVertexIndex in edgeFirst.vertexIndexes:
		if edgeFirstVertexIndex == edgeSecond.vertexIndexes[ 0 ] or edgeFirstVertexIndex == edgeSecond.vertexIndexes[ 1 ]:
			return edgeFirstVertexIndex
	print( "Inconsistent GNU Triangulated Surface" )
	print( edgeFirst )
	print( edgeSecond )
	return 0

def getCarveIntersectionFromEdge( edge, vertices, z ):
	"Get the complex where the carve intersects the edge."
	firstVertex = vertices[ edge.vertexIndexes[ 0 ] ]
	firstVertexComplex = firstVertex.dropAxis( 2 )
	secondVertex = vertices[ edge.vertexIndexes[ 1 ] ]
	secondVertexComplex = secondVertex.dropAxis( 2 )
	zMinusFirst = z - firstVertex.z
	up = secondVertex.z - firstVertex.z
	return zMinusFirst * ( secondVertexComplex - firstVertexComplex ) / up + firstVertexComplex

def getCommonVertexIndex( edgeFirst, edgeSecond ):
	"Get the vertex index that both edges have in common."
	for edgeFirstVertexIndex in edgeFirst.vertexIndexes:
		if edgeFirstVertexIndex == edgeSecond.vertexIndexes[ 0 ] or edgeFirstVertexIndex == edgeSecond.vertexIndexes[ 1 ]:
			return edgeFirstVertexIndex
	print( "Inconsistent GNU Triangulated Surface" )
	print( edgeFirst )
	print( edgeSecond )
	return 0

def getDoubledRoundZ( overhangingSegment, segmentRoundZ ):
	"Get doubled plane angle around z of the overhanging segment."
	endpoint = overhangingSegment[ 0 ]
	roundZ = endpoint.point - endpoint.otherEndpoint.point
	roundZ *= segmentRoundZ
	if abs( roundZ ) == 0.0:
		return complex()
	if roundZ.real < 0.0:
		roundZ *= - 1.0
	roundZLength = abs( roundZ )
	return roundZ * roundZ / roundZLength

def getEmptyZ( shape, z ):
	"Get the first z which is not in the zone table."
	zoneIndex = round( z / shape.zoneInterval )
	if zoneIndex not in shape.zZoneTable:
		return z
	zoneAround = 1
	while 1:
		zoneDown = zoneIndex - zoneAround
		if zoneDown not in shape.zZoneTable:
			return zoneDown * shape.zoneInterval
		zoneUp = zoneIndex + zoneAround
		if zoneUp not in shape.zZoneTable:
			return zoneUp * shape.zoneInterval
		zoneAround += 1

def getInclusiveLoops( allPoints, corners, importRadius, isInteriorWanted = True ):
	"Get loops which include most of the points."
	centers = intercircle.getCentersFromPoints( allPoints, importRadius )
	clockwiseLoops = []
	inclusiveLoops = []
	tinyRadius = 0.03 * importRadius
	for loop in centers:
		if len( loop ) > 2:
			insetPoint = getInsetPoint( loop, tinyRadius )
			if getNumberOfOddIntersectionsFromLoops( insetPoint, centers ) % 4 == 0:
				inclusiveLoops.append( loop )
			else:
				clockwiseLoops.append( loop )
	pointTable = {}
	for inclusiveLoop in inclusiveLoops:
		addLoopToPointTable( inclusiveLoop, pointTable )
	if not isInteriorWanted:
		return getLoopsWithCorners( corners, importRadius, inclusiveLoops, pointTable )
	clockwiseLoops = getLoopsInOrderOfArea( compareAreaDescending, clockwiseLoops )
	for clockwiseLoop in clockwiseLoops:
		if getOverlapRatio( clockwiseLoop, pointTable ) < 0.1:
			inclusiveLoops.append( clockwiseLoop )
			addLoopToPointTable( clockwiseLoop, pointTable )
	return getLoopsWithCorners( corners, importRadius, inclusiveLoops, pointTable )

def getInsetPoint( loop, tinyRadius ):
	"Get the inset vertex."
	pointIndex = getWideAnglePointIndex( loop )
	point = loop[ pointIndex % len( loop ) ]
	afterPoint = loop[ ( pointIndex + 1 ) % len( loop ) ]
	beforePoint = loop[ ( pointIndex - 1 ) % len( loop ) ]
	afterSegmentNormalized = euclidean.getNormalized( afterPoint - point )
	beforeSegmentNormalized = euclidean.getNormalized( beforePoint - point )
	afterClockwise = complex( afterSegmentNormalized.imag, - afterSegmentNormalized.real )
	beforeWiddershins = complex( - beforeSegmentNormalized.imag, beforeSegmentNormalized.real )
	midpoint = afterClockwise + beforeWiddershins
	midpointNormalized = midpoint / abs( midpoint )
	return point + midpointNormalized * tinyRadius

def getLoopsFromCorrectMesh( edges, faces, vertices, z ):
	"Get loops from a carve of a correct mesh."
	remainingEdgeTable = getRemainingEdgeTable( edges, vertices, z )
	remainingValues = remainingEdgeTable.values()
	for edge in remainingValues:
		if len( edge.faceIndexes ) < 2:
			print( 'This should never happen, there is a hole in the triangle mesh, each edge should have two faces.' )
			print( edge )
			print( "Something will still be printed, but there is no guarantee that it will be the correct shape." )
			print( 'Once the gcode is saved, you should check over the layer with a z of:' )
			print( z )
			return []
	loops = []
	while isPathAdded( edges, faces, loops, remainingEdgeTable, vertices, z ):
		pass
	for loopIndex in xrange( len( loops ) - 1 ):
		loop = loops[ loopIndex ]
		if euclidean.isLoopIntersectingLoops( loop, loops[ loopIndex + 1 : ] ):
			print( 'This should never happen, the triangle mesh slice intersects itself.' )
			print( "Something will still be printed, but there is no guarantee that it will be the correct shape." )
			print( 'Once the gcode is saved, you should check over the layer with a z of:' )
			print( z )
			return []
	return loops
#	untouchables = []
#	for boundingLoop in boundingLoops:
#		if not boundingLoop.isIntersectingList( untouchables ):
#			untouchables.append( boundingLoop )
#	if len( untouchables ) < len( boundingLoops ):
#		print( 'This should never happen, the carve layer intersects itself. Something will still be printed, but there is no guarantee that it will be the correct shape.' )
#		print( 'Once the gcode is saved, you should check over the layer with a z of:' )
#		print( z )
#	remainingLoops = []
#	for untouchable in untouchables:
#		remainingLoops.append( untouchable.loop )
#	return remainingLoops

def getLoopsFromUnprovenMesh( edges, faces, importRadius, vertices, z ):
	"Get loops from a carve of an unproven mesh."
	edgePairTable = {}
	corners = []
	remainingEdgeTable = getRemainingEdgeTable( edges, vertices, z )
	remainingEdgeTableKeys = remainingEdgeTable.keys()
	for remainingEdgeIndexKey in remainingEdgeTable:
		edge = remainingEdgeTable[ remainingEdgeIndexKey ]
		carveIntersection = getCarveIntersectionFromEdge( edge, vertices, z )
		corners.append( carveIntersection )
		for edgeFaceIndex in edge.faceIndexes:
			face = faces[ edgeFaceIndex ]
			for edgeIndex in face.edgeIndexes:
				addEdgePair( edgePairTable, edges, edgeIndex, remainingEdgeIndexKey, remainingEdgeTable )
	allPoints = corners[ : ]
	for edgePairValue in edgePairTable.values():
		addPointsAtZ( edgePairValue, allPoints, importRadius, vertices, z )
	pointTable = {}
	return getInclusiveLoops( allPoints, corners, importRadius )

def getLoopsInOrderOfArea( compareAreaFunction, loops ):
	"Get the loops in the order of area according to the compare function."
	loopAreas = []
	for loop in loops:
		loopArea = LoopArea( loop )
		loopAreas.append( loopArea )
	loopAreas.sort( compareAreaFunction )
	loopsInDescendingOrderOfArea = []
	for loopArea in loopAreas:
		loopsInDescendingOrderOfArea.append( loopArea.loop )
	return loopsInDescendingOrderOfArea

def getLoopsWithCorners( corners, importRadius, loops, pointTable ):
	"Add corners to the loops."
	shortestAdditionalLength = 0.85 * importRadius
	for corner in corners:
		if corner not in pointTable:
			addWithLeastLength( loops, corner, shortestAdditionalLength )
	return loops

def getNextEdgeIndexAroundZ( edge, faces, remainingEdgeTable ):
	"Get the next edge index in the mesh carve."
	for faceIndex in edge.faceIndexes:
		face = faces[ faceIndex ]
		for edgeIndex in face.edgeIndexes:
			if edgeIndex in remainingEdgeTable:
				return edgeIndex
	return - 1

def getNumberOfOddIntersectionsFromLoops( leftPoint, loops ):
	"Get the number of odd intersections with the loops."
	totalNumberOfOddIntersections = 0
	for loop in loops:
		totalNumberOfOddIntersections += int( euclidean.getNumberOfIntersectionsToLeft( loop, leftPoint ) % 2 )
	return totalNumberOfOddIntersections

def getOverhangDirection( belowOutsetLoops, segmentBegin, segmentEnd ):
	"Add to span direction from the endpoint segments which overhang the layer below."
	segment = segmentEnd - segmentBegin
	normalizedSegment = euclidean.getNormalized( complex( segment.real, segment.imag ) )
	segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
	segmentBegin = segmentYMirror * segmentBegin
	segmentEnd = segmentYMirror * segmentEnd
	solidXIntersectionList = []
	y = segmentBegin.imag
	solidXIntersectionList.append( euclidean.XIntersectionIndex( - 1.0, segmentBegin.real ) )
	solidXIntersectionList.append( euclidean.XIntersectionIndex( - 1.0, segmentEnd.real ) )
	for belowLoopIndex in xrange( len( belowOutsetLoops ) ):
		belowLoop = belowOutsetLoops[ belowLoopIndex ]
		rotatedOutset = euclidean.getPointsRoundZAxis( segmentYMirror, belowLoop )
		euclidean.addXIntersectionIndexesFromLoopY( rotatedOutset, belowLoopIndex, solidXIntersectionList, y )
	overhangingSegments = euclidean.getSegmentsFromXIntersectionIndexes( solidXIntersectionList, y )
	overhangDirection = complex()
	for overhangingSegment in overhangingSegments:
		overhangDirection += getDoubledRoundZ( overhangingSegment, normalizedSegment )
	return overhangDirection

def getOverlapRatio( loop, pointTable ):
	"Get the overlap ratio between the loop and the point table."
	numberOfOverlaps = 0
	for point in loop:
		if point in pointTable:
			numberOfOverlaps += 1
	return float( numberOfOverlaps ) / float( len( loop ) )

def getPath( edges, pathIndexes, loop, z ):
	"Get the path from the edge intersections."
	path = []
	for pathIndexIndex in xrange( len( pathIndexes ) ):
		pathIndex = pathIndexes[ pathIndexIndex ]
		edge = edges[ pathIndex ]
		carveIntersection = getCarveIntersectionFromEdge( edge, loop, z )
		path.append( carveIntersection )
	return path

def getRemainingEdgeTable( edges, vertices, z ):
	"Get the remaining edge hashtable."
	remainingEdgeTable = {}
	if len( edges ) > 0:
		if edges[ 0 ].zMinimum == None:
			for edge in edges:
				edge.zMinimum = min( vertices[ edge.vertexIndexes[ 0 ] ].z, vertices[ edge.vertexIndexes[ 1 ] ].z )
				edge.zMaximum = max( vertices[ edge.vertexIndexes[ 0 ] ].z, vertices[ edge.vertexIndexes[ 1 ] ].z )
	for edgeIndex in xrange( len( edges ) ):
		edge = edges[ edgeIndex ]
		if ( edge.zMinimum < z ) and ( edge.zMaximum > z ):
			remainingEdgeTable[ edgeIndex ] = edge
	return remainingEdgeTable

def getSharedFace( firstEdge, faces, secondEdge ):
	"Get the face which is shared by two edges."
	for firstEdgeFaceIndex in firstEdge.faceIndexes:
		for secondEdgeFaceIndex in secondEdge.faceIndexes:
			if firstEdgeFaceIndex == secondEdgeFaceIndex:
				return faces[ firstEdgeFaceIndex ]
	return None

def getTriangleMesh( fileName = '' ):
	"Carve a GNU Triangulated Surface file.  If no fileName is specified, carve the first GNU Triangulated Surface file in this folder."
	if fileName == '':
		unmodified = gcodec.getGNUTriangulatedSurfaceFiles()
		if len( unmodified ) == 0:
			print( "There are no GNU Triangulated Surface files in this folder." )
			return None
		fileName = unmodified[ 0 ]
	gnuTriangulatedSurfaceText = gcodec.getFileText( fileName )
	if gnuTriangulatedSurfaceText == '':
		return None
	triangleMesh = TriangleMesh().getFromGNUTriangulatedSurfaceText( gnuTriangulatedSurfaceText )
	return triangleMesh

def getWideAnglePointIndex( loop ):
	"Get a point index which has a wide enough angle, most point indexes have a wide enough angle, this is just to make sure."
	dotProductMinimum = 9999999.9
	widestPointIndex = 0
	for pointIndex in xrange( len( loop ) ):
		point = loop[ pointIndex % len( loop ) ]
		afterPoint = loop[ ( pointIndex + 1 ) % len( loop ) ]
		beforePoint = loop[ ( pointIndex - 1 ) % len( loop ) ]
		afterSegmentNormalized = euclidean.getNormalized( afterPoint - point )
		beforeSegmentNormalized = euclidean.getNormalized( beforePoint - point )
		dotProduct = euclidean.getDotProduct( afterSegmentNormalized, beforeSegmentNormalized )
		if dotProduct < .99:
			return pointIndex
		if dotProduct < dotProductMinimum:
			dotProductMinimum = dotProduct
			widestPointIndex = pointIndex
	return widestPointIndex

def initializeZoneIntervalTable( shape, vertices ):
	"Initialize the zone interval and the zZone table"
	shape.zoneInterval = shape.layerThickness / math.sqrt( len( vertices ) ) / 1000.0
	shape.zZoneTable = {}
	for point in vertices:
		addToZoneTable( point, shape )

def isInline( beginComplex, centerComplex, endComplex ):
	"Determine if the three complex points form a line."
	centerBeginComplex = beginComplex - centerComplex
	centerEndComplex = endComplex - centerComplex
	centerBeginLength = abs( centerBeginComplex )
	centerEndLength = abs( centerEndComplex )
	if centerBeginLength <= 0.0 or centerEndLength <= 0.0:
		return False
	centerBeginComplex /= centerBeginLength
	centerEndComplex /= centerEndLength
	return euclidean.getDotProduct( centerBeginComplex, centerEndComplex ) < - 0.999

def isPathAdded( edges, faces, loops, remainingEdgeTable, vertices, z ):
	"Get the path indexes around a triangle mesh carve and add the path to the flat loops."
	if len( remainingEdgeTable ) < 1:
		return False
	pathIndexes = []
	remainingEdgeIndexKey = remainingEdgeTable.keys()[ 0 ]
	pathIndexes.append( remainingEdgeIndexKey )
	del remainingEdgeTable[ remainingEdgeIndexKey ]
	nextEdgeIndexAroundZ = getNextEdgeIndexAroundZ( edges[ remainingEdgeIndexKey ], faces, remainingEdgeTable )
	while nextEdgeIndexAroundZ != - 1:
		pathIndexes.append( nextEdgeIndexAroundZ )
		del remainingEdgeTable[ nextEdgeIndexAroundZ ]
		nextEdgeIndexAroundZ = getNextEdgeIndexAroundZ( edges[ nextEdgeIndexAroundZ ], faces, remainingEdgeTable )
	if len( pathIndexes ) < 3:
		print( "Dangling edges, will use intersecting circles to get import layer at height %s" % z )
		del loops[ : ]
		return False
	loops.append( getPath( edges, pathIndexes, vertices, z ) )
	return True


class Edge:
	"An edge of a triangle mesh."
	def __init__( self ):
		"Set the face indexes to None."
		self.faceIndexes = []
		self.vertexIndexes = []
		self.zMaximum = None
		self.zMinimum = None
	
	def __repr__( self ):
		"Get the string representation of this Edge."
		return str( self.index ) + ' ' + str( self.faceIndexes ) + ' ' + str( self.vertexIndexes )

	def addFaceIndex( self, faceIndex ):
		"Add first None face index to input face index."
		self.faceIndexes.append( faceIndex )

	def getFromVertexIndexes( self, edgeIndex, vertexIndexes ):
		"Initialize from two vertex indices."
		self.index = edgeIndex
		self.vertexIndexes = vertexIndexes[ : ]
		self.vertexIndexes.sort()
		return self

	def getGNUTriangulatedSurfaceLine( self ):
		"Get the GNU Triangulated Surface (.gts) line of text."
		return '%s %s' % ( self.vertexIndexes[ 0 ] + 1, self.vertexIndexes[ 1 ] + 1 )


class EdgePair:
	def __init__( self ):
		"Pair of edges on a face."
		self.edgeIndexes = []
		self.edges = []

	def __repr__( self ):
		"Get the string representation of this EdgePair."
		return str( self.edgeIndexes )

	def getFromIndexesEdges( self, edgeIndexes, edges ):
		"Initialize from edge indices."
		self.edgeIndexes = edgeIndexes[ : ]
		self.edgeIndexes.sort()
		for edgeIndex in self.edgeIndexes:
			self.edges.append( edges[ edgeIndex ] )
		return self


class Face:
	"A face of a triangle mesh."
	def __init__( self ):
		"Set the edge indexes to None."
		self.edgeIndexes = []
		self.index = None
		self.vertexIndexes = []
	
	def __repr__( self ):
		"Get the string representation of this Face."
		return str( self.index ) + ' ' + str( self.edgeIndexes ) + ' ' + str( self.vertexIndexes )

	def getFromEdgeIndexes( self, edgeIndexes, edges, faceIndex ):
		"Initialize from edge indices."
		self.index = faceIndex
		self.edgeIndexes = edgeIndexes
		for edgeIndex in edgeIndexes:
			edges[ edgeIndex ].addFaceIndex( faceIndex )
		for triangleIndex in xrange( 3 ):
			indexFirst = ( 3 - triangleIndex ) % 3
			indexSecond = ( 4 - triangleIndex ) % 3
			self.vertexIndexes.append( getCommonVertexIndex( edges[ edgeIndexes[ indexFirst ] ], edges[ edgeIndexes[ indexSecond ] ] ) )
		return self

	def getGNUTriangulatedSurfaceLine( self ):
		"Get the GNU Triangulated Surface (.gts) line of text."
		return '%s %s %s' % ( self.edgeIndexes[ 0 ] + 1, self.edgeIndexes[ 1 ] + 1, self.edgeIndexes[ 2 ] + 1 )

	def setEdgeIndexesToVertexIndexes( self, edges, edgeTable ):
		"Set the edge indexes to the vertex indexes."
		for triangleIndex in xrange( 3 ):
			indexFirst = ( 3 - triangleIndex ) % 3
			indexSecond = ( 4 - triangleIndex ) % 3
			vertexIndexFirst = self.vertexIndexes[ indexFirst ]
			vertexIndexSecond = self.vertexIndexes[ indexSecond ]
			vertexIndexPair = [ vertexIndexFirst, vertexIndexSecond ]
			vertexIndexPair.sort()
			edgeIndex = len( edges )
			if str( vertexIndexPair ) in edgeTable:
				edgeIndex = edgeTable[ str( vertexIndexPair ) ]
			else:
				edgeTable[ str( vertexIndexPair ) ] = edgeIndex
				edge = Edge().getFromVertexIndexes( edgeIndex, vertexIndexPair )
				edges.append( edge )
			edges[ edgeIndex ].addFaceIndex( self.index )
			self.edgeIndexes.append( edgeIndex )
		return self


class LoopArea:
	"Complex loop with an area."
	def __init__( self, loop ):
		self.area = abs( euclidean.getPolygonArea( loop ) )
		self.loop = loop

	def __repr__( self ):
		"Get the string representation of this flat path."
		return '%s, %s' % ( self.area, self.loop )


"""
Quoted from http://gts.sourceforge.net/reference/gts-surfaces.html#GTS-SURFACE-WRITE
"All the lines beginning with GTS_COMMENTS (#!) are ignored. The first line contains three unsigned integers separated by spaces. The first integer is the number of vertices, nv, the second is the number of edges, ne and the third is the number of faces, nf.

Follows nv lines containing the x, y and z coordinates of the vertices. Follows ne lines containing the two indices (starting from one) of the vertices of each edge. Follows nf lines containing the three ordered indices (also starting from one) of the edges of each face.

The format described above is the least common denominator to all GTS files. Consistent with an object-oriented approach, the GTS file format is extensible. Each of the lines of the file can be extended with user-specific attributes accessible through the read() and write() virtual methods of each of the objects written (surface, vertices, edges or faces). When read with different object classes, these extra attributes are just ignored."
"""

class TriangleMesh:
	"A triangle mesh."
	def __init__( self ):
		"Add empty lists."
		self.belowLoops = []
		self.bridgeLayerThickness = None
		self.edges = []
		self.faces = []
		self.importCoarseness = 1.0
		self.isCorrectMesh = True
		self.rotatedBoundaryLayers = []
		self.vertices = []
	
	def __repr__( self ):
		"Get the string representation of this TriangleMesh."
		return self.getGNUTriangulatedSurfaceText()

	def getCarveCornerMaximum( self ):
		"Get the corner maximum of the vertices."
		return self.cornerMaximum

	def getCarveCornerMinimum( self ):
		"Get the corner minimum of the vertices."
		return self.cornerMinimum

	def getCarveLayerThickness( self ):
		"Get the layer thickness."
		return self.layerThickness

	def getCarveRotatedBoundaryLayers( self ):
		"Get the rotated boundary layers."
		self.cornerMaximum = Vector3( - 999999999.0, - 999999999.0, - 999999999.0 )
		self.cornerMinimum = Vector3( 999999999.0, 999999999.0, 999999999.0 )
		for point in self.vertices:
			self.cornerMaximum = euclidean.getPointMaximum( self.cornerMaximum, point )
			self.cornerMinimum = euclidean.getPointMinimum( self.cornerMinimum, point )
		halfHeight = 0.5 * self.layerThickness
		initializeZoneIntervalTable( self, self.vertices )
		layerTop = self.cornerMaximum.z - halfHeight * 0.5
		z = self.cornerMinimum.z + halfHeight
		while z < layerTop:
			z = self.getZAddExtruderPaths( z )
		return self.rotatedBoundaryLayers

	def getGNUTriangulatedSurfaceText( self ):
		"Get this mesh in the GNU Triangulated Surface (.gts) format."
		output = cStringIO.StringIO()
		output.write( '%s %s %s Number of Vertices,Number of Edges,Number of Faces\n' % ( len( self.vertices ), len( self.edges ), len( self.faces ) ) )
		output.write( '%s %s %s Vertex Coordinates XYZ\n' % ( self.vertices[ 0 ].x, self.vertices[ 0 ].y, self.vertices[ 0 ].z ) )
		for vertex in self.vertices[ 1 : ]:
			output.write( '%s %s %s\n' % ( vertex.x, vertex.y, vertex.z ) )
		output.write( '%s Edge Vertex Indices Starting from 1\n' % self.edges[ 0 ].getGNUTriangulatedSurfaceLine() )
		for edge in self.edges[ 1 : ]:
			output.write( '%s\n' % edge.getGNUTriangulatedSurfaceLine() )
		output.write( '%s Face Edge Indices Starting from 1\n' % self.faces[ 0 ].getGNUTriangulatedSurfaceLine() )
		for face in self.faces[ 1 : ]:
			output.write( '%s\n' % face.getGNUTriangulatedSurfaceLine() )
		return output.getvalue()

	def getLoopsFromMesh( self, z ):
		"Get loops from a carve of a mesh."
		originalLoops = []
		if self.isCorrectMesh:
			originalLoops = getLoopsFromCorrectMesh( self.edges, self.faces, self.vertices, z )
		if len( originalLoops ) < 1:
			originalLoops = getLoopsFromUnprovenMesh( self.edges, self.faces, self.importRadius, self.vertices, z )
		loops = getLoopsInOrderOfArea( compareAreaDescending, euclidean.getSimplifiedLoops( originalLoops, self.importRadius ) )
		for loopIndex in xrange( len( loops ) ):
			loop = loops[ loopIndex ]
			leftPoint = euclidean.getLeftPoint( loop )
			isInFilledRegion = euclidean.isInFilledRegion( loops[ : loopIndex ] + loops[ loopIndex + 1 : ], leftPoint )
			if isInFilledRegion == euclidean.isWiddershins( loop ):
				loop.reverse()
		return loops

	def getZAddExtruderPaths( self, z ):
		"Get next z and add extruder loops."
		rotatedBoundaryLayer = euclidean.RotatedLoopLayer( z )
		self.rotatedBoundaryLayers.append( rotatedBoundaryLayer )
		rotatedBoundaryLayer.loops = self.getLoopsFromMesh( getEmptyZ( self, z ) )
		if self.bridgeLayerThickness == None:
			return z + self.layerThickness
		allExtrudateLoops = []
		for loop in rotatedBoundaryLayer.loops:
			allExtrudateLoops += getBridgeLoops( self.layerThickness, loop )
		rotatedBoundaryLayer.rotation = getBridgeDirection( self.belowLoops, allExtrudateLoops, self.layerThickness )
		self.belowLoops = allExtrudateLoops
		if rotatedBoundaryLayer.rotation == None:
			return z + self.layerThickness
		return z + self.bridgeLayerThickness

	def setCarveBridgeLayerThickness( self, bridgeLayerThickness ):
		"Set the bridge layer thickness.  If the infill is not in the direction of the bridge, the bridge layer thickness should be given as None or not set at all."
		self.bridgeLayerThickness = bridgeLayerThickness

	def setCarveLayerThickness( self, layerThickness ):
		"Set the layer thickness."
		self.layerThickness = layerThickness

	def setCarveImportRadius( self, importRadius ):
		"Set the import radius."
		self.importRadius = importRadius

	def setCarveIsCorrectMesh( self, isCorrectMesh ):
		"Set the is correct mesh flag."
		self.isCorrectMesh = isCorrectMesh

	def setEdgesForAllFaces( self ):
		"Set the face edges of all the faces."
		edgeTable = {}
		for face in self.faces:
			face.setEdgeIndexesToVertexIndexes( self.edges, edgeTable )
