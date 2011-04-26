#! /usr/bin/env python
"""
This page is in the table of contents.
Fill is a script to fill the perimeters of a gcode file.

The fill manual page is at:
http://fabmetheus.crsndoo.com/wiki/index.php/Skeinforge_Fill

Allan Ecker aka The Masked Retriever has written the "Skeinforge Quicktip: Fill" at:
http://blog.thingiverse.com/2009/07/21/mysteries-of-skeinforge-fill/

==Operation==
The default 'Activate Fill' checkbox is off.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Diaphragm===
The diaphragm is a solid group of layers, at regular intervals.  It can be used with a sparse infill to give the object watertight, horizontal compartments and/or a higher shear strength.

====Diaphragm Period====
Default is one hundred.

Defines the number of layers between diaphrams.

====Diaphragm Thickness====
Default is zero, because the diaphragm feature is rarely used.

Defines the number of layers the diaphram is composed of.

===Extra Shells===
The shells interior perimeter loops.  Adding extra shells makes the object stronger & heavier.

====Extra Shells on Alternating Solid Layers====
Default is two.

Defines the number of extra shells, on the alternating solid layers.

====Extra Shells on Base====
Default is one.

Defines the number of extra shells on the bottom, base layer and every even solid layer after that.  Setting this to a different value than the "Extra Shells on Alternating Solid Layers" means the infill pattern will alternate, creating a strong interleaved bond even if the perimeter loop shrinks.

====Extra Shells on Sparse Layer====
Default is one.

Defines the number of extra shells on the sparse layers.  The solid layers are those at the top & bottom, and wherever the object has a plateau or overhang, the sparse layers are the layers in between.

===Grid===
====Grid Circle Separation over Perimeter Width====
Default is 0.2.

Defines the ratio of the amount the grid circle is inset over the perimeter width, the default is zero.  With a value of zero the circles will touch, with a value of one two threads could be fitted between the circles.

====Grid Extra Overlap====
Default is 0.1.

Defines the amount of extra overlap added when extruding the grid to compensate for the fact that when the first thread going through a grid point is extruded, since there is nothing there yet for it to connect to it will shrink extra.

====Grid Junction Separation over Octogon Radius At End====
Default is zero.

Defines the ratio of the amount the grid square is increased in each direction over the extrusion width at the end.  With a value of one or so the grid pattern will have large squares to go with the octogons.

====Grid Junction Separation over Octogon Radius At Middle====
Default is zero.

Defines the increase at the middle.  If this value is different than the value at the end, the grid would have an accordion pattern, which would give it a higher shear strength.

====Grid Junction Separation Band Height====
Default is ten.

Defines the height of the bands of the accordion pattern.

===Infill===
====Infill Pattern====
Default is 'Line', since it is quicker to generate and does not add extra movements for the extruder.  The grid pattern has extra diagonal lines, so when choosing a grid option, set the infill solidity to 0.2 or less so that there is not too much plastic and the grid generation time, which increases with the third power of solidity, will be reasonable.

=====Grid Circular=====
When selected, the infill will be a grid of separated circles.  Because the circles are separated, the pattern is weak, it only provides support for the top layer threads and some strength in the z direction.  The flip side is that this infill does not warp the object, the object will get warped only by the walls.

Because this pattern turns the extruder on and off often, it is best to use a stepper motor extruder.

=====Grid Hexagonal=====
When selected, the infill will be a hexagonal grid.  Because the grid is made with threads rather than with molding or milling, only a partial hexagon is possible, so the rectangular grid pattern is stronger.

=====Grid Rectangular=====
When selected, the infill will be a funky octogon square honeycomb like pattern which gives the object extra strength.

=====Line=====
When selected, the infill will be made up of lines.

====Infill Begin Rotation====
Default is forty five degrees, giving a diagonal infill.

Defines the amount the infill direction of the base and every second layer thereafter is rotated.

====Infill Odd Layer Extra Rotation====
Default is ninety degrees, making the odd layer infill perpendicular to the base layer.

Defines the extra amount the infill direction of the odd layers is rotated compared to the base layer.

====Infill Begin Rotation Repeat====
Default is one, giving alternating cross hatching.

Defines the number of layers that the infill begin rotation will repeat.  With a value higher than one, the infill will go in one direction more often, giving the object more strength in one direction and less in the other, this is useful for beams and cantilevers.

====Infill Perimeter Overlap====
Default is 0.15.

Defines the amount the infill overlaps the perimeter over the average of the perimeter and infill width.  The higher the value the more the infill will overlap the perimeter, and the thicker join between the infill and the perimeter.  If the value is too high, the join will be so thick that the nozzle will run plow through the join below making a mess, also when it is above 0.45 fill may not be able to create infill correctly.  If you want to stretch the infill a lot, set 'Path Stretch over Perimeter Width' in stretch to a high value.

====Infill Solidity====
Default is 0.2.

Defines the solidity of the infill, this is the most important setting in fill.  A value of one means the infill lines will be right beside each other, resulting in a solid, strong, heavy shape which takes a long time to extrude.  A low value means the infill will be sparse, the interior will be mosty empty space, the object will be weak, light and quick to build.

====Interior Infill Density over Exterior Density====
Default is 0.9.

Defines the ratio of the infill density of the interior over the infill density of the exterior surfaces.  The exterior should have a high infill density, so that the surface will be strong and watertight.  With the interior infill density a bit lower than the exterior, the plastic will not fill up higher than the extruder nozzle.  If the interior density is too high that could happen, as Nophead described in the Hydraraptor "Bearing Fruit" post at:
http://hydraraptor.blogspot.com/2008/08/bearing-fruit.html

====Infill Width over Thickness====
Default is 1.5.

Defines the ratio of the infill width over the layer thickness.  The higher the value the wider apart the infill will be and therefore the sparser the infill will be.

===Solid Surface Thickness===
Default is three.

Defines the number of solid layers that are at the bottom, top, plateaus and overhang.  With a value of zero, the entire object will be composed of a sparse infill, and water could flow right through it.  With a value of one, water will leak slowly through the surface and with a value of three, the object could be watertight.  The higher the solid surface thickness, the stronger and heavier the object will be.

===Thread Sequence Choice===
The 'Thread Sequence Choice' is the sequence in which the threads will be extruded.  There are three kinds of thread, the perimeter threads on the outside of the object, the loop threads aka inner shell threads, and the interior infill threads.

The default choice is 'Perimeter > Loops > Infill', which the default stretch parameters are based on.  If you change from the default sequence choice setting of perimeter, then loops, then infill, the optimal stretch thread parameters would also be different.  In general, if the infill is extruded first, the infill would have to be stretched more so that even after the filament shrinkage, it would still be long enough to connect to the loop or perimeter.  The six sequence combinations follow below.

====Infill > Loops > Perimeter====
====Infill > Perimeter > Loops====
====Loops > Infill > Perimeter====
====Loops > Perimeter > Infill====
====Perimeter > Infill > Loops====
====Perimeter > Loops > Infill====

==Examples==
The following examples fill the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and fill.py.


> python fill.py
This brings up the fill dialog.


> python fill.py Screw Holder Bottom.stl
The fill tool is parsing the file:
Screw Holder Bottom.stl
..
The fill tool has created the file:
.. Screw Holder Bottom_fill.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import fill
>>> fill.main()
This brings up the fill dialog.


>>> fill.writeOutput('Screw Holder Bottom.stl')
The fill tool is parsing the file:
Screw Holder Bottom.stl
..
The fill tool has created the file:
.. Screw Holder Bottom_fill.gcode

"""

from __future__ import absolute_import
try:
	import psyco
	psyco.full()
except:
	pass
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities.geometry.solids import trianglemesh
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import archive
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import intercircle
from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_craft
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
from skeinforge_application.skeinforge_utilities import skeinforge_profile
import math
import sys


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = "$Date: 2008/28/04 $"
__license__ = 'GPL 3.0'



def addAroundGridPoint( arounds, gridPoint, gridPointInsetX, gridPointInsetY, gridPoints, gridSearchRadius, isBothOrNone, isDoubleJunction, isJunctionWide, paths, pixelTable, width ):
	"Add the path around the grid point."
	closestPathIndex = None
	aroundIntersectionPaths = []
	for aroundIndex in xrange( len( arounds ) ):
		loop = arounds[ aroundIndex ]
		for pointIndex in xrange(len(loop)):
			pointFirst = loop[pointIndex]
			pointSecond = loop[(pointIndex + 1) % len(loop)]
			yIntersection = euclidean.getYIntersectionIfExists( pointFirst, pointSecond, gridPoint.real )
			addYIntersectionPathToList( aroundIndex, pointIndex, gridPoint.imag, yIntersection, aroundIntersectionPaths )
	if len( aroundIntersectionPaths ) < 2:
		print('This should never happen, aroundIntersectionPaths is less than 2 in fill.')
		print( aroundIntersectionPaths )
		print( gridPoint )
		return
	yCloseToCenterArounds = getClosestOppositeIntersectionPaths( aroundIntersectionPaths )
	if len( yCloseToCenterArounds ) < 2:
#		This used to be worth the warning below.
#		print('This should never happen, yCloseToCenterArounds is less than 2 in fill.')
#		print( gridPoint )
#		print( len( yCloseToCenterArounds ) )
		return
	segmentFirstY = min( yCloseToCenterArounds[0].y, yCloseToCenterArounds[1].y )
	segmentSecondY = max( yCloseToCenterArounds[0].y, yCloseToCenterArounds[1].y )
	yIntersectionPaths = []
	gridPixel = euclidean.getStepKeyFromPoint( gridPoint / width )
	segmentFirstPixel = euclidean.getStepKeyFromPoint( complex( gridPoint.real, segmentFirstY ) / width )
	segmentSecondPixel = euclidean.getStepKeyFromPoint( complex( gridPoint.real, segmentSecondY ) / width )
	pathIndexTable = {}
	addPathIndexFirstSegment( gridPixel, pathIndexTable, pixelTable, segmentFirstPixel )
	addPathIndexSecondSegment( gridPixel, pathIndexTable, pixelTable, segmentSecondPixel )
	for pathIndex in pathIndexTable.keys():
		path = paths[ pathIndex ]
		for pointIndex in xrange( len(path) - 1 ):
			pointFirst = path[ pointIndex ]
			pointSecond = path[ pointIndex + 1 ]
			yIntersection = getYIntersectionInsideYSegment( segmentFirstY, segmentSecondY, pointFirst, pointSecond, gridPoint.real )
			addYIntersectionPathToList( pathIndex, pointIndex, gridPoint.imag, yIntersection, yIntersectionPaths )
	if len( yIntersectionPaths ) < 1:
		return
	yCloseToCenterPaths = []
	if isDoubleJunction:
		yCloseToCenterPaths = getClosestOppositeIntersectionPaths( yIntersectionPaths )
	else:
		yIntersectionPaths.sort( compareDistanceFromCenter )
		yCloseToCenterPaths = [ yIntersectionPaths[0] ]
	for yCloseToCenterPath in yCloseToCenterPaths:
		setIsOutside( yCloseToCenterPath, aroundIntersectionPaths )
	if len( yCloseToCenterPaths ) < 2:
		yCloseToCenterPaths[0].gridPoint = gridPoint
		insertGridPointPair( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, paths, pixelTable, yCloseToCenterPaths[0], width )
		return
	plusMinusSign = getPlusMinusSign( yCloseToCenterPaths[1].y - yCloseToCenterPaths[0].y )
	yCloseToCenterPaths[0].gridPoint = complex( gridPoint.real, gridPoint.imag - plusMinusSign * gridPointInsetY )
	yCloseToCenterPaths[1].gridPoint = complex( gridPoint.real, gridPoint.imag + plusMinusSign * gridPointInsetY )
	yCloseToCenterPaths.sort( comparePointIndexDescending )
	insertGridPointPairs( gridPoint, gridPointInsetX, gridPoints, yCloseToCenterPaths[0], yCloseToCenterPaths[1], isBothOrNone, isJunctionWide, paths, pixelTable, width )

def addLoop(infillWidth, infillPaths, loop, rotationPlaneAngle):
	"Add simplified path to fill."
	simplifiedLoop = euclidean.getSimplifiedLoop(loop, infillWidth)
	if len(simplifiedLoop) < 2:
		return
	simplifiedLoop.append(simplifiedLoop[0])
	planeRotated = euclidean.getPointsRoundZAxis(rotationPlaneAngle, simplifiedLoop)
	infillPaths.append(planeRotated)

def addPath(infillWidth, infillPaths, path, rotationPlaneAngle):
	"Add simplified path to fill."
	simplifiedPath = euclidean.getSimplifiedPath(path, infillWidth)
	if len(simplifiedPath) < 2:
		return
	planeRotated = euclidean.getPointsRoundZAxis(rotationPlaneAngle, simplifiedPath)
	infillPaths.append(planeRotated)

def addPathIndexFirstSegment( gridPixel, pathIndexTable, pixelTable, segmentFirstPixel ):
	"Add the path index of the closest segment found toward the second segment."
	for yStep in xrange( gridPixel[1], segmentFirstPixel[1] - 1, - 1 ):
		if getKeyIsInPixelTableAddValue( ( gridPixel[0], yStep ), pathIndexTable, pixelTable ):
			return

def addPathIndexSecondSegment( gridPixel, pathIndexTable, pixelTable, segmentSecondPixel ):
	"Add the path index of the closest segment found toward the second segment."
	for yStep in xrange( gridPixel[1], segmentSecondPixel[1] + 1 ):
		if getKeyIsInPixelTableAddValue( ( gridPixel[0], yStep ), pathIndexTable, pixelTable ):
			return

def addPointOnPath( path, pathIndex, pixelTable, point, pointIndex, width ):
	"Add a point to a path and the pixel table."
	pointIndexMinusOne = pointIndex - 1
	if pointIndex < len(path) and pointIndexMinusOne >= 0:
		segmentTable = {}
		begin = path[ pointIndexMinusOne ]
		end = path[ pointIndex ]
		euclidean.addValueSegmentToPixelTable( begin, end, segmentTable, pathIndex, width )
		euclidean.removePixelTableFromPixelTable( segmentTable, pixelTable )
	if pointIndexMinusOne >= 0:
		begin = path[ pointIndexMinusOne ]
		euclidean.addValueSegmentToPixelTable( begin, point, pixelTable, pathIndex, width )
	if pointIndex < len(path):
		end = path[ pointIndex ]
		euclidean.addValueSegmentToPixelTable( point, end, pixelTable, pathIndex, width )
	path.insert( pointIndex, point )

def addPointOnPathIfFree( path, pathIndex, pixelTable, point, pointIndex, width ):
	"Add the closest point to a path, if the point added to a path is free."
	if isAddedPointOnPathFree( path, pixelTable, point, pointIndex, width ):
		addPointOnPath( path, pathIndex, pixelTable, point, pointIndex, width )

def addSparseEndpoints( doubleExtrusionWidth, endpoints, fillLine, horizontalSegmentLists, infillSolidity, removedEndpoints, solidSurfaceThickness, surroundingXIntersections ):
	"Add sparse endpoints."
	horizontalEndpoints = horizontalSegmentLists[ fillLine ]
	for segment in horizontalEndpoints:
		addSparseEndpointsFromSegment( doubleExtrusionWidth, endpoints, fillLine, horizontalSegmentLists, infillSolidity, removedEndpoints, segment, solidSurfaceThickness, surroundingXIntersections )

def addSparseEndpointsFromSegment( doubleExtrusionWidth, endpoints, fillLine, horizontalSegmentLists, infillSolidity, removedEndpoints, segment, solidSurfaceThickness, surroundingXIntersections ):
	"Add sparse endpoints from a segment."
	endpointFirstPoint = segment[0].point
	endpointSecondPoint = segment[1].point
	if surroundingXIntersections == None:
		endpoints += segment
		return
	if infillSolidity > 0.0:
		if fillLine < 1 or fillLine >= len( horizontalSegmentLists ) - 1:
			endpoints += segment
			return
		if int( round( round( fillLine * infillSolidity ) / infillSolidity ) ) == fillLine:
			endpoints += segment
			return
		if abs( endpointFirstPoint - endpointSecondPoint ) < doubleExtrusionWidth:
			endpoints += segment
			return
		if not isSegmentAround( horizontalSegmentLists[ fillLine - 1 ], segment ):
			endpoints += segment
			return
		if not isSegmentAround( horizontalSegmentLists[ fillLine + 1 ], segment ):
			endpoints += segment
			return
	if solidSurfaceThickness == 0:
		removedEndpoints += segment
		return
	if isSegmentCompletelyInAnIntersection( segment, surroundingXIntersections ):
		removedEndpoints += segment
		return
	endpoints += segment

def addYIntersectionPathToList( pathIndex, pointIndex, y, yIntersection, yIntersectionPaths ):
	"Add the y intersection path to the y intersection paths."
	if yIntersection == None:
		return
	yIntersectionPath = YIntersectionPath( pathIndex, pointIndex, yIntersection )
	yIntersectionPath.yMinusCenter = yIntersection - y
	yIntersectionPaths.append( yIntersectionPath )

def compareDistanceFromCenter(self, other):
	"Get comparison in order to sort y intersections in ascending order of distance from the center."
	distanceFromCenter = abs( self.yMinusCenter )
	distanceFromCenterOther = abs( other.yMinusCenter )
	if distanceFromCenter > distanceFromCenterOther:
		return 1
	if distanceFromCenter < distanceFromCenterOther:
		return - 1
	return 0

def comparePointIndexDescending(self, other):
	"Get comparison in order to sort y intersections in descending order of point index."
	if self.pointIndex > other.pointIndex:
		return - 1
	if self.pointIndex < other.pointIndex:
		return 1
	return 0

def createExtraFillLoops( radius, shouldExtraLoopsBeAdded, surroundingLoop ):
	"Create extra fill loops."
	for innerSurrounding in surroundingLoop.innerSurroundings:
		createFillForSurroundings( radius, shouldExtraLoopsBeAdded, innerSurrounding.innerSurroundings )
	allFillLoops = getExtraFillLoops( surroundingLoop.getFillLoops(), radius )
	surroundingLoop.lastFillLoops = allFillLoops
	if shouldExtraLoopsBeAdded:
		surroundingLoop.extraLoops += allFillLoops

def createFillForSurroundings( radius, shouldExtraLoopsBeAdded, surroundingLoops ):
	"Create extra fill loops for surrounding loops."
	for surroundingLoop in surroundingLoops:
		createExtraFillLoops( radius, shouldExtraLoopsBeAdded, surroundingLoop )

def getAdditionalLength( path, point, pointIndex ):
	"Get the additional length added by inserting a point into a path."
	if pointIndex == 0:
		return abs( point - path[0] )
	if pointIndex == len(path):
		return abs( point - path[-1] )
	return abs( point - path[ pointIndex - 1 ] ) + abs( point - path[ pointIndex ] ) - abs( path[ pointIndex ] - path[ pointIndex - 1 ] )

def getCraftedText( fileName, gcodeText = '', repository=None):
	"Fill the inset file or gcode text."
	return getCraftedTextFromText( archive.getTextIfEmpty(fileName, gcodeText), repository )

def getCraftedTextFromText(gcodeText, repository=None):
	"Fill the inset gcode text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'fill'):
		return gcodeText
	if repository == None:
		repository = settings.getReadRepository( FillRepository() )
	if not repository.activateFill.value:
		return gcodeText
	return FillSkein().getCraftedGcode( repository, gcodeText )

def getClosestOppositeIntersectionPaths( yIntersectionPaths ):
	"Get the close to center paths, starting with the first and an additional opposite if it exists."
	yIntersectionPaths.sort( compareDistanceFromCenter )
	beforeFirst = yIntersectionPaths[0].yMinusCenter < 0.0
	yCloseToCenterPaths = [ yIntersectionPaths[0] ]
	for yIntersectionPath in yIntersectionPaths[1 :]:
		beforeSecond = yIntersectionPath.yMinusCenter < 0.0
		if beforeFirst != beforeSecond:
			yCloseToCenterPaths.append( yIntersectionPath )
			return yCloseToCenterPaths
	return yCloseToCenterPaths

def getExtraFillLoops(loops, radius):
	"Get extra loops between inside and outside loops."
	greaterThanRadius = 1.4 * radius
	extraFillLoops = []
	centers = intercircle.getCentersFromPoints(intercircle.getPointsFromLoops(loops, greaterThanRadius), greaterThanRadius)
	for center in centers:
		inset = intercircle.getSimplifiedInsetFromClockwiseLoop(center, radius)
		if intercircle.isLargeSameDirection(inset, center, radius):
			if euclidean.getIsInFilledRegion(loops, euclidean.getLeftPoint(inset)):
				inset.reverse()
				extraFillLoops.append(inset)
	return extraFillLoops

def getKeyIsInPixelTableAddValue( key, pathIndexTable, pixelTable ):
	"Determine if the key is in the pixel table, and if it is and if the value is not None add it to the path index table."
	if key in pixelTable:
		value = pixelTable[key]
		if value != None:
			pathIndexTable[value] = None
		return True
	return False

def getNonIntersectingGridPointLine( gridPointInsetX, isJunctionWide, paths, pixelTable, yIntersectionPath, width ):
	"Get the points around the grid point that is junction wide that do not intersect."
	pointIndexPlusOne = yIntersectionPath.getPointIndexPlusOne()
	path = yIntersectionPath.getPath(paths)
	begin = path[ yIntersectionPath.pointIndex ]
	end = path[ pointIndexPlusOne ]
	plusMinusSign = getPlusMinusSign( end.real - begin.real )
	if isJunctionWide:
		gridPointXFirst = complex( yIntersectionPath.gridPoint.real - plusMinusSign * gridPointInsetX, yIntersectionPath.gridPoint.imag )
		gridPointXSecond = complex( yIntersectionPath.gridPoint.real + plusMinusSign * gridPointInsetX, yIntersectionPath.gridPoint.imag )
		if isAddedPointOnPathFree( path, pixelTable, gridPointXSecond, pointIndexPlusOne, width ):
			if isAddedPointOnPathFree( path, pixelTable, gridPointXFirst, pointIndexPlusOne, width ):
				return [ gridPointXSecond, gridPointXFirst ]
			if isAddedPointOnPathFree( path, pixelTable, yIntersectionPath.gridPoint, pointIndexPlusOne, width ):
				return [ gridPointXSecond, yIntersectionPath.gridPoint ]
			return [ gridPointXSecond ]
	if isAddedPointOnPathFree( path, pixelTable, yIntersectionPath.gridPoint, pointIndexPlusOne, width ):
		return [ yIntersectionPath.gridPoint ]
	return []

def getPlusMinusSign(number):
	"Get one if the number is zero or positive else negative one."
	if number >= 0.0:
		return 1.0
	return - 1.0

def getNewRepository():
	"Get the repository constructor."
	return FillRepository()

def getWithLeastLength( path, point ):
	"Insert a point into a path, at the index at which the path would be shortest."
	if len(path) < 1:
		return 0
	shortestPointIndex = None
	shortestAdditionalLength = 999999999999999999.0
	for pointIndex in xrange( len(path) + 1 ):
		additionalLength = getAdditionalLength( path, point, pointIndex )
		if additionalLength < shortestAdditionalLength:
			shortestAdditionalLength = additionalLength
			shortestPointIndex = pointIndex
	return shortestPointIndex

def getYIntersectionInsideYSegment( segmentFirstY, segmentSecondY, beginComplex, endComplex, x ):
	"Get the y intersection inside the y segment if it does, else none."
	yIntersection = euclidean.getYIntersectionIfExists( beginComplex, endComplex, x )
	if yIntersection == None:
		return None
	if yIntersection < min( segmentFirstY, segmentSecondY ):
		return None
	if yIntersection <= max( segmentFirstY, segmentSecondY ):
		return yIntersection
	return None

def insertGridPointPair( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, paths, pixelTable, yIntersectionPath, width ):
	"Insert a pair of points around the grid point is is junction wide, otherwise inset one point."
	linePath = getNonIntersectingGridPointLine( gridPointInsetX, isJunctionWide, paths, pixelTable, yIntersectionPath, width )
	insertGridPointPairWithLinePath( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, linePath, paths, pixelTable, yIntersectionPath, width )

def insertGridPointPairs( gridPoint, gridPointInsetX, gridPoints, intersectionPathFirst, intersectionPathSecond, isBothOrNone, isJunctionWide, paths, pixelTable, width ):
	"Insert a pair of points around a pair of grid points."
	gridPointLineFirst = getNonIntersectingGridPointLine( gridPointInsetX, isJunctionWide, paths, pixelTable, intersectionPathFirst, width )
	if len( gridPointLineFirst ) < 1:
		if isBothOrNone:
			return
		intersectionPathSecond.gridPoint = gridPoint
		insertGridPointPair( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, paths, pixelTable, intersectionPathSecond, width )
		return
	gridPointLineSecond = getNonIntersectingGridPointLine( gridPointInsetX, isJunctionWide, paths, pixelTable, intersectionPathSecond, width )
	if len( gridPointLineSecond ) > 0:
		insertGridPointPairWithLinePath( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, gridPointLineFirst, paths, pixelTable, intersectionPathFirst, width )
		insertGridPointPairWithLinePath( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, gridPointLineSecond, paths, pixelTable, intersectionPathSecond, width )
		return
	if isBothOrNone:
		return
	originalGridPointFirst = intersectionPathFirst.gridPoint
	intersectionPathFirst.gridPoint = gridPoint
	gridPointLineFirstCenter = getNonIntersectingGridPointLine( gridPointInsetX, isJunctionWide, paths, pixelTable, intersectionPathFirst, width )
	if len( gridPointLineFirstCenter ) > 0:
		insertGridPointPairWithLinePath( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, gridPointLineFirstCenter, paths, pixelTable, intersectionPathFirst, width )
		return
	intersectionPathFirst.gridPoint = originalGridPointFirst
	insertGridPointPairWithLinePath( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, gridPointLineFirst, paths, pixelTable, intersectionPathFirst, width )

def insertGridPointPairWithLinePath( gridPoint, gridPointInsetX, gridPoints, isJunctionWide, linePath, paths, pixelTable, yIntersectionPath, width ):
	"Insert a pair of points around the grid point is is junction wide, otherwise inset one point."
	if len( linePath ) < 1:
		return
	if gridPoint in gridPoints:
		gridPoints.remove( gridPoint )
	intersectionBeginPoint = None
	moreThanInset = 2.1 * gridPointInsetX
	path = yIntersectionPath.getPath(paths)
	begin = path[ yIntersectionPath.pointIndex ]
	end = path[ yIntersectionPath.getPointIndexPlusOne() ]
	if yIntersectionPath.isOutside:
		distanceX = end.real - begin.real
		if abs( distanceX ) > 2.1 * moreThanInset:
			intersectionBeginXDistance = yIntersectionPath.gridPoint.real - begin.real
			endIntersectionXDistance = end.real - yIntersectionPath.gridPoint.real
			intersectionPoint = begin * endIntersectionXDistance / distanceX + end * intersectionBeginXDistance / distanceX
			distanceYAbsoluteInset = max( abs( yIntersectionPath.gridPoint.imag - intersectionPoint.imag ), moreThanInset )
			intersectionEndSegment = end - intersectionPoint
			intersectionEndSegmentLength = abs( intersectionEndSegment )
			if intersectionEndSegmentLength > 1.1 * distanceYAbsoluteInset:
				intersectionEndPoint = intersectionPoint + intersectionEndSegment * distanceYAbsoluteInset / intersectionEndSegmentLength
				path.insert( yIntersectionPath.getPointIndexPlusOne(), intersectionEndPoint )
			intersectionBeginSegment = begin - intersectionPoint
			intersectionBeginSegmentLength = abs( intersectionBeginSegment )
			if intersectionBeginSegmentLength > 1.1 * distanceYAbsoluteInset:
				intersectionBeginPoint = intersectionPoint + intersectionBeginSegment * distanceYAbsoluteInset / intersectionBeginSegmentLength
	for point in linePath:
		addPointOnPath( path, yIntersectionPath.pathIndex, pixelTable, point, yIntersectionPath.getPointIndexPlusOne(), width )
	if intersectionBeginPoint != None:
		addPointOnPath( path, yIntersectionPath.pathIndex, pixelTable, intersectionBeginPoint, yIntersectionPath.getPointIndexPlusOne(), width )

def isAddedPointOnPathFree( path, pixelTable, point, pointIndex, width ):
	"Determine if the point added to a path is intersecting the pixel table or the path."
	if pointIndex > 0 and pointIndex < len(path):
		if isSharpCorner( ( path[ pointIndex - 1 ] ), point, ( path[ pointIndex ] ) ):
			return False
	pointIndexMinusOne = pointIndex - 1
	if pointIndexMinusOne >= 0:
		maskTable = {}
		begin = path[ pointIndexMinusOne ]
		if pointIndex < len(path):
			end = path[ pointIndex ]
			euclidean.addValueSegmentToPixelTable( begin, end, maskTable, None, width )
		segmentTable = {}
		euclidean.addSegmentToPixelTable( point, begin, segmentTable, 0.0, 2.0, width )
		if euclidean.isPixelTableIntersecting( pixelTable, segmentTable, maskTable ):
			return False
		if isAddedPointOnPathIntersectingPath( begin, path, point, pointIndexMinusOne ):
			return False
	if pointIndex < len(path):
		maskTable = {}
		begin = path[ pointIndex ]
		if pointIndexMinusOne >= 0:
			end = path[ pointIndexMinusOne ]
			euclidean.addValueSegmentToPixelTable( begin, end, maskTable, None, width )
		segmentTable = {}
		euclidean.addSegmentToPixelTable( point, begin, segmentTable, 0.0, 2.0, width )
		if euclidean.isPixelTableIntersecting( pixelTable, segmentTable, maskTable ):
			return False
		if isAddedPointOnPathIntersectingPath( begin, path, point, pointIndex ):
			return False
	return True

def isAddedPointOnPathIntersectingPath( begin, path, point, pointIndex ):
	"Determine if the point added to a path is intersecting the path by checking line intersection."
	segment = point - begin
	segmentLength = abs( segment )
	if segmentLength <= 0.0:
		return False
	normalizedSegment = segment / segmentLength
	segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
	pointRotated = segmentYMirror * point
	beginRotated = segmentYMirror * begin
	if euclidean.isXSegmentIntersectingPath( path[ max( 0, pointIndex - 20 ) : pointIndex ], pointRotated.real, beginRotated.real, segmentYMirror, pointRotated.imag ):
		return True
	return euclidean.isXSegmentIntersectingPath( path[ pointIndex + 1 : pointIndex + 21 ], pointRotated.real, beginRotated.real, segmentYMirror, pointRotated.imag )

def isIntersectingLoopsPaths( loops, paths, pointBegin, pointEnd ):
	"Determine if the segment between the first and second point is intersecting the loop list."
	normalizedSegment = pointEnd.dropAxis(2) - pointBegin.dropAxis(2)
	normalizedSegmentLength = abs( normalizedSegment )
	if normalizedSegmentLength == 0.0:
		return False
	normalizedSegment /= normalizedSegmentLength
	segmentYMirror = complex( normalizedSegment.real, - normalizedSegment.imag )
	pointBeginRotated = euclidean.getRoundZAxisByPlaneAngle( segmentYMirror, pointBegin )
	pointEndRotated = euclidean.getRoundZAxisByPlaneAngle( segmentYMirror, pointEnd )
	if euclidean.isLoopListIntersectingInsideXSegment( loops, pointBeginRotated.real, pointEndRotated.real, segmentYMirror, pointBeginRotated.imag ):
		return True
	return euclidean.isXSegmentIntersectingPaths( paths, pointBeginRotated.real, pointEndRotated.real, segmentYMirror, pointBeginRotated.imag )

#def isPerimeterPathInSurroundLoops( surroundingLoops ):
#	"Determine if there is a perimeter path in the surrounding loops."
#	for surroundingLoop in surroundingLoops:
#		if len( surroundingLoop.perimeterPaths ) > 0:
#			return True
#	return False

def isPointAddedAroundClosest( pixelTable, layerExtrusionWidth, paths, removedEndpointPoint, width ):
	"Add the closest removed endpoint to the path, with minimal twisting."
	closestDistanceSquared = 999999999999999999.0
	closestPathIndex = None
	for pathIndex in xrange( len(paths) ):
		path = paths[ pathIndex ]
		for pointIndex in xrange( len(path) ):
			point = path[ pointIndex ]
			distanceSquared = abs( point - removedEndpointPoint )
			if distanceSquared < closestDistanceSquared:
				closestDistanceSquared = distanceSquared
				closestPathIndex = pathIndex
	if closestPathIndex == None:
		return
	if closestDistanceSquared < 0.8 * layerExtrusionWidth * layerExtrusionWidth:
		return
	closestPath = paths[ closestPathIndex ]
	closestPointIndex = getWithLeastLength( closestPath, removedEndpointPoint )
	if isAddedPointOnPathFree( closestPath, pixelTable, removedEndpointPoint, closestPointIndex, width ):
		addPointOnPath( closestPath, closestPathIndex, pixelTable, removedEndpointPoint, closestPointIndex, width )
		return True
	return isSidePointAdded( pixelTable, closestPath, closestPathIndex, closestPointIndex, layerExtrusionWidth, removedEndpointPoint, width )

def isSegmentAround( aroundSegments, segment ):
	"Determine if there is another segment around."
	for aroundSegment in aroundSegments:
		endpoint = aroundSegment[0]
		if isSegmentInX( segment, endpoint.point.real, endpoint.otherEndpoint.point.real ):
			return True
	return False

def isSegmentCompletelyInAnIntersection( segment, xIntersections ):
	"Add sparse endpoints from a segment."
	for xIntersectionIndex in xrange( 0, len( xIntersections ), 2 ):
		surroundingXFirst = xIntersections[ xIntersectionIndex ]
		surroundingXSecond = xIntersections[ xIntersectionIndex + 1 ]
		if euclidean.isSegmentCompletelyInX( segment, surroundingXFirst, surroundingXSecond ):
			return True
	return False

def isSegmentInX( segment, xFirst, xSecond ):
	"Determine if the segment overlaps within x."
	segmentFirstX = segment[0].point.real
	segmentSecondX = segment[1].point.real
	if min( segmentFirstX, segmentSecondX ) > max( xFirst, xSecond ):
		return False
	return max( segmentFirstX, segmentSecondX ) > min( xFirst, xSecond )

def isSharpCorner( beginComplex, centerComplex, endComplex ):
	"Determine if the three complex points form a sharp corner."
	centerBeginComplex = beginComplex - centerComplex
	centerEndComplex = endComplex - centerComplex
	centerBeginLength = abs( centerBeginComplex )
	centerEndLength = abs( centerEndComplex )
	if centerBeginLength <= 0.0 or centerEndLength <= 0.0:
		return False
	centerBeginComplex /= centerBeginLength
	centerEndComplex /= centerEndLength
	return euclidean.getDotProduct( centerBeginComplex, centerEndComplex ) > 0.9

def isSidePointAdded( pixelTable, closestPath, closestPathIndex, closestPointIndex, layerExtrusionWidth, removedEndpointPoint, width ):
	"Add side point along with the closest removed endpoint to the path, with minimal twisting."
	if closestPointIndex <= 0 or closestPointIndex >= len( closestPath ):
		return False
	pointBegin = closestPath[ closestPointIndex - 1 ]
	pointEnd = closestPath[ closestPointIndex ]
	removedEndpointPoint = removedEndpointPoint
	closest = pointBegin
	farthest = pointEnd
	removedMinusClosest = removedEndpointPoint - pointBegin
	removedMinusClosestLength = abs( removedMinusClosest )
	if removedMinusClosestLength <= 0.0:
		return False
	removedMinusOther = removedEndpointPoint - pointEnd
	removedMinusOtherLength = abs( removedMinusOther )
	if removedMinusOtherLength <= 0.0:
		return False
	insertPointAfter = None
	insertPointBefore = None
	if removedMinusOtherLength < removedMinusClosestLength:
		closest = pointEnd
		farthest = pointBegin
		removedMinusClosest = removedMinusOther
		removedMinusClosestLength = removedMinusOtherLength
		insertPointBefore = removedEndpointPoint
	else:
		insertPointAfter = removedEndpointPoint
	removedMinusClosestNormalized = removedMinusClosest / removedMinusClosestLength
	perpendicular = removedMinusClosestNormalized * complex( 0.0, layerExtrusionWidth )
	sidePoint = removedEndpointPoint + perpendicular
	#extra check in case the line to the side point somehow slips by the line to the perpendicular
	sidePointOther = removedEndpointPoint - perpendicular
	if abs( sidePoint -  farthest ) > abs( sidePointOther -  farthest ):
		perpendicular = - perpendicular
		sidePoint = sidePointOther
	maskTable = {}
	closestSegmentTable = {}
	toPerpendicularTable = {}
	euclidean.addValueSegmentToPixelTable( pointBegin, pointEnd, maskTable, None, width )
	euclidean.addValueSegmentToPixelTable( closest, removedEndpointPoint, closestSegmentTable, None, width )
	euclidean.addValueSegmentToPixelTable( sidePoint, farthest, toPerpendicularTable, None, width )
	if euclidean.isPixelTableIntersecting( pixelTable, toPerpendicularTable, maskTable ) or euclidean.isPixelTableIntersecting( closestSegmentTable, toPerpendicularTable, maskTable ):
		sidePoint = removedEndpointPoint - perpendicular
		toPerpendicularTable = {}
		euclidean.addValueSegmentToPixelTable( sidePoint, farthest, toPerpendicularTable, None, width )
		if euclidean.isPixelTableIntersecting( pixelTable, toPerpendicularTable, maskTable ) or euclidean.isPixelTableIntersecting( closestSegmentTable, toPerpendicularTable, maskTable ):
			return False
	if insertPointBefore != None:
		addPointOnPathIfFree( closestPath, closestPathIndex, pixelTable, insertPointBefore, closestPointIndex, width )
	addPointOnPathIfFree( closestPath, closestPathIndex, pixelTable, sidePoint, closestPointIndex, width )
	if insertPointAfter != None:
		addPointOnPathIfFree( closestPath, closestPathIndex, pixelTable, insertPointAfter, closestPointIndex, width )
	return True

def removeEndpoints( pixelTable, layerExtrusionWidth, paths, removedEndpoints, aroundWidth ):
	"Remove endpoints which are added to the path."
	for removedEndpointIndex in xrange( len(removedEndpoints) - 1, - 1, - 1 ):
		removedEndpoint = removedEndpoints[ removedEndpointIndex ]
		removedEndpointPoint = removedEndpoint.point
		if isPointAddedAroundClosest( pixelTable, layerExtrusionWidth, paths, removedEndpointPoint, aroundWidth ):
			removedEndpoints.remove( removedEndpoint )

def setIsOutside( yCloseToCenterPath, yIntersectionPaths ):
	"Determine if the yCloseToCenterPath is outside."
	beforeClose = yCloseToCenterPath.yMinusCenter < 0.0
	for yIntersectionPath in yIntersectionPaths:
		if yIntersectionPath != yCloseToCenterPath:
			beforePath = yIntersectionPath.yMinusCenter < 0.0
			if beforeClose == beforePath:
				yCloseToCenterPath.isOutside = False
				return
	yCloseToCenterPath.isOutside = True

def writeOutput(fileName=''):
	"Fill an inset gcode file."
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified(fileName)
	if fileName != '':
		skeinforge_craft.writeChainTextWithNounMessage( fileName, 'fill')


class FillRepository:
	"A class to handle the fill settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository('skeinforge_application.skeinforge_plugins.craft_plugins.fill.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Fill', self, '')
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute('http://fabmetheus.crsndoo.com/wiki/index.php/Skeinforge_Fill')
		self.activateFill = settings.BooleanSetting().getFromValue('Activate Fill:', self, True )
		settings.LabelSeparator().getFromRepository(self)
		settings.LabelDisplay().getFromName('- Diaphragm -', self )
		self.diaphragmPeriod = settings.IntSpin().getFromValue( 20, 'Diaphragm Period (layers):', self, 200, 100 )
		self.diaphragmThickness = settings.IntSpin().getFromValue( 0, 'Diaphragm Thickness (layers):', self, 5, 0 )
		settings.LabelSeparator().getFromRepository(self)
		settings.LabelDisplay().getFromName('- Extra Shells -', self )
		self.extraShellsAlternatingSolidLayer = settings.IntSpin().getFromValue( 0, 'Extra Shells on Alternating Solid Layer (layers):', self, 3, 2 )
		self.extraShellsBase = settings.IntSpin().getFromValue( 0, 'Extra Shells on Base (layers):', self, 3, 1 )
		self.extraShellsSparseLayer = settings.IntSpin().getFromValue( 0, 'Extra Shells on Sparse Layer (layers):', self, 3, 1 )
		settings.LabelSeparator().getFromRepository(self)
		settings.LabelDisplay().getFromName('- Grid -', self )
		self.gridCircleSeparationOverPerimeterWidth = settings.FloatSpin().getFromValue(0.0, 'Grid Circle Separation over Perimeter Width (ratio):', self, 1.0, 0.2)
		self.gridExtraOverlap = settings.FloatSpin().getFromValue( 0.0, 'Grid Extra Overlap (ratio):', self, 0.5, 0.1 )
		self.gridJunctionSeparationBandHeight = settings.IntSpin().getFromValue( 0, 'Grid Junction Separation Band Height (layers):', self, 20, 10 )
		self.gridJunctionSeparationOverOctogonRadiusAtEnd = settings.FloatSpin().getFromValue( 0.0, 'Grid Junction Separation over Octogon Radius At End (ratio):', self, 0.8, 0.0 )
		self.gridJunctionSeparationOverOctogonRadiusAtMiddle = settings.FloatSpin().getFromValue( 0.0, 'Grid Junction Separation over Octogon Radius At Middle (ratio):', self, 0.8, 0.0 )
		settings.LabelSeparator().getFromRepository(self)
		settings.LabelDisplay().getFromName('- Infill -', self )
		self.infillBeginRotation = settings.FloatSpin().getFromValue( 0.0, 'Infill Begin Rotation (degrees):', self, 90.0, 45.0 )
		self.infillBeginRotationRepeat = settings.IntSpin().getFromValue( 0, 'Infill Begin Rotation Repeat (layers):', self, 3, 1 )
		self.infillInteriorDensityOverExteriorDensity = settings.FloatSpin().getFromValue( 0.8, 'Infill Interior Density over Exterior Density (ratio):', self, 1.0, 0.9 )
		self.infillOddLayerExtraRotation = settings.FloatSpin().getFromValue( 30.0, 'Infill Odd Layer Extra Rotation (degrees):', self, 90.0, 90.0 )
		self.infillPatternLabel = settings.LabelDisplay().getFromName('Infill Pattern:', self )
		infillLatentStringVar = settings.LatentStringVar()
		self.infillPatternGridCircular = settings.Radio().getFromRadio( infillLatentStringVar, 'Grid Circular', self, False )
		self.infillPatternGridHexagonal = settings.Radio().getFromRadio( infillLatentStringVar, 'Grid Hexagonal', self, False )
		self.infillPatternGridRectangular = settings.Radio().getFromRadio( infillLatentStringVar, 'Grid Rectangular', self, False )
		self.infillPatternLine = settings.Radio().getFromRadio( infillLatentStringVar, 'Line', self, True )
		self.infillPerimeterOverlap = settings.FloatSpin().getFromValue( 0.0, 'Infill Perimeter Overlap (ratio):', self, 0.4, 0.15 )
		self.infillSolidity = settings.FloatSpin().getFromValue( 0.04, 'Infill Solidity (ratio):', self, 0.3, 0.2 )
		self.infillWidthOverThickness = settings.FloatSpin().getFromValue( 1.3, 'Infill Width over Thickness (ratio):', self, 1.7, 1.5 )
		settings.LabelSeparator().getFromRepository(self)
		self.solidSurfaceThickness = settings.IntSpin().getFromValue( 0, 'Solid Surface Thickness (layers):', self, 5, 3 )
		self.threadSequenceChoice = settings.MenuButtonDisplay().getFromName('Thread Sequence Choice:', self )
		self.threadSequenceInfillLoops = settings.MenuRadio().getFromMenuButtonDisplay( self.threadSequenceChoice, 'Infill > Loops > Perimeter', self, False )
		self.threadSequenceInfillPerimeter = settings.MenuRadio().getFromMenuButtonDisplay( self.threadSequenceChoice, 'Infill > Perimeter > Loops', self, False )
		self.threadSequenceLoopsInfill = settings.MenuRadio().getFromMenuButtonDisplay( self.threadSequenceChoice, 'Loops > Infill > Perimeter', self, False )
		self.threadSequenceLoopsPerimeter = settings.MenuRadio().getFromMenuButtonDisplay( self.threadSequenceChoice, 'Loops > Perimeter > Infill', self, True )
		self.threadSequencePerimeterInfill = settings.MenuRadio().getFromMenuButtonDisplay( self.threadSequenceChoice, 'Perimeter > Infill > Loops', self, False )
		self.threadSequencePerimeterLoops = settings.MenuRadio().getFromMenuButtonDisplay( self.threadSequenceChoice, 'Perimeter > Loops > Infill', self, False )
		self.executeTitle = 'Fill'

	def execute(self):
		"Fill button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode(self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled)
		for fileName in fileNames:
			writeOutput(fileName)


class FillSkein:
	"A class to fill a skein of extrusions."
	def __init__(self):
		self.bridgeWidthMultiplier = 1.0
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.extruderActive = False
		self.fillInset = 0.18
		self.isPerimeter = False
		self.lastExtraShells = - 1
		self.lineIndex = 0
		self.oldLocation = None
		self.oldOrderedLocation = Vector3()
		self.perimeterWidth = None
		self.rotatedLayer = None
		self.rotatedLayers = []
		self.shutdownLineIndex = sys.maxint
		self.surroundingLoop = None
		self.thread = None

	def addFill(self, layerIndex):
		"Add fill to the carve layer."
#		if layerIndex > 2:
#			return
		settings.printProgressByNumber(layerIndex, len(self.rotatedLayers), 'fill')
		alreadyFilledArounds = []
		pixelTable = {}
		arounds = []
		betweenWidth = self.betweenWidth
		self.layerExtrusionWidth = self.infillWidth
		layerFillInset = self.fillInset
		rotatedLayer = self.rotatedLayers[ layerIndex ]
		self.distanceFeedRate.addLine('(<layer> %s )' % rotatedLayer.z )
		layerRotation = self.getLayerRotation(layerIndex)
		reverseRotation = complex( layerRotation.real, - layerRotation.imag )
		surroundingCarves = []
		layerRemainder = layerIndex % int( round( self.repository.diaphragmPeriod.value ) )
		if layerRemainder >= int( round( self.repository.diaphragmThickness.value ) ) and rotatedLayer.rotation == None:
			for surroundingIndex in xrange( 1, self.solidSurfaceThickness + 1 ):
				self.addRotatedCarve( layerIndex - surroundingIndex, reverseRotation, surroundingCarves )
				self.addRotatedCarve( layerIndex + surroundingIndex, reverseRotation, surroundingCarves )
		extraShells = self.repository.extraShellsSparseLayer.value
		if len(surroundingCarves) < self.doubleSolidSurfaceThickness:
			extraShells = self.repository.extraShellsAlternatingSolidLayer.value
			if self.lastExtraShells != self.repository.extraShellsBase.value:
				extraShells = self.repository.extraShellsBase.value
		if rotatedLayer.rotation != None:
			extraShells = 0
			betweenWidth *= self.bridgeWidthMultiplier
			self.layerExtrusionWidth *= self.bridgeWidthMultiplier
			layerFillInset *= self.bridgeWidthMultiplier
			self.distanceFeedRate.addLine('(<bridgeRotation> %s )' % rotatedLayer.rotation )
		aroundInset = 0.25 * self.layerExtrusionWidth
		aroundWidth = 0.25 * self.layerExtrusionWidth
		self.lastExtraShells = extraShells
		gridPointInsetX = 0.5 * layerFillInset
		doubleExtrusionWidth = 2.0 * self.layerExtrusionWidth
		endpoints = []
		infillPaths = []
		layerInfillSolidity = self.infillSolidity
		self.isDoubleJunction = True
		self.isJunctionWide = True
		if self.repository.infillPatternGridHexagonal.value:
			if abs( euclidean.getDotProduct( layerRotation, euclidean.getWiddershinsUnitPolar( self.infillBeginRotation ) ) ) < math.sqrt( 0.5 ):
				layerInfillSolidity *= 0.5
				self.isDoubleJunction = False
			else:
				self.isJunctionWide = False
		rotatedLoops = []
#		for surroundingLoop in rotatedLayer.surroundingLoops:
#			surroundingLoop.fillBoundaries = intercircle.getInsetLoopsFromLoop( surroundingLoop.boundary, betweenWidth )
#			surroundingLoop.lastExistingFillLoops = surroundingLoop.fillBoundaries
		surroundingLoops = euclidean.getOrderedSurroundingLoops( self.layerExtrusionWidth, rotatedLayer.surroundingLoops )
#		if isPerimeterPathInSurroundLoops( surroundingLoops ):
#			extraShells = 0
		createFillForSurroundings( betweenWidth, False, surroundingLoops )
		for extraShellIndex in xrange( extraShells ):
			createFillForSurroundings( self.layerExtrusionWidth, True, surroundingLoops )
		fillLoops = euclidean.getFillOfSurroundings( surroundingLoops )
		slightlyGreaterThanFill = 1.01 * layerFillInset
		for loop in fillLoops:
			alreadyFilledLoop = []
			alreadyFilledArounds.append( alreadyFilledLoop )
			planeRotatedPerimeter = euclidean.getPointsRoundZAxis( reverseRotation, loop )
			rotatedLoops.append(planeRotatedPerimeter)
			centers = intercircle.getCentersFromLoop( planeRotatedPerimeter, slightlyGreaterThanFill )
			euclidean.addLoopToPixelTable( planeRotatedPerimeter, pixelTable, aroundWidth )
			for center in centers:
				alreadyFilledInset = intercircle.getSimplifiedInsetFromClockwiseLoop( center, layerFillInset )
				if intercircle.isLargeSameDirection( alreadyFilledInset, center, layerFillInset ):
					alreadyFilledLoop.append( alreadyFilledInset )
					around = intercircle.getSimplifiedInsetFromClockwiseLoop( center, aroundInset )
					if euclidean.isPathInsideLoop( planeRotatedPerimeter, around ) == euclidean.isWiddershins(planeRotatedPerimeter):
						around.reverse()
						arounds.append(around)
						euclidean.addLoopToPixelTable( around, pixelTable, aroundWidth )
		if len( arounds ) < 1:
			self.addThreadsBridgeLayer( rotatedLayer, surroundingLoops )
			return
		back = euclidean.getBackOfLoops( arounds )
		front = euclidean.getFrontOfLoops( arounds )
		area = self.getCarveArea(layerIndex)
		if area > 0.0 and len(surroundingCarves) >= self.doubleSolidSurfaceThickness:
			areaChange = 0.0
			for surroundingIndex in xrange( 1, self.solidSurfaceThickness + 1 ):
				areaChange = max( areaChange, self.getAreaChange( area, layerIndex - surroundingIndex ) )
				areaChange = max( areaChange, self.getAreaChange( area, layerIndex + surroundingIndex ) )
			if areaChange < 0.5 or self.solidSurfaceThickness == 0:
				if self.repository.infillInteriorDensityOverExteriorDensity.value <= 0.0:
					self.addThreadsBridgeLayer( rotatedLayer, surroundingLoops )
				self.layerExtrusionWidth /= self.repository.infillInteriorDensityOverExteriorDensity.value
		front = math.ceil( front / self.layerExtrusionWidth ) * self.layerExtrusionWidth
		fillWidth = back - front
		numberOfLines = int( math.ceil( fillWidth / self.layerExtrusionWidth ) )
		self.frontOverWidth = 0.0
		self.horizontalSegmentLists = euclidean.getHorizontalSegmentListsFromLoopLists( alreadyFilledArounds, front, numberOfLines, rotatedLoops, self.layerExtrusionWidth )
		self.surroundingXIntersectionLists = []
		self.yList = []
		gridCircular = False
		removedEndpoints = []
		if len(surroundingCarves) >= self.doubleSolidSurfaceThickness:
			if self.repository.infillPatternGridCircular.value and self.getIsDensitySolidityPositive():
				gridCircular = True
				layerInfillSolidity = 0.0
			xIntersectionIndexLists = []
			self.frontOverWidth = euclidean.getFrontOverWidthAddXListYList( front, surroundingCarves, numberOfLines, xIntersectionIndexLists, self.layerExtrusionWidth, self.yList )
			for fillLine in xrange( len( self.horizontalSegmentLists ) ):
				xIntersectionIndexList = xIntersectionIndexLists[ fillLine ]
				surroundingXIntersections = euclidean.getIntersectionOfXIntersectionIndexes( self.doubleSolidSurfaceThickness, xIntersectionIndexList )
				self.surroundingXIntersectionLists.append( surroundingXIntersections )
				addSparseEndpoints( doubleExtrusionWidth, endpoints, fillLine, self.horizontalSegmentLists, layerInfillSolidity, removedEndpoints, self.solidSurfaceThickness, surroundingXIntersections )
		else:
			for fillLine in xrange( len( self.horizontalSegmentLists ) ):
				addSparseEndpoints( doubleExtrusionWidth, endpoints, fillLine, self.horizontalSegmentLists, layerInfillSolidity, removedEndpoints, self.solidSurfaceThickness, None )
		paths = euclidean.getPathsFromEndpoints( endpoints, self.layerExtrusionWidth, pixelTable, aroundWidth )
		if gridCircular:
			startAngle = euclidean.globalGoldenAngle * float(layerIndex)
			for gridPoint in self.getGridPoints(fillLoops, reverseRotation):
				self.addGridCircle(gridPoint, infillPaths, layerRotation, pixelTable, rotatedLoops, layerRotation, aroundWidth)
		else:
			if self.isGridToBeExtruded():
				self.addGrid( arounds, fillLoops, gridPointInsetX, layerIndex, paths, pixelTable, reverseRotation, surroundingCarves, aroundWidth )
			oldRemovedEndpointLength = len(removedEndpoints) + 1
			while oldRemovedEndpointLength - len(removedEndpoints) > 0:
				oldRemovedEndpointLength = len(removedEndpoints)
				removeEndpoints( pixelTable, self.layerExtrusionWidth, paths, removedEndpoints, aroundWidth )
			paths = euclidean.getConnectedPaths( paths, pixelTable, aroundWidth )
		for path in paths:
			addPath( self.layerExtrusionWidth, infillPaths, path, layerRotation )
		euclidean.transferPathsToSurroundingLoops( infillPaths, surroundingLoops )
		self.addThreadsBridgeLayer( rotatedLayer, surroundingLoops )

	def addGcodeFromThreadZ( self, thread, z ):
		"Add a gcode thread to the output."
		self.distanceFeedRate.addGcodeFromThreadZ( thread, z )

	def addGrid(self, arounds, fillLoops, gridPointInsetX, layerIndex, paths, pixelTable, reverseRotation, surroundingCarves, width):
		"Add the grid to the infill layer."
		if len(surroundingCarves) < self.doubleSolidSurfaceThickness:
			return
		explodedPaths = []
		pathGroups = []
		for path in paths:
			pathIndexBegin = len( explodedPaths )
			for pointIndex in xrange( len(path) - 1 ):
				pathSegment = [ path[ pointIndex ], path[ pointIndex + 1 ] ]
				explodedPaths.append( pathSegment )
			pathGroups.append( ( pathIndexBegin, len( explodedPaths ) ) )
		for pathIndex in xrange( len( explodedPaths ) ):
			explodedPath = explodedPaths[ pathIndex ]
			euclidean.addPathToPixelTable( explodedPath, pixelTable, pathIndex, width )
		gridPoints = self.getGridPoints(fillLoops, reverseRotation)
		gridPointInsetY = gridPointInsetX * ( 1.0 - self.repository.gridExtraOverlap.value )
		if self.repository.infillPatternGridRectangular.value:
			gridBandHeight = self.repository.gridJunctionSeparationBandHeight.value
			gridLayerRemainder = ( layerIndex - self.solidSurfaceThickness ) % gridBandHeight
			halfBandHeight = 0.5 * float( gridBandHeight )
			halfBandHeightFloor = math.floor( halfBandHeight )
			fromMiddle = math.floor( abs( gridLayerRemainder - halfBandHeight ) )
			fromEnd = halfBandHeightFloor - fromMiddle
			gridJunctionSeparation = self.gridJunctionSeparationAtEnd * fromMiddle + self.gridJunctionSeparationAtMiddle * fromEnd
			gridJunctionSeparation /= halfBandHeightFloor
			gridPointInsetX += gridJunctionSeparation
			gridPointInsetY += gridJunctionSeparation
		oldGridPointLength = len( gridPoints ) + 1
		while oldGridPointLength - len( gridPoints ) > 0:
			oldGridPointLength = len( gridPoints )
			self.addRemainingGridPoints( arounds, gridPointInsetX, gridPointInsetY, gridPoints, True, explodedPaths, pixelTable, width )
		oldGridPointLength = len( gridPoints ) + 1
		while oldGridPointLength - len( gridPoints ) > 0:
			oldGridPointLength = len( gridPoints )
			self.addRemainingGridPoints( arounds, gridPointInsetX, gridPointInsetY, gridPoints, False, explodedPaths, pixelTable, width )
		for pathGroupIndex in xrange( len( pathGroups ) ):
			pathGroup = pathGroups[ pathGroupIndex ]
			paths[ pathGroupIndex ] = []
			for explodedPathIndex in xrange( pathGroup[0], pathGroup[1] ):
				explodedPath = explodedPaths[ explodedPathIndex ]
				if len( paths[ pathGroupIndex ] ) == 0:
					paths[ pathGroupIndex ] = explodedPath
				else:
					paths[ pathGroupIndex ] += explodedPath[1 :]

	def addGridCircle(self, center, infillPaths, layerRotation, pixelTable, rotatedLoops, startRotation, width):
		"Add circle to the grid."
		startAngle = -math.atan2(startRotation.imag, startRotation.real)
		loop = euclidean.getComplexPolygon(center, self.gridCircleRadius, 17, startAngle)
		loopPixelDictionary = {}
		euclidean.addLoopToPixelTable(loop, loopPixelDictionary, width)
		if not euclidean.isPixelTableIntersecting(pixelTable, loopPixelDictionary):
			if euclidean.getIsInFilledRegion(rotatedLoops, euclidean.getLeftPoint(loop)):
				addLoop(self.layerExtrusionWidth, infillPaths, loop, layerRotation)
				return
		insideIndexPaths = []
		insideIndexPath = None
		for pointIndex, point in enumerate(loop):
			nextPoint = loop[(pointIndex + 1) % len(loop)]
			segmentDictionary = {}
			euclidean.addValueSegmentToPixelTable(point, nextPoint, segmentDictionary, None, width)
			euclidean.addSquareTwoToPixelDictionary(segmentDictionary, point, None, width)
			euclidean.addSquareTwoToPixelDictionary(segmentDictionary, nextPoint, None, width)
			shouldAddLoop = not euclidean.isPixelTableIntersecting(pixelTable, segmentDictionary)
			if shouldAddLoop:
				shouldAddLoop = euclidean.getIsInFilledRegion(rotatedLoops, point)
			if shouldAddLoop:
				if insideIndexPath == None:
					insideIndexPath = [pointIndex]
					insideIndexPaths.append(insideIndexPath)
				else:
					insideIndexPath.append(pointIndex)
			else:
				insideIndexPath = None
		if len(insideIndexPaths) > 1:
			insideIndexPathFirst = insideIndexPaths[0]
			insideIndexPathLast = insideIndexPaths[-1]
			if insideIndexPathFirst[0] == 0 and insideIndexPathLast[-1] == len(loop) - 1:
				insideIndexPaths[0] = insideIndexPathLast + insideIndexPathFirst
				del insideIndexPaths[-1]
		for insideIndexPath in insideIndexPaths:
			path = []
			for insideIndex in insideIndexPath:
				if len(path) == 0:
					path.append(loop[insideIndex])
				path.append(loop[(insideIndex + 1) % len(loop)])
			addPath(self.layerExtrusionWidth, infillPaths, path, layerRotation)

	def addGridLinePoints( self, begin, end, gridPoints, gridRotationAngle, offset, y ):
		"Add the segments of one line of a grid to the infill."
		if self.gridRadius == 0.0:
			return
		gridXStep = int(math.floor((begin) / self.gridXStepSize)) - 3
		gridXOffset = offset + self.gridXStepSize * float(gridXStep)
		while gridXOffset < end:
			if gridXOffset >= begin:
				gridPointComplex = complex(gridXOffset, y) * gridRotationAngle
				if self.repository.infillPatternGridCircular.value or self.isPointInsideLineSegments(gridPointComplex):
					gridPoints.append(gridPointComplex)
			gridXStep = self.getNextGripXStep(gridXStep)
			gridXOffset = offset + self.gridXStepSize * float(gridXStep)

	def addRemainingGridPoints( self, arounds, gridPointInsetX, gridPointInsetY, gridPoints, isBothOrNone, paths, pixelTable, width ):
		"Add the remaining grid points to the grid point list."
		for gridPointIndex in xrange( len( gridPoints ) - 1, - 1, - 1 ):
			gridPoint = gridPoints[ gridPointIndex ]
			addAroundGridPoint( arounds, gridPoint, gridPointInsetX, gridPointInsetY, gridPoints, self.gridRadius, isBothOrNone, self.isDoubleJunction, self.isJunctionWide, paths, pixelTable, width )

	def addRotatedCarve( self, layerIndex, reverseRotation, surroundingCarves ):
		"Add a rotated carve to the surrounding carves."
		if layerIndex < 0 or layerIndex >= len( self.rotatedLayers ):
			return
		surroundingLoops = self.rotatedLayers[ layerIndex ].surroundingLoops
		rotatedCarve = []
		for surroundingLoop in surroundingLoops:
			planeRotatedLoop = euclidean.getPointsRoundZAxis( reverseRotation, surroundingLoop.boundary )
			rotatedCarve.append( planeRotatedLoop )
		surroundingCarves.append( rotatedCarve )

	def addThreadsBridgeLayer( self, rotatedLayer, surroundingLoops ):
		"Add the threads, add the bridge end & the layer end tag."
		euclidean.addToThreadsRemoveFromSurroundings( self.oldOrderedLocation, surroundingLoops, self )
		if rotatedLayer.rotation != None:
			self.distanceFeedRate.addLine('(</bridgeRotation>)')
		self.distanceFeedRate.addLine('(</layer>)')

	def addToThread(self, location):
		"Add a location to thread."
		if self.oldLocation == None:
			return
		if self.isPerimeter:
			self.surroundingLoop.addToLoop( location )
			return
		elif self.thread == None:
			self.thread = [ self.oldLocation.dropAxis(2) ]
			self.surroundingLoop.perimeterPaths.append( self.thread )
		self.thread.append( location.dropAxis(2) )

	def getAreaChange( self, area, layerIndex ):
		"Get the difference between the area of the carve at the layer index and the given area."
		layerArea = self.getCarveArea(layerIndex)
		return 1.0 - min( area, layerArea ) / max( area, layerArea )

	def getCraftedGcode( self, repository, gcodeText ):
		"Parse gcode text and store the bevel gcode."
		self.repository = repository
		self.lines = archive.getTextLines(gcodeText)
		self.threadSequence = None
		if repository.threadSequenceInfillLoops.value:
			self.threadSequence = ['infill', 'loops', 'perimeter']
		if repository.threadSequenceInfillPerimeter.value:
			self.threadSequence = ['infill', 'perimeter', 'loops']
		if repository.threadSequenceLoopsInfill.value:
			self.threadSequence = ['loops', 'infill', 'perimeter']
		if repository.threadSequenceLoopsPerimeter.value:
			self.threadSequence = ['loops', 'perimeter', 'infill']
		if repository.threadSequencePerimeterInfill.value:
			self.threadSequence = ['perimeter', 'infill', 'loops']
		if repository.threadSequencePerimeterLoops.value:
			self.threadSequence = ['perimeter', 'loops', 'infill']
		if self.repository.infillPerimeterOverlap.value > 0.45:
			print('')
			print('!!! WARNING !!!')
			print('"Infill Perimeter Overlap" is greater than 0.45, which may create problems with the infill, like threads going through empty space and/or the extruder switching on and off a lot.')
			print('If you want to stretch the infill a lot, set "Path Stretch over Perimeter Width" in stretch to a high value instead of setting "Infill Perimeter Overlap" to a high value.')
			print('')
		self.parseInitialization()
		if self.perimeterWidth == None:
			print('Warning, nothing will be done because self.perimeterWidth in getCraftedGcode in FillSkein was None.')
			return ''
		self.betweenWidth = self.perimeterWidth - 0.5 * self.infillWidth
		self.fillInset = self.infillWidth - self.infillWidth * self.repository.infillPerimeterOverlap.value
		if self.repository.infillInteriorDensityOverExteriorDensity.value > 0:
			self.interiorExtrusionWidth /= self.repository.infillInteriorDensityOverExteriorDensity.value
		self.infillSolidity = repository.infillSolidity.value
		if self.isGridToBeExtruded():
			self.setGridVariables(repository)
		self.infillBeginRotation = math.radians( repository.infillBeginRotation.value )
		self.infillOddLayerExtraRotation = math.radians( repository.infillOddLayerExtraRotation.value )
		self.solidSurfaceThickness = int( round( self.repository.solidSurfaceThickness.value ) )
		self.doubleSolidSurfaceThickness = self.solidSurfaceThickness + self.solidSurfaceThickness
		for lineIndex in xrange( self.lineIndex, len(self.lines) ):
			self.parseLine( lineIndex )
		for layerIndex in xrange(len(self.rotatedLayers)):
			self.addFill(layerIndex)
		self.distanceFeedRate.addLines( self.lines[ self.shutdownLineIndex : ] )
		return self.distanceFeedRate.output.getvalue()

	def getGridPoints(self, fillLoops, reverseRotation):
		"Get the grid points."
		if self.infillSolidity > 0.8:
			return []
		rotationBaseAngle = euclidean.getWiddershinsUnitPolar(self.infillBeginRotation)
		reverseRotationBaseAngle = complex(rotationBaseAngle.real, - rotationBaseAngle.imag)
		gridRotationAngle = reverseRotation * rotationBaseAngle
		slightlyGreaterThanFill = 1.01 * self.gridInset
		rotatedLoops = []
		for loop in trianglemesh.getLoopsInOrderOfArea(trianglemesh.compareAreaDescending, fillLoops):
			rotatedLoops.append(euclidean.getPointsRoundZAxis(reverseRotationBaseAngle, loop))
		if self.repository.infillPatternGridCircular.value:
			return self.getGridPointsByLoops(
				gridRotationAngle, intercircle.getInsetSeparateLoopsFromLoops(-self.gridCircleRadius, rotatedLoops))
		return self.getGridPointsByLoops(gridRotationAngle, intercircle.getInsetSeparateLoopsFromLoops(self.gridInset, rotatedLoops))

	def getGridPointsByLoops(self, gridRotationAngle, loops):
		"Get the grid points by loops."
		gridIntersectionsDictionary = {}
		gridPoints = []
		euclidean.addXIntersectionsFromLoopsForTable(loops, gridIntersectionsDictionary, self.gridRadius)
		for gridIntersectionsKey in gridIntersectionsDictionary:
			y = gridIntersectionsKey * self.gridRadius + self.gridRadius * 0.5
			gridIntersections = gridIntersectionsDictionary[gridIntersectionsKey]
			gridIntersections.sort()
			gridIntersectionsLength = len(gridIntersections)
			if gridIntersectionsLength % 2 == 1:
				gridIntersectionsLength -= 1
			for gridIntersectionIndex in xrange(0, gridIntersectionsLength, 2):
				begin = gridIntersections[gridIntersectionIndex]
				end = gridIntersections[gridIntersectionIndex + 1]
				offset = self.offsetMultiplier * (gridIntersectionsKey % 2) + self.offsetBaseX
				self.addGridLinePoints(begin, end, gridPoints, gridRotationAngle, offset, y)
		return gridPoints

	def getLayerRotation(self, layerIndex):
		"Get the layer rotation."
		rotation = self.rotatedLayers[ layerIndex ].rotation
		if rotation != None:
			return rotation
		infillBeginRotationRepeat = self.repository.infillBeginRotationRepeat.value
		infillOddLayerRotationMultiplier = float( layerIndex % ( infillBeginRotationRepeat + 1 ) == infillBeginRotationRepeat )
		layerAngle = self.infillBeginRotation + infillOddLayerRotationMultiplier * self.infillOddLayerExtraRotation
		return euclidean.getWiddershinsUnitPolar(layerAngle)

	def getNextGripXStep( self, gridXStep ):
		"Get the next grid x step, increment by an extra one every three if hexagonal grid is chosen."
		gridXStep += 1
		if self.repository.infillPatternGridHexagonal.value:
			if gridXStep % 3 == 0:
				gridXStep += 1
		return gridXStep

	def getCarveArea( self, layerIndex ):
		"Get the area of the carve."
		if layerIndex < 0 or layerIndex >= len( self.rotatedLayers ):
			return 0.0
		surroundingLoops = self.rotatedLayers[ layerIndex ].surroundingLoops
		area = 0.0
		for surroundingLoop in surroundingLoops:
			area += euclidean.getAreaLoop( surroundingLoop.boundary )
		return area

	def getIsDensitySolidityPositive(self):
		"Determine if the infillSolidity and infillInteriorDensityOverExteriorDensity are both positive."
		return self.repository.infillSolidity.value > 0.0 and self.repository.infillInteriorDensityOverExteriorDensity.value > 0.0

	def isGridToBeExtruded(self):
		"Determine if the grid is to be extruded."
		if self.repository.infillPatternLine.value:
			return False
		return self.getIsDensitySolidityPositive()

	def isPointInsideLineSegments( self, gridPoint ):
		"Is the point inside the line segments of the loops."
		if self.solidSurfaceThickness <= 0:
			return True
		fillLine = int( round( gridPoint.imag / self.layerExtrusionWidth - self.frontOverWidth ) )
		if fillLine >= len( self.horizontalSegmentLists ) or fillLine < 0:
			return False
		lineSegments = self.horizontalSegmentLists[ fillLine ]
		surroundingXIntersections = self.surroundingXIntersectionLists[ fillLine ]
		for lineSegment in lineSegments:
			if isSegmentCompletelyInAnIntersection( lineSegment, surroundingXIntersections ):
				xFirst = lineSegment[0].point.real
				xSecond = lineSegment[1].point.real
				if gridPoint.real > min( xFirst, xSecond ) and gridPoint.real < max( xFirst, xSecond ):
					return True
		return False

	def linearMove( self, splitLine ):
		"Add a linear move to the thread."
		location = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
		if self.extruderActive:
			self.addToThread( location )
		self.oldLocation = location

	def parseInitialization(self):
		'Parse gcode initialization and store the parameters.'
		for self.lineIndex in xrange(len(self.lines)):
			line = self.lines[self.lineIndex]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			self.distanceFeedRate.parseSplitLine(firstWord, splitLine)
			if firstWord == '(<perimeterWidth>':
				self.perimeterWidth = float(splitLine[1])
				threadSequenceString = ' '.join( self.threadSequence )
				self.distanceFeedRate.addTagBracketedLine('threadSequenceString', threadSequenceString )
			elif firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine('(<procedureDone> fill </procedureDone>)')
			elif firstWord == '(<crafting>)':
				self.distanceFeedRate.addLine(line)
				return
			elif firstWord == '(<bridgeWidthMultiplier>':
				self.bridgeWidthMultiplier = float(splitLine[1])
			elif firstWord == '(<layerThickness>':
				self.layerThickness = float(splitLine[1])
				self.infillWidth = self.repository.infillWidthOverThickness.value * self.layerThickness
				self.interiorExtrusionWidth = self.infillWidth
			self.distanceFeedRate.addLine(line)
 
	def parseLine( self, lineIndex ):
		"Parse a gcode line and add it to the fill skein."
		line = self.lines[lineIndex]
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
		if len(splitLine) < 1:
			return
		firstWord = splitLine[0]
		if firstWord == 'G1':
			self.linearMove(splitLine)
		elif firstWord == 'M101':
			self.extruderActive = True
		elif firstWord == 'M103':
			self.extruderActive = False
			self.thread = None
			self.isPerimeter = False
		elif firstWord == '(<boundaryPerimeter>)':
			self.surroundingLoop = euclidean.SurroundingLoop( self.threadSequence )
			self.rotatedLayer.surroundingLoops.append( self.surroundingLoop )
		elif firstWord == '(</boundaryPerimeter>)':
			self.surroundingLoop = None
		elif firstWord == '(<boundaryPoint>':
			location = gcodec.getLocationFromSplitLine(None, splitLine)
			self.surroundingLoop.addToBoundary( location )
		elif firstWord == '(<bridgeRotation>':
			secondWordWithoutBrackets = splitLine[1].replace('(', '').replace(')', '')
			self.rotatedLayer.rotation = complex( secondWordWithoutBrackets )
		elif firstWord == '(</crafting>)':
			self.shutdownLineIndex = lineIndex
		elif firstWord == '(<layer>':
			self.rotatedLayer = RotatedLayer(float(splitLine[1]))
			self.rotatedLayers.append( self.rotatedLayer )
			self.thread = None
		elif firstWord == '(<perimeter>':
			self.isPerimeter = True

	def setGridVariables( self, repository ):
		"Set the grid variables."
		self.gridInset = 1.2 * self.interiorExtrusionWidth
		self.gridRadius = self.interiorExtrusionWidth / self.infillSolidity
		self.gridXStepSize = 2.0 * self.gridRadius
 		self.offsetMultiplier = self.gridRadius
		if self.repository.infillPatternGridHexagonal.value:
			self.gridXStepSize = 4.0 / 3.0 * self.gridRadius
			self.offsetMultiplier = 1.5 * self.gridXStepSize
		if self.repository.infillPatternGridCircular.value:
			self.gridRadius += self.gridRadius
			self.gridXStepSize = self.gridRadius / math.sqrt(.75)
			self.offsetMultiplier = 0.5 * self.gridXStepSize
			circleInsetOverPerimeterWidth = repository.gridCircleSeparationOverPerimeterWidth.value + 0.5
			self.gridMinimumCircleRadius = self.perimeterWidth
			self.gridInset = self.gridMinimumCircleRadius
			self.gridCircleRadius = self.offsetMultiplier - circleInsetOverPerimeterWidth * self.perimeterWidth
			if self.gridCircleRadius < self.gridMinimumCircleRadius:
				print('')
				print('!!! WARNING !!!')
				print('Grid Circle Separation over Perimeter Width is too high, which makes the grid circles too small.')
				print('You should reduce Grid Circle Separation over Perimeter Width to a reasonable value, like the default of 0.5.')
				print('The grid circle radius will be set to the minimum grid circle radius.')
				print('')
				self.gridCircleRadius = self.gridMinimumCircleRadius
		self.offsetBaseX = 0.25 * self.gridXStepSize
		if self.repository.infillPatternGridRectangular.value:
			halfGridRadiusMinusInteriorExtrusionWidth = 0.5 * ( self.gridRadius - self.interiorExtrusionWidth )
			self.gridJunctionSeparationAtEnd = halfGridRadiusMinusInteriorExtrusionWidth * repository.gridJunctionSeparationOverOctogonRadiusAtEnd.value
			self.gridJunctionSeparationAtMiddle = halfGridRadiusMinusInteriorExtrusionWidth * repository.gridJunctionSeparationOverOctogonRadiusAtMiddle.value


class RotatedLayer:
	"A rotated layer."
	def __init__( self, z ):
		self.rotation = None
		self.surroundingLoops = []
		self.z = z

	def __repr__(self):
		"Get the string representation of this RotatedLayer."
		return '%s, %s, %s' % ( self.z, self.rotation, self.surroundingLoops )


class YIntersectionPath:
	"A class to hold the y intersection position, the loop which it intersected and the point index of the loop which it intersected."
	def __init__( self, pathIndex, pointIndex, y ):
		"Initialize from the path, point index, and y."
		self.pathIndex = pathIndex
		self.pointIndex = pointIndex
		self.y = y

	def __repr__(self):
		"Get the string representation of this y intersection."
		return '%s, %s, %s' % ( self.pathIndex, self.pointIndex, self.y )

	def getPath( self, paths ):
		"Get the path from the paths and path index."
		return paths[ self.pathIndex ]

	def getPointIndexPlusOne(self):
		"Get the point index plus one."
		return self.pointIndex + 1


def main():
	"Display the fill dialog."
	if len(sys.argv) > 1:
		writeOutput(' '.join(sys.argv[1 :]))
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
