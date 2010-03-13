"""
This page is in the table of contents.
The xml.py script is an import translator plugin to get a carving from an Art of Illusion xml file.

An import plugin is a script in the interpret_plugins folder which has the function getCarving.  It is meant to be run from the interpret tool.  To ensure that the plugin works on platforms which do not handle file capitalization properly, give the plugin a lower case name.

The getCarving function takes the file name of an xml file and returns the carving.

This example gets a triangle mesh for the xml file boolean.xml.  This example is run in a terminal in the folder which contains boolean.xml and xml.py.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import xml
>>> xml.getCarving().getCarveRotatedBoundaryLayers()
[-1.159765625, None, [[(-18.925000000000001-2.4550000000000001j), (-18.754999999999981-2.4550000000000001j)
..
many more lines of the carving
..


An xml file can be exported from Art of Illusion by going to the "File" menu, then going into the "Export" menu item, then picking the XML choice.  This will bring up the XML file chooser window, choose a place to save the file then click "OK".  Leave the "compressFile" checkbox unchecked.  All the objects from the scene will be exported, this plugin will ignore the light and camera.  If you want to fabricate more than one object at a time, you can have multiple objects in the Art of Illusion scene and they will all be carved, then fabricated together.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.fabmetheus_utilities.vector3 import Vector3
from skeinforge_tools.fabmetheus_utilities.xml_simple_parser import XMLSimpleParser
from skeinforge_tools.fabmetheus_utilities import euclidean
from skeinforge_tools.fabmetheus_utilities import gcodec
from skeinforge_tools.fabmetheus_utilities import intercircle
from skeinforge_tools.fabmetheus_utilities import triangle_mesh
import cStringIO
import math
import sys

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addBeginXMLTag( attributeTable, depth, name, output ):
	"Get the begin xml tag."
	attributeTableString = ''
	attributeTableKeys = attributeTable.keys()
	attributeTableKeys.sort()
	for attributeTableKey in attributeTableKeys:
		attributeTableString += ' %s="%s"' % ( attributeTableKey, attributeTable[ attributeTableKey ] )
	depthStart = '\t' * depth
	output.write( '%s<%s%s>\n' % ( depthStart, name, attributeTableString ) )

def addEndXMLTag( depth, name, output ):
	"Get the end xml tag."
	depthStart = '\t' * depth
	output.write( '%s</%s>\n' % ( depthStart, name ) )

def addLineLoopsIntersections( loopLoopsIntersections, loops, pointBegin, pointEnd ):
	"Add intersections of the line with the loops."
	normalizedSegment = pointEnd - pointBegin
	normalizedSegmentLength = abs( normalizedSegment )
	if normalizedSegmentLength <= 0.0:
		return
	lineLoopsIntersections = []
	normalizedSegment /= normalizedSegmentLength
	segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
	pointBeginRotated = segmentYMirror * pointBegin
	pointEndRotated = segmentYMirror * pointEnd
	addLoopsXSegmentIntersections( lineLoopsIntersections, loops, pointBeginRotated.real, pointEndRotated.real, segmentYMirror, pointBeginRotated.imag )
	for lineLoopsIntersection in lineLoopsIntersections:
		point = complex( lineLoopsIntersection, pointBeginRotated.imag ) * normalizedSegment
		loopLoopsIntersections.append( point )

def addLineXSegmentIntersection( lineLoopsIntersections, segmentFirstX, segmentSecondX, vector3First, vector3Second, y ):
	"Add intersections of the line with the x segment."
	isYAboveFirst = y > vector3First.imag
	isYAboveSecond = y > vector3Second.imag
	if isYAboveFirst == isYAboveSecond:
		return
	xIntersection = euclidean.getXIntersection( vector3First, vector3Second, y )
	if xIntersection <= min( segmentFirstX, segmentSecondX ):
		return
	if xIntersection >= max( segmentFirstX, segmentSecondX ):
		return
	lineLoopsIntersections.append( xIntersection )

def addLoopLoopsIntersections( loop, loopsLoopsIntersections, otherLoops ):
	"Add intersections of the loop with the other loops."
	for pointIndex in xrange( len( loop ) ):
		pointBegin = loop[ pointIndex ]
		pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
		addLineLoopsIntersections( loopsLoopsIntersections, otherLoops, pointBegin, pointEnd )

def addLoopsXSegmentIntersections( lineLoopsIntersections, loops, segmentFirstX, segmentSecondX, segmentYMirror, y ):
	"Add intersections of the loops with the x segment."
	for loop in loops:
		addLoopXSegmentIntersections( lineLoopsIntersections, loop, segmentFirstX, segmentSecondX, segmentYMirror, y )

def addLoopXSegmentIntersections( lineLoopsIntersections, loop, segmentFirstX, segmentSecondX, segmentYMirror, y ):
	"Add intersections of the loop with the x segment."
	rotatedLoop = euclidean.getPointsRoundZAxis( segmentYMirror, loop )
	for pointIndex in xrange( len( rotatedLoop ) ):
		pointFirst = rotatedLoop[ pointIndex ]
		pointSecond = rotatedLoop[ ( pointIndex + 1 ) % len( rotatedLoop ) ]
		addLineXSegmentIntersection( lineLoopsIntersections, segmentFirstX, segmentSecondX, pointFirst, pointSecond, y )

def getBottom( points ):
	"Get the bottom of the points."
	bottom = 999999999.9
	for point in points:
		bottom = min( bottom, point.z )
	return bottom

def getFloatOne( key, table ):
	"Get the value as a float if it exists, otherwise return one."
	if key in table:
		return float( table[ key ] )
	return 1.0

def getFloatZero( key, table ):
	"Get the value as a float if it exists, otherwise return zero."
	if key in table:
		return float( table[ key ] )
	return 0.0

def getInBetweenPointsFromLoops( importRadius, loops ):
	"Get the in between points from loops."
	inBetweenPoints = []
	for loop in loops:
		for pointIndex in xrange( len( loop ) ):
			pointBegin = loop[ pointIndex ]
			pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
			intercircle.addPointsFromSegment( pointBegin, pointEnd, inBetweenPoints, importRadius, 0.2123 )
	return inBetweenPoints

def getInBetweenPointsFromLoopsBoundarySideOtherLoops( inside, importRadius, loops, otherLoops, radiusSide ):
	"Get the in between points from loops."
	inBetweenPoints = []
	for loop in loops:
		for pointIndex in xrange( len( loop ) ):
			pointBegin = loop[ pointIndex ]
			pointEnd = loop[ ( pointIndex + 1 ) % len( loop ) ]
			inBetweenSegmentPoints = []
			intercircle.addPointsFromSegment( pointBegin, pointEnd, inBetweenSegmentPoints, importRadius, 0.2123 )
			for inBetweenSegmentPoint in inBetweenSegmentPoints:
				if isPointOrEitherLineBoundarySideInsideLoops( inside, otherLoops, pointBegin, inBetweenSegmentPoint, pointEnd, radiusSide ):
					inBetweenPoints.append( inBetweenSegmentPoint )
	return inBetweenPoints

def getJoinedList( originalLists ):
	"Get the lists as one joined list."
	concatenatedList = []
	for originalList in originalLists:
		concatenatedList += originalList
	return concatenatedList

def getLoopsListsIntersections( loopsList ):
	"Get intersections betweens the loops lists."
	loopsListsIntersections = []
	for loopsIndex in xrange( len( loopsList ) ):
		loops = loopsList[ loopsIndex ]
		for otherLoops in loopsList[ : loopsIndex ]:
			loopsListsIntersections += getLoopsLoopsIntersections( loops, otherLoops )
	return loopsListsIntersections

def getLoopsLoopsIntersections( loops, otherLoops ):
	"Get all the intersections of the loops with the other loops."
	loopsLoopsIntersections = []
	for loop in loops:
		addLoopLoopsIntersections( loop, loopsLoopsIntersections, otherLoops )
	return loopsLoopsIntersections

def getMatrixKey( column, row ):
	"Get the key string from row & column, counting from one."
	return 'm' + str( column + 1 ) + str( row + 1 )

def getPointsBoundarySideLoops( inside, loops, points, radius ):
	"Get the points inside the loops."
	pointsInsideLoops = []
	for pointIndex in xrange( len( points ) ):
		pointBegin = points[ ( pointIndex + len( points ) - 1 ) % len( points ) ]
		pointCenter = points[ pointIndex ]
		pointEnd = points[ ( pointIndex + 1 ) % len( points ) ]
		if isPointOrEitherBoundarySideInsideLoops( inside, loops, pointBegin, pointCenter, pointEnd, radius ):
			pointsInsideLoops.append( pointCenter )
	return pointsInsideLoops

def getSubObjectLoopsList( importRadius, subObjects, z ):
	"Get subObject loops list."
	subObjectLoopsList = []
	for subObject in subObjects:
		subObjectLoops = subObject.getLoops( importRadius, z )
		subObjectLoopsList.append( subObjectLoops )
	return subObjectLoopsList

def getTop( points ):
	"Get the top of the points."
	top = - 999999999.9
	for point in points:
		top = max( top, point.z )
	return top

def getTransformedByList( floatList, point ):
	"Get the point transformed by the array."
	return floatList[ 0 ] * point.x + floatList[ 1 ] * point.y + floatList[ 2 ] * point.z + floatList[ 3 ]

def getVector3TransformedByMatrix( matrix, vector3 ):
	"Get the vector3 multiplied by a vector3."
	vector3Transformed = Vector3()
	vector3Transformed.x = getTransformedByList( matrix[ 0 ], vector3 )
	vector3Transformed.y = getTransformedByList( matrix[ 1 ], vector3 )
	vector3Transformed.z = getTransformedByList( matrix[ 2 ], vector3 )
	return vector3Transformed

def isPointOrEitherBoundarySideInsideLoops( inside, loops, pointBegin, pointCenter, pointEnd, radius ):
	"Determine if the point or a point on either side of the point, is inside the loops."
	if euclidean.isPointInsideLoops( loops, pointCenter ) != inside:
		return False
	segmentBegin = pointBegin - pointCenter
	segmentEnd = pointEnd - pointCenter
	segmentBeginLength = abs( segmentBegin )
	segmentEndLength = abs( segmentEnd )
	if segmentBeginLength <= 0.0 or segmentEndLength <= 0.0:
		return False
	segmentBegin /= segmentBeginLength
	segmentEnd /= segmentEndLength
	addedSegment = segmentBegin + segmentEnd
	addedSegmentLength = abs( addedSegment )
	if addedSegmentLength > 0.0:
		addedSegment *= radius / addedSegmentLength
	else:
		addedSegment = radius * complex( segmentEnd.imag, - segmentEnd.real )
	if euclidean.isPointInsideLoops( loops,  pointCenter + addedSegment ) != inside:
		return False
	return euclidean.isPointInsideLoops( loops,  pointCenter - addedSegment ) == inside

def isPointOrEitherLineBoundarySideInsideLoops( inside, loops, pointBegin, pointCenter, pointEnd, radius ):
	"Determine if the point or a point on either side of the point, is inside the loops."
	if euclidean.isPointInsideLoops( loops, pointCenter ) != inside:
		return False
	segment = pointEnd - pointBegin
	segmentLength = abs( segment )
	if segmentLength <= 0.0:
		return False
	segment /= segmentLength
	addedSegment = radius * complex( segment.imag, - segment.real )
	if euclidean.isPointInsideLoops( loops,  pointCenter + addedSegment ) != inside:
		return False
	return euclidean.isPointInsideLoops( loops,  pointCenter - addedSegment ) == inside

def setBottomTopTriangleMesh( carvableObject, edgeTriples, matrixChain, vertexPairs, vertices ):
	"Set the bottom, top and triangle mesh of this carvable object info."
	newMatrix4X4 = carvableObject.matrix4X4.getReverseMultiplied( matrixChain )
	carvableObject.triangleMesh = triangle_mesh.TriangleMesh()
	for vertex in vertices:
		carvableObject.triangleMesh.vertices.append( getVector3TransformedByMatrix( newMatrix4X4.matrix, vertex ) )
	for vertexPairsIndex in xrange( len( vertexPairs ) ):
		vertexPair = vertexPairs[ vertexPairsIndex ]
		edge = triangle_mesh.Edge().getFromVertexIndexes( vertexPairsIndex, vertexPair )
		carvableObject.triangleMesh.edges.append( edge )
	for edgeTriplesIndex in xrange( len( edgeTriples ) ):
		edgeTriple = edgeTriples[ edgeTriplesIndex ]
		face = triangle_mesh.Face().getFromEdgeIndexes( edgeTriple, carvableObject.triangleMesh.edges, edgeTriplesIndex )
		carvableObject.triangleMesh.faces.append( face )
	carvableObject.bottom = getBottom( carvableObject.triangleMesh.vertices )
	carvableObject.top = getTop( carvableObject.triangleMesh.vertices )


class BooleanGeometry:
	"A shape scene."
	def __init__( self ):
		"Add empty lists."
		self.belowLoops = []
		self.bridgeLayerThickness = None
		self.carvableObjects = []
		self.importRadius = 0.3
		self.layerThickness = 0.4
		self.rotatedBoundaryLayers = []

	def __repr__( self ):
		"Get the string representation of this carving."
		output = cStringIO.StringIO()
		output.write( "<?xml version='1.0' ?>\n" )
		addBeginXMLTag( { 'version' : '2010-03-10' }, 0, self.__class__.__name__.lower(), output )
		for carvableObject in self.carvableObjects:
			carvableObject.addXML( 1, output )
		addEndXMLTag( 0, self.__class__.__name__.lower(), output )
		return output.getvalue()

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
		if len( self.carvableObjects ) < 1:
			return []
		self.cornerMaximum = Vector3( - 999999999.0, - 999999999.0, - 9999999999.9 )
		self.cornerMinimum = Vector3( 999999999.0, 999999999.0, 9999999999.9 )
		for carvableObject in self.carvableObjects:
			self.cornerMaximum.z = max( self.cornerMaximum.z, carvableObject.top )
			self.cornerMinimum.z = min( self.cornerMinimum.z, carvableObject.bottom )
		halfHeight = 0.5 * self.layerThickness
		layerTop = self.cornerMaximum.z - halfHeight
		self.setActualMinimumZ( halfHeight, layerTop )
		vertices = []
		for carvableObject in self.carvableObjects:
			vertices += carvableObject.getVertices()
		triangle_mesh.initializeZoneIntervalTable( self, vertices )
		z = self.cornerMinimum.z + halfHeight
		while z < layerTop:
			z = self.getZAddExtruderPaths( z )
		for rotatedBoundaryLayer in self.rotatedBoundaryLayers:
			for loop in rotatedBoundaryLayer.loops:
				for point in loop:
					pointVector3 = Vector3( point.real, point.imag, rotatedBoundaryLayer.z )
					self.cornerMaximum = euclidean.getPointMaximum( self.cornerMaximum, pointVector3 )
					self.cornerMinimum = euclidean.getPointMinimum( self.cornerMinimum, pointVector3 )
		self.cornerMaximum.z = layerTop + halfHeight
		for rotatedBoundaryLayerIndex in xrange( len( self.rotatedBoundaryLayers ) - 1, - 1, - 1 ):
			rotatedBoundaryLayer = self.rotatedBoundaryLayers[ rotatedBoundaryLayerIndex ]
			if len( rotatedBoundaryLayer.loops ) > 0:
				return self.rotatedBoundaryLayers[ : rotatedBoundaryLayerIndex + 1 ]
		return []

	def getExtruderPaths( self, z ):
		"Get extruder loops."
		rotatedBoundaryLayer = euclidean.RotatedLoopLayer( z )
		for carvableObject in self.carvableObjects:
			rotatedBoundaryLayer.loops += carvableObject.getLoops( self.importRadius, z )
		return rotatedBoundaryLayer

	def getZAddExtruderPaths( self, z ):
		"Get next z and add extruder loops."
		rotatedBoundaryLayer = self.getExtruderPaths( triangle_mesh.getEmptyZ( self, z ) )
		self.rotatedBoundaryLayers.append( rotatedBoundaryLayer )
		if self.bridgeLayerThickness == None:
			return z + self.layerThickness
		allExtrudateLoops = []
		for loop in rotatedBoundaryLayer.loops:
			allExtrudateLoops += triangle_mesh.getBridgeLoops( self.layerThickness, loop )
		rotatedBoundaryLayer.rotation = triangle_mesh.getBridgeDirection( self.belowLoops, allExtrudateLoops, self.layerThickness )
		self.belowLoops = allExtrudateLoops
		if rotatedBoundaryLayer.rotation == None:
			return z + self.layerThickness
		return z + self.bridgeLayerThickness

	def setActualMinimumZ( self, halfHeight, layerTop ):
		"Get the actual minimum z at the lowest rotated boundary layer."
		while self.cornerMinimum.z < layerTop:
			if len( self.getExtruderPaths( self.cornerMinimum.z ).loops ) > 0:
				increment = - halfHeight
				while abs( increment ) > 0.001 * halfHeight:
					self.cornerMinimum.z += increment
					increment = 0.5 * abs( increment )
					if len( self.getExtruderPaths( self.cornerMinimum.z ).loops ) > 0:
						increment = - increment
				return
			self.cornerMinimum.z += self.layerThickness

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


class Matrix4X4:
	"A four by four matrix."
	def __init__( self ):
		"Add empty lists."
		self.setMatrixToIdentity()

	def __repr__( self ):
		"Get the string representation of this four by four matrix."
		output = cStringIO.StringIO()
		self.addXML( 0, output )
		return output.getvalue()

	def addXML( self, depth, output ):
		"Add xml for this object."
		addBeginXMLTag( self.getAttributeTable(), depth, self.__class__.__name__.lower(), output )
		addEndXMLTag( depth, self.__class__.__name__.lower(), output )

	def getAttributeTable( self ):
		"Get the from row column attribute strings, counting from one."
		attributeTable = {}
		for column in xrange( 4 ):
			for row in xrange( 4 ):
				default = float( column == row )
				value = self.matrix[ column ][ row ]
				if abs( value - default ) > 0.00000000000001:
					attributeTable[ getMatrixKey( column, row ) ] = value
		return attributeTable

	def getFromAttributeTable( self, attributeTable ):
		"Get the values from row column attribute strings, counting from one."
		if attributeTable == None:
			return self
		for column in xrange( 4 ):
			for row in xrange( 4 ):
				key = getMatrixKey( column, row )
				if key in attributeTable:
					self.matrix[ column ][ row ] = float( attributeTable[ key ] )
		return self

	def getMultiplied( self, otherMatrix ):
		"Get this matrix multiplied by the other matrix."
		if otherMatrix == None:
			return self.matrix
		if self.matrix == None:
			return None
		#A down, B right from http://en.wikipedia.org/wiki/Matrix_multiplication
		newMatrix4X4 = Matrix4X4()
		newMatrix4X4.setMatrixToZero()
		for column in xrange( 4 ):
			for row in xrange( 4 ):
				matrixColumn = self.matrix[ column ]
				dotProduct = 0
				for elementIndex in xrange( 4 ):
					dotProduct += matrixColumn[ elementIndex ] * otherMatrix[ elementIndex ][ row ]
				newMatrix4X4.matrix[ column ][ row ] = dotProduct
		return newMatrix4X4

	def getReverseMultiplied( self, otherMatrix4X4 ):
		"Get this matrix reverse multiplied by the other matrix."
		if otherMatrix4X4 == None:
			return self
		return otherMatrix4X4.getMultiplied( self.matrix )

	def setMatrixToIdentity( self ):
		"Set the diagonal matrix elements to one."
		self.setMatrixToZero()
		for diagonal in xrange( 4 ):
			self.matrix[ diagonal ][ diagonal ] = 1.0

	def setMatrixToZero( self ):
		"Set the matrix elements to zero."
		self.matrix = [ [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ], [ 0.0, 0.0, 0.0, 0.0 ] ]


class TriangleMesh:
	"A triangle mesh object."
	def __init__( self ):
		"Set name to None."
		self.name = None

	def __repr__( self ):
		"Get the string representation of this object info."
		output = cStringIO.StringIO()
		self.addXML( 0, output )
		return output.getvalue()

	def addXML( self, depth, output ):
		"Add xml for this object."
		attributeTable = self.getAttributeTable()
		attributeTable[ 'id' ] = self.getName()
		addBeginXMLTag( attributeTable, depth, self.getXMLClassName(), output )
		self.addXMLSection( depth + 1, output )
		self.matrix4X4.addXML( depth + 1, output )
		addEndXMLTag( depth, self.getXMLClassName(), output )

	def addXMLSection( self, depth, output ):
		"Add the xml section for this object."
		addBeginXMLTag( {}, depth, 'vertices', output )
		for vertex in self.originalVertices:
			attributeTable = { 'x' : str( vertex.x ), 'y' : str( vertex.y ), 'z' : str( vertex.z ) }
			addBeginXMLTag( attributeTable, depth + 1, 'vector3', output )
			addEndXMLTag( depth + 1, 'vector3', output )
		addEndXMLTag( depth, 'vertices', output )
		addBeginXMLTag( {}, depth, 'faces', output )
		for face in self.triangleMesh.faces:
			attributeTable = {}
			for vertexIndexIndex in xrange( len( face.vertexIndexes ) ):
				vertexIndex = face.vertexIndexes[ vertexIndexIndex ]
				attributeTable[ 'vertex' + str( vertexIndexIndex ) ] = str( vertexIndex )
			addBeginXMLTag( attributeTable, depth + 1, 'face', output )
			addEndXMLTag( depth + 1, 'face', output )
		addEndXMLTag( depth, 'faces', output )

	def getAttributeTable( self ):
		"Get attribute table."
		return {}

	def getLoops( self, importRadius, z ):
		"Get loops sliced through shape."
		self.triangleMesh.importRadius = importRadius
		return self.triangleMesh.getLoopsFromMesh( z )

	def getName( self ):
		"Get the name if it exists, otherwise return the class name."
		if self.name == None:
			return self.__class__.__name__
		return self.name

	def getType( self ):
		"Get type."
		return self.__class__.__name__

	def getXMLClassName( self ):
		"Get xml class name."
		return self.__class__.__name__.lower()

	def getVertices( self ):
		"Get all vertices."
		return self.triangleMesh.vertices

	def setShapeToObjectVariables( self, matrixChain ):
		"Set the shape to the object variables."
		self.originalVertices = []
		newMatrix4X4 = self.matrix4X4.getReverseMultiplied( matrixChain )
		for vertex in self.triangleMesh.vertices:
			self.originalVertices.append( vertex.copy() )
			vertex.setToVector3( getVector3TransformedByMatrix( newMatrix4X4.matrix, vertex ) )
		self.bottom = getBottom( self.triangleMesh.vertices )
		self.top = getTop( self.triangleMesh.vertices )


class BooleanSolid( TriangleMesh ):
	"A boolean solid object."
	def __repr__( self ):
		"Get the string representation of this object info."
		stringRepresentation = '%s %s' % ( self.getName(), self.__class__.__name__ )
		for subObject in self.subObjects:
			stringRepresentation += '\n%s' % subObject
		return stringRepresentation

	def addXMLSection( self, depth, output ):
		"Add the xml section for this object."
		for subObject in self.subObjects:
			subObject.addXML( depth, output )

	def getAttributeTable( self ):
		"Get attribute table."
		return { 'operation' : self.operationFunction.__name__.lower()[ 3 : ] }

	def getIntersection( self, importRadius, subObjectLoopsList ):
		"Get intersected loops sliced through shape."
		firstLoops = subObjectLoopsList[ 0 ]
		lastLoops = getJoinedList( subObjectLoopsList[ 1 : ] )
		radiusSide = 0.01 * importRadius
		corners = getPointsBoundarySideLoops( True, firstLoops, getJoinedList( lastLoops ), radiusSide )
		corners += getPointsBoundarySideLoops( True, lastLoops, getJoinedList( firstLoops ), radiusSide )
		corners += getLoopsListsIntersections( subObjectLoopsList )
		allPoints = corners[ : ]
		allPoints += getInBetweenPointsFromLoopsBoundarySideOtherLoops( True, importRadius, lastLoops, firstLoops, radiusSide )
		allPoints += getInBetweenPointsFromLoopsBoundarySideOtherLoops( True, importRadius, firstLoops, lastLoops, radiusSide )
		return triangle_mesh.getInclusiveLoops( allPoints, corners, importRadius, False )

	def getUnion( self, importRadius, subObjectLoopsList ):
		"Get joined loops sliced through shape."
		loops = []
		for subObjectLoops in subObjectLoopsList:
			loops += subObjectLoops
		corners = []
		for loop in loops:
			corners += loop
		corners += getLoopsListsIntersections( subObjectLoopsList )
		allPoints = corners[ : ]
		allPoints += getInBetweenPointsFromLoops( importRadius, loops )
		return triangle_mesh.getInclusiveLoops( allPoints, corners, importRadius, False )

	def getLoops( self, importRadius, z ):
		"Get loops sliced through shape."
		if len( self.subObjects ) < 1:
			return []
		subObjectLoopsList = getSubObjectLoopsList( importRadius, self.subObjects, z )
		loops = self.operationFunction( importRadius, subObjectLoopsList )
		return euclidean.getSimplifiedLoops( loops, importRadius )

	def getFirstMinusComplement( self, importRadius, subObjectLoopsList ):
		"Get subtracted loops sliced through shape."
		negativeLoops = getJoinedList( subObjectLoopsList[ 1 : ] )
		positiveLoops = subObjectLoopsList[ 0 ]
		radiusSide = 0.01 * importRadius
		corners = getPointsBoundarySideLoops( True, positiveLoops, getJoinedList( negativeLoops ), radiusSide )
		corners += getPointsBoundarySideLoops( False, negativeLoops, getJoinedList( positiveLoops ), radiusSide )
		loopsListsIntersections = getLoopsListsIntersections( subObjectLoopsList )
		corners += loopsListsIntersections
		allPoints = corners[ : ]
		allPoints += getInBetweenPointsFromLoopsBoundarySideOtherLoops( True, importRadius, negativeLoops, positiveLoops, radiusSide )
		allPoints += getInBetweenPointsFromLoopsBoundarySideOtherLoops( False, importRadius, positiveLoops, negativeLoops, radiusSide )
		return triangle_mesh.getInclusiveLoops( allPoints, corners, importRadius, False )

	def getLastMinusComplement( self, importRadius, subObjectLoopsList ):
		"Get subtracted loops sliced through shape."
		subObjectLoopsList.reverse()
		return self.getFirstMinusComplement( importRadius, subObjectLoopsList )

	def getVertices( self ):
		"Get all vertices."
		vertices = []
		for subObject in self.subObjects:
			vertices += subObject.getVertices()
		return vertices

	def getXMLClassName( self ):
		"Get xml class name."
		return 'booleansolid'

	def setShapeToObjectVariables( self, matrixChain ):
		"Set the shape to the object variables."
		self.bottom = 999999999.9
		self.top = - 999999999.9
		for subObject in self.subObjects:
			self.bottom = min( self.bottom, subObject.bottom )
			self.top = max( self.top, subObject.top )


class Cube( TriangleMesh ):
	"A cube object."
	def addXMLSection( self, depth, output ):
		"Add the xml section for this object."
		pass

	def getAttributeTable( self ):
		"Get attribute table."
		return { 'halfx': self.halfX, 'halfy': self.halfY, 'halfz': self.halfZ }

	def setShapeToObjectVariables( self, matrixChain ):
		"Set the shape to the object variables."
		vertices = [
			Vector3( - 1.0, - 1.0, 1.0 ),
			Vector3( 1.0, - 1.0, 1.0 ),
			Vector3( 1.0, - 1.0, - 1.0 ),
			Vector3( - 1.0, - 1.0, - 1.0 ),
			Vector3( - 1.0, 1.0, 1.0 ),
			Vector3( 1.0, 1.0, 1.0 ),
			Vector3( 1.0, 1.0, - 1.0 ),
			Vector3( - 1.0, 1.0, - 1.0 ) ]
		for vertex in vertices:
			vertex.x *= self.halfX
			vertex.y *= self.halfY
			vertex.z *= self.halfZ
		vertexPairs = [
			[ 6, 4 ],
			[ 7, 6 ],
			[ 6, 2 ],
			[ 3, 2 ],
			[ 2, 1 ],
			[ 3, 1 ],
			[ 1, 0 ],
			[ 7, 2 ],
			[ 6, 1 ],
			[ 6, 5 ],
			[ 5, 1 ],
			[ 4, 3 ],
			[ 3, 0 ],
			[ 7, 3 ],
			[ 5, 0 ],
			[ 5, 4 ],
			[ 4, 0 ],
			[ 7, 4 ] ]
		edgeTriples = [
			[ 9, 0, 15 ],
			[ 1, 2, 7 ],
			[ 3, 4, 5 ],
			[ 12, 5, 6 ],
			[ 13, 7, 3 ],
			[ 2, 8, 4 ],
			[ 9, 10, 8 ],
			[ 16, 11, 12 ],
			[ 17, 13, 11 ],
			[ 10, 14, 6 ],
			[ 15, 16, 14 ],
			[ 1, 17, 0 ] ]
		setBottomTopTriangleMesh( self, edgeTriples, matrixChain, vertexPairs, vertices )


class Cylinder( Cube ):
	"A cylinder object."
	def getAttributeTable( self ):
		"Get attribute table."
		return { 'height': self.height, 'radiusx': self.radiusX, 'radiusz': self.radiusZ, 'topoverbottom': self.topOverBottom }

	def setShapeToObjectVariables( self, matrixChain ):
		"Set the shape to the object variables."
		numberOfSides = 31
		halfHeight = 0.5 * self.height
		vertices = []
		sideAngle = 2.0 * math.pi / float( numberOfSides )
		halfSideAngle = 0.5 * sideAngle
		edgeTriples = []
		vertexPairs = []
		numberOfVertices = numberOfSides + numberOfSides
		numberOfCircumferentialEdges = numberOfVertices + numberOfVertices
		for side in xrange( numberOfSides ):
			bottomAngle = float( side ) * sideAngle
			bottomComplex = euclidean.getUnitPolar( bottomAngle )
			bottomPoint = Vector3( bottomComplex.real * self.radiusX, - halfHeight, bottomComplex.imag * self.radiusZ )
			vertices.append( bottomPoint )
			topPoint = Vector3( bottomPoint.x * self.topOverBottom, halfHeight, bottomPoint.z * self.topOverBottom )
			vertices.append( topPoint )
			vertexPairBottom = [ side + side, ( side + side + 2 ) % numberOfVertices ]
			vertexPairBottomIndex = len( vertexPairs )
			vertexPairs.append( vertexPairBottom )
			vertexPairDiagonal = [ ( side + side + 2 ) % numberOfVertices, side + side + 1 ]
			vertexPairDiagonalIndex = len( vertexPairs )
			vertexPairs.append( vertexPairDiagonal )
			vertexPairVertical = [ side + side + 1, side + side ]
			vertexPairVerticalIndex = len( vertexPairs )
			vertexPairs.append( vertexPairVertical )
			vertexPairTop = [ side + side + 1, ( side + side + 3 ) % numberOfVertices ]
			vertexPairTopIndex = len( vertexPairs )
			vertexPairs.append( vertexPairTop )
			edgeTripleBottomVertical = [ vertexPairBottomIndex, vertexPairDiagonalIndex, vertexPairVerticalIndex ]
			edgeTriples.append( edgeTripleBottomVertical )
			edgeTripleBottomVertical = [ vertexPairTopIndex, vertexPairDiagonalIndex, ( vertexPairVerticalIndex + 4 ) % numberOfCircumferentialEdges ]
			edgeTriples.append( edgeTripleBottomVertical )
		for side in xrange( 2, numberOfSides - 1 ):
			vertexPairBottomHorizontal = [ 0, side + side ]
			vertexPairs.append( vertexPairBottomHorizontal )
			vertexPairTopHorizontal = [ 1, side + side + 1 ]
			vertexPairs.append( vertexPairTopHorizontal )
		for side in xrange( 1, numberOfSides - 1 ):
			vertexPairBottomIndex = 4 * side
			vertexPairBottomDiagonalIndex = vertexPairBottomIndex + 4
			vertexPairBottomBeforeIndex = vertexPairBottomIndex - 4
			vertexPairTopIndex = 4 * side + 3
			vertexPairTopDiagonalIndex = vertexPairTopIndex + 4
			vertexPairTopBeforeIndex = vertexPairTopIndex - 4
			if side > 1:
				vertexPairBottomBeforeIndex = numberOfCircumferentialEdges + 2 * side - 4
				vertexPairTopBeforeIndex = vertexPairBottomBeforeIndex + 1
			if side < numberOfSides - 2:
				vertexPairBottomDiagonalIndex = numberOfCircumferentialEdges + 2 * side - 2
				vertexPairTopDiagonalIndex = vertexPairBottomDiagonalIndex + 1
			edgeTripleBottomHorizontal = [ vertexPairBottomIndex, vertexPairBottomDiagonalIndex, vertexPairBottomBeforeIndex ]
			edgeTriples.append( edgeTripleBottomHorizontal )
			edgeTripleTopHorizontal = [ vertexPairTopIndex, vertexPairTopDiagonalIndex, vertexPairTopBeforeIndex ]
			edgeTriples.append( edgeTripleTopHorizontal )
		setBottomTopTriangleMesh( self, edgeTriples, matrixChain, vertexPairs, vertices )


class Sphere( Cube ):
	"A sphere object."
	def getAttributeTable( self ):
		"Get attribute table."
		return { 'radiusx': self.radiusX, 'radiusy': self.radiusY, 'radiusz': self.radiusZ }

	def setShapeToObjectVariables( self, matrixChain ):
		"Set the shape to the object variables."
		self.numberOfInBetweens = 19
		self.numberOfDivisions = self.numberOfInBetweens + 1
		squareRadius = 0.5 * float( self.numberOfInBetweens )
		vertexPairs = []
		edgeTriples = []
		vertices = []
		edgeDiagonalTable = {}
		edgeHorizontalTable = {}
		edgeVerticalTable = {}
		vertexTable = {}
		for row in xrange( self.numberOfDivisions ):
			for column in xrange( self.numberOfDivisions ):
				columnMinusRadius = float( column - squareRadius )
				rowMinusRadius = float( row - squareRadius )
				height = min( squareRadius - abs( columnMinusRadius ), squareRadius - abs( rowMinusRadius ) )
				squarePoint = Vector3( rowMinusRadius, columnMinusRadius, - height )
				vertexTable[ row, column, 0 ] = len( vertices )
				if row != 0 and row != self.numberOfInBetweens and column != 0 and column != self.numberOfInBetweens:
					vertices.append( squarePoint )
					squarePoint = Vector3( rowMinusRadius, columnMinusRadius, height )
				vertexTable[ row, column, 1 ] = len( vertices )
				vertices.append( squarePoint )
		for row in xrange( self.numberOfInBetweens ):
			for column in xrange( self.numberOfDivisions ):
				horizontalEdgeBottom = [ vertexTable[ row, column, 0 ], vertexTable[ row + 1, column, 0 ] ]
				edgeHorizontalTable[ row, column, 0 ] = len( vertexPairs )
				vertexPairs.append( horizontalEdgeBottom )
				horizontalEdgeTop = [ vertexTable[ row, column, 1 ], vertexTable[ row + 1, column, 1 ] ]
				edgeHorizontalTable[ row, column, 1 ] = len( vertexPairs )
				vertexPairs.append( horizontalEdgeTop )
		for row in xrange( self.numberOfDivisions ):
			for column in xrange( self.numberOfInBetweens ):
				verticalEdgeBottom = [ vertexTable[ row, column, 0 ], vertexTable[ row, column + 1, 0 ] ]
				edgeVerticalTable[ row, column, 0 ] = len( vertexPairs )
				vertexPairs.append( verticalEdgeBottom )
				verticalEdgeTop = [ vertexTable[ row, column, 1 ], vertexTable[ row, column + 1, 1 ] ]
				edgeVerticalTable[ row, column, 1 ] = len( vertexPairs )
				vertexPairs.append( verticalEdgeTop )
		for row in xrange( self.numberOfInBetweens ):
			for column in xrange( self.numberOfInBetweens ):
				diagonalEdgeBottom = [ vertexTable[ row, column, 0 ], vertexTable[ row + 1, column + 1, 0 ] ]
				edgeDiagonalTable[ row, column, 0 ] = len( vertexPairs )
				vertexPairs.append( diagonalEdgeBottom )
				diagonalEdgeTop = [ vertexTable[ row, column, 1 ], vertexTable[ row + 1, column + 1, 1 ] ]
				edgeDiagonalTable[ row, column, 1 ] = len( vertexPairs )
				vertexPairs.append( diagonalEdgeTop )
		for row in xrange( self.numberOfInBetweens ):
			for column in xrange( self.numberOfInBetweens ):
				fourThirtyOClockFaceBottom = [ edgeHorizontalTable[ row, column, 0 ], edgeVerticalTable[ row + 1, column, 0 ], edgeDiagonalTable[ row, column, 0 ] ]
				edgeTriples.append( fourThirtyOClockFaceBottom )
				tenThirtyOClockFaceBottom = [ edgeHorizontalTable[ row, column + 1, 0 ], edgeVerticalTable[ row, column, 0 ], edgeDiagonalTable[ row, column, 0 ] ]
				edgeTriples.append( tenThirtyOClockFaceBottom )
				fourThirtyOClockFaceTop = [ edgeHorizontalTable[ row, column, 1 ], edgeVerticalTable[ row + 1, column, 1 ], edgeDiagonalTable[ row, column, 1 ] ]
				edgeTriples.append( fourThirtyOClockFaceTop )
				tenThirtyOClockFaceTop = [ edgeHorizontalTable[ row, column + 1, 1 ], edgeVerticalTable[ row, column, 1 ], edgeDiagonalTable[ row, column, 1 ] ]
				edgeTriples.append( tenThirtyOClockFaceTop )
		for vertex in vertices:
			vertex.normalize()
			vertex.x *= self.radiusX
			vertex.y *= self.radiusY
			vertex.z *= self.radiusZ
		setBottomTopTriangleMesh( self, edgeTriples, matrixChain, vertexPairs, vertices )

