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

from fabmetheus_utilities.solids.group import Group
from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.solids import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import intercircle
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


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

def getUnifiedLoops( importRadius, visibleObjectLoops, visibleObjectLoopsList ):
	"Get joined loops sliced through shape."
	corners = []
	for visibleObjectLoop in visibleObjectLoops:
		corners += visibleObjectLoop
	corners += getLoopsListsIntersections( visibleObjectLoopsList )
	allPoints = corners[ : ]
	allPoints += getInBetweenPointsFromLoops( importRadius, visibleObjectLoops )
	return trianglemesh.getInclusiveLoops( allPoints, corners, importRadius, False )

def getVisibleObjectLoopsList( importRadius, visibleObjects, z ):
	"Get visible object loops list."
	visibleObjectLoopsList = []
	for visibleObject in visibleObjects:
		visibleObjectLoops = visibleObject.getLoops( importRadius, z )
		visibleObjectLoopsList.append( visibleObjectLoops )
	return visibleObjectLoopsList

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


class BooleanSolid( Group ):
	"A boolean solid object."
	def createShape( self, matrixChain ):
		"Create the shape."
		self.setArchivableObjectOrder()
		Group.createShape( self, matrixChain )

	def getDifference( self, importRadius, visibleObjectLoopsList ):
		"Get subtracted loops sliced through shape."
		negativeLoops = getJoinedList( visibleObjectLoopsList[ 1 : ] )
		positiveLoops = visibleObjectLoopsList[ 0 ]
		radiusSide = 0.01 * importRadius
		corners = getPointsBoundarySideLoops( True, positiveLoops, getJoinedList( negativeLoops ), radiusSide )
		corners += getPointsBoundarySideLoops( False, negativeLoops, getJoinedList( positiveLoops ), radiusSide )
		loopsListsIntersections = getLoopsListsIntersections( visibleObjectLoopsList )
		corners += loopsListsIntersections
		allPoints = corners[ : ]
		allPoints += getInBetweenPointsFromLoopsBoundarySideOtherLoops( True, importRadius, negativeLoops, positiveLoops, radiusSide )
		allPoints += getInBetweenPointsFromLoopsBoundarySideOtherLoops( False, importRadius, positiveLoops, negativeLoops, radiusSide )
		return trianglemesh.getInclusiveLoops( allPoints, corners, importRadius, False )

	def getIntersection( self, importRadius, visibleObjectLoopsList ):
		"Get intersected loops sliced through shape."
		firstLoops = visibleObjectLoopsList[ 0 ]
		lastLoops = getJoinedList( visibleObjectLoopsList[ 1 : ] )
		radiusSide = 0.01 * importRadius
		corners = getPointsBoundarySideLoops( True, firstLoops, getJoinedList( lastLoops ), radiusSide )
		corners += getPointsBoundarySideLoops( True, lastLoops, getJoinedList( firstLoops ), radiusSide )
		corners += getLoopsListsIntersections( visibleObjectLoopsList )
		allPoints = corners[ : ]
		allPoints += getInBetweenPointsFromLoopsBoundarySideOtherLoops( True, importRadius, lastLoops, firstLoops, radiusSide )
		allPoints += getInBetweenPointsFromLoopsBoundarySideOtherLoops( True, importRadius, firstLoops, lastLoops, radiusSide )
		return trianglemesh.getInclusiveLoops( allPoints, corners, importRadius, False )

	def getLoops( self, importRadius, z ):
		"Get loops sliced through shape."
		visibleObjects = geomancer.getVisibleObjects( self.archivableObjects )
		if len( visibleObjects ) < 1:
			return []
		visibleObjectLoopsList = getVisibleObjectLoopsList( importRadius, visibleObjects, z )
		loops = self.getLoopsFromObjectLoopsList( importRadius, visibleObjectLoopsList )
		return euclidean.getSimplifiedLoops( loops, importRadius )

	def getLoopsFromObjectLoopsList( self, importRadius, visibleObjectLoopsList ):
		"Get loops from visible object loops list."
		return self.operationFunction( importRadius, visibleObjectLoopsList )

	def getUnion( self, importRadius, visibleObjectLoopsList ):
		"Get joined loops sliced through shape."
		return getUnifiedLoops( importRadius, getJoinedList( visibleObjectLoopsList ), visibleObjectLoopsList )

	def getXMLClassName( self ):
		"Get xml class name."
		return self.operationFunction.__name__.lower()[ len( 'get' ) : ]

	def reverseArchivableObjects( self ):
		"Reverse the archivable objects and set the operation function."
		self.archivableObjects.reverse()
		self.operationFunction = self.getDifference

	def setArchivableObjectOrder( self ):
		"Set the archivable object order."
		if self.operationFunction == self.reverseArchivableObjects:
			self.reverseArchivableObjects()
