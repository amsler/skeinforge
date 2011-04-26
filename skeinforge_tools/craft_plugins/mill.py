"""
This page is in the table of contents.
Mill is a script to mill the outlines.

The default 'Activate Mill' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.

If the 'Add Inner Loops' checkbox is on, inner milling loops will be added, the default is on.  If the 'Add Outer Loops' checkbox is on, outer milling loops will be added, the default is on.  If the 'Cross Hatch' checkbox is on, there will be alternating horizontal and vertical milling paths, if it is off there will only be horizontal milling paths, the default is on.

The 'Loop Inner Outset over Perimeter Width' times the perimeter width is the amount the inner milling loop will be outset, the default is 0.5.  The 'Loop Outer Outset over Perimeter Width' times the perimeter width is the amount the outer milling loop will be outset, the default is 1.0.  The 'Loop Outer Outset over Perimeter Width' ratio should be greater than the 'Loop Inner Outset over Perimeter Width' ratio.

The 'Mill Width over Perimeter Width' times the perimeter width is the width of the mill lines, the default is 1.0.  If the ratio is one, all the material will be milled.  The greater the 'Mill Width over Perimeter Width' the farther apart the mill lines will be and so less of the material will be directly milled, the remaining material might still be removed in chips if the ratio is not much greater than one.

The following examples mill the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and mill.py.


> python mill.py
This brings up the mill dialog.


> python mill.py Screw Holder Bottom.stl
The mill tool is parsing the file:
Screw Holder Bottom.stl
..
The mill tool has created the file:
Screw Holder Bottom_mill.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import mill
>>> mill.main()
This brings up the mill dialog.


>>> mill.writeOutput( 'Screw Holder Bottom.stl' )
Screw Holder Bottom.stl
The mill tool is parsing the file:
Screw Holder Bottom.stl
..
The mill tool has created the file:
Screw Holder Bottom_mill.gcode


"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools import profile
from skeinforge_tools.meta_plugins import polyfile
from skeinforge_tools.skeinforge_utilities import consecution
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import intercircle
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.skeinforge_utilities import settings
from skeinforge_tools.skeinforge_utilities import triangle_mesh
from skeinforge_tools.skeinforge_utilities.vector3 import Vector3
import math
import os
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getCraftedText( fileName, gcodeText = '', repository = None ):
	"Mill the file or gcodeText."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, gcodeText ), repository )

def getCraftedTextFromText( gcodeText, repository = None ):
	"Mill a gcode linear move gcodeText."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'mill' ):
		return gcodeText
	if repository == None:
		repository = settings.getReadRepository( MillRepository() )
	if not repository.activateMill.value:
		return gcodeText
	return MillSkein().getCraftedGcode( gcodeText, repository )

def getDiagonalFlippedLoops( loops ):
	"Get loops flipped over the dialogonal, in other words with the x and y swapped."
	diagonalFlippedLoops = []
	for loop in loops:
		diagonalFlippedLoop = []
		diagonalFlippedLoops.append( diagonalFlippedLoop )
		for point in loop:
			diagonalFlippedLoop.append( complex( point.imag, point.real ) )
	return diagonalFlippedLoops

def getNewRepository():
	"Get the repository constructor."
	return MillRepository()

def getPointsFromSegmentTable( segmentTable ):
	"Get the points from the segment table."
	points = []
	endpoints = euclidean.getEndpointsFromSegmentTable( segmentTable )
	for endpoint in endpoints:
		points.append( endpoint.point )
	return points

def isPointOfTableInLoop( loop, pointTable ):
	"Determine if a point in the point table is in the loop."
	for point in loop:
		if point in pointTable:
			return True
	return False

def writeOutput( fileName = '' ):
	"Mill a gcode linear move file."
	fileName = interpret.getFirstTranslatorFileNameUnmodified( fileName )
	if fileName == '':
		return
	consecution.writeChainTextWithNounMessage( fileName, 'mill' )


class Average:
	"A class to hold values and get the average."
	def __init__( self ):
		self.reset()

	def addValue( self, value ):
		"Add a value to the total and the number of values."
		self.numberOfValues += 1
		self.total += value

	def getAverage( self ):
		"Get the average."
		if self.numberOfValues == 0:
			print( 'should never happen, self.numberOfValues in Average is zero' )
			return 0.0
		return self.total / float( self.numberOfValues )

	def reset( self ):
		"Set the number of values and the total to the default."
		self.numberOfValues = 0
		self.total = 0.0


class MillRepository:
	"A class to handle the mill settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		profile.addListsToCraftTypeRepository( 'skeinforge_tools.craft_plugins.mill.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Mill', self, '' )
		self.activateMill = settings.BooleanSetting().getFromValue( 'Activate Mill', self, True )
		self.addInnerLoops = settings.BooleanSetting().getFromValue( 'Add Inner Loops', self, True )
		self.addOuterLoops = settings.BooleanSetting().getFromValue( 'Add Outer Loops', self, True )
		self.crossHatch = settings.BooleanSetting().getFromValue( 'Cross Hatch', self, True )
		self.loopInnerOutsetOverPerimeterWidth = settings.FloatSpin().getFromValue( 0.3, 'Loop Inner Outset over Perimeter Width (ratio):', self, 0.7, 0.5 )
		self.loopOuterOutsetOverPerimeterWidth = settings.FloatSpin().getFromValue( 0.8, 'Loop Outer Outset over Perimeter Width (ratio):', self, 1.4, 1.0 )
		self.millWidthOverPerimeterWidth = settings.FloatSpin().getFromValue( 0.8, 'Mill Width over Perimeter Width (ratio):', self, 1.8, 1.0 )
		self.executeTitle = 'Mill'

	def execute( self ):
		"Mill button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )



class MillSkein:
	"A class to mill a skein of extrusions."
	def __init__( self ):
		self.aroundPixelTable = {}
		self.average = Average()
		self.boundaryLayers = []
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.isExtruderActive = False
		self.layerIndex = 0
		self.lineIndex = 0
		self.lines = None
		self.oldLocation = None
		self.perimeterWidth = 0.6

	def addGcodeFromLoops( self, loops, z ):
		"Add gcode from loops."
		if self.oldLocation == None:
			self.oldLocation = Vector3()
		self.oldLocation.z = z
		for loop in loops:
			self.distanceFeedRate.addGcodeFromThreadZ( loop, z )
			euclidean.addToThreadsFromLoop( self.halfPerimeterWidth, 'loop', loop, self.oldLocation, self )

	def addGcodeFromThreadZ( self, thread, z ):
		"Add a thread to the output."
		self.distanceFeedRate.addGcodeFromThreadZ( thread, z )

	def addMillThreads( self ):
		"Add the mill htreads to the skein."
		boundaryLayer = self.boundaryLayers[ self.layerIndex ]
		endpoints = euclidean.getEndpointsFromSegmentTable( boundaryLayer.segmentTable )
		if len( endpoints ) < 1:
			return
		paths = euclidean.getPathsFromEndpoints( endpoints, self.millWidth, self.aroundPixelTable, self.aroundWidth )
		paths = euclidean.getConnectedPaths( paths, self.aroundPixelTable, self.aroundWidth ) # this is probably unnecesary
		averageZ = self.average.getAverage()
		if self.repository.addInnerLoops.value:
			self.addGcodeFromLoops( boundaryLayer.innerLoops, averageZ )
		if self.repository.addOuterLoops.value:
			self.addGcodeFromLoops( boundaryLayer.outerLoops, averageZ )
		for path in paths:
			simplifiedPath = euclidean.getSimplifiedPath( path, self.millWidth )
			self.distanceFeedRate.addGcodeFromThreadZ( simplifiedPath, averageZ )

	def addSegmentTableLoops( self, boundaryLayerIndex ):
		"Add the segment tables and loops to the boundary."
		boundaryLayer = self.boundaryLayers[ boundaryLayerIndex ]
		euclidean.subtractXIntersectionsTable( boundaryLayer.outerHorizontalTable, boundaryLayer.innerHorizontalTable )
		euclidean.subtractXIntersectionsTable( boundaryLayer.outerVerticalTable, boundaryLayer.innerVerticalTable )
		boundaryLayer.horizontalSegmentTable = self.getHorizontalSegmentTableForXIntersectionsTable( boundaryLayer.outerHorizontalTable )
		boundaryLayer.verticalSegmentTable = self.getVerticalSegmentTableForXIntersectionsTable( boundaryLayer.outerVerticalTable )
		innerHorizontalSegmentTable = self.getHorizontalSegmentTableForXIntersectionsTable( boundaryLayer.innerHorizontalTable )
		innerVerticalSegmentTable = self.getVerticalSegmentTableForXIntersectionsTable( boundaryLayer.innerVerticalTable )
		betweenPoints = getPointsFromSegmentTable( boundaryLayer.horizontalSegmentTable )
		betweenPoints += getPointsFromSegmentTable( boundaryLayer.verticalSegmentTable )
		innerPoints = getPointsFromSegmentTable( innerHorizontalSegmentTable )
		innerPoints += getPointsFromSegmentTable( innerVerticalSegmentTable )
		innerPointTable = {}
		for innerPoint in innerPoints:
			innerPointTable[ innerPoint ] = None
		boundaryLayer.innerLoops = []
		boundaryLayer.outerLoops = []
		millRadius = 0.75 * self.millWidth
		loops = triangle_mesh.getInclusiveLoops( betweenPoints, betweenPoints, millRadius )
		loops = euclidean.getSimplifiedLoops( loops, millRadius )
		for loop in loops:
			if isPointOfTableInLoop( loop, innerPointTable ):
				boundaryLayer.innerLoops.append( loop )
			else:
				boundaryLayer.outerLoops.append( loop )
		if self.repository.crossHatch.value and boundaryLayerIndex % 2 == 1:
			boundaryLayer.segmentTable = boundaryLayer.verticalSegmentTable
		else:
			boundaryLayer.segmentTable = boundaryLayer.horizontalSegmentTable

	def getCraftedGcode( self, gcodeText, repository ):
		"Parse gcode text and store the mill gcode."
		self.repository = repository
		self.lines = gcodec.getTextLines( gcodeText )
		self.parseInitialization()
		self.parseBoundaries()
		for line in self.lines[ self.lineIndex : ]:
			self.parseLine( line )
		return self.distanceFeedRate.output.getvalue()

	def getHorizontalSegmentTableForXIntersectionsTable( self, xIntersectionsTable ):
		"Get the horizontal segment table from the xIntersectionsTable."
		horizontalSegmentTable = {}
		xIntersectionsTableKeys = xIntersectionsTable.keys()
		xIntersectionsTableKeys.sort()
		for xIntersectionsTableKey in xIntersectionsTableKeys:
			xIntersections = xIntersectionsTable[ xIntersectionsTableKey ]
			segments = euclidean.getSegmentsFromXIntersections( xIntersections, xIntersectionsTableKey * self.millWidth )
			horizontalSegmentTable[ xIntersectionsTableKey ] = segments
		return horizontalSegmentTable

	def getHorizontalXIntersectionsTable( self, loops ):
		"Get the horizontal x intersections table from the loops."
		horizontalXIntersectionsTable = {}
		euclidean.addXIntersectionsFromLoopsForTable( loops, horizontalXIntersectionsTable, self.millWidth )
		return horizontalXIntersectionsTable

	def getVerticalSegmentTableForXIntersectionsTable( self, xIntersectionsTable ):
		"Get the vertical segment table from the xIntersectionsTable which has the x and y swapped."
		verticalSegmentTable = {}
		xIntersectionsTableKeys = xIntersectionsTable.keys()
		xIntersectionsTableKeys.sort()
		for xIntersectionsTableKey in xIntersectionsTableKeys:
			xIntersections = xIntersectionsTable[ xIntersectionsTableKey ]
			segments = euclidean.getSegmentsFromXIntersections( xIntersections, xIntersectionsTableKey * self.millWidth )
			for segment in segments:
				for endpoint in segment:
					endpoint.point = complex( endpoint.point.imag, endpoint.point.real )
			verticalSegmentTable[ xIntersectionsTableKey ] = segments
		return verticalSegmentTable

	def parseBoundaries( self ):
		"Parse the boundaries and add them to the boundary layers."
		boundaryLoop = None
		boundaryLayer = None
		for line in self.lines[ self.lineIndex : ]:
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			if firstWord == '(</boundaryPerimeter>)':
				boundaryLoop = None
			elif firstWord == '(<boundaryPoint>':
				location = gcodec.getLocationFromSplitLine( None, splitLine )
				if boundaryLoop == None:
					boundaryLoop = []
					boundaryLayer.loops.append( boundaryLoop )
				boundaryLoop.append( location.dropAxis( 2 ) )
			elif firstWord == '(<layer>':
				boundaryLayer = euclidean.LoopLayer( float( splitLine[ 1 ] ) )
				self.boundaryLayers.append( boundaryLayer )
		if len( self.boundaryLayers ) < 2:
			return
		for boundaryLayer in self.boundaryLayers:
			boundaryLayer.innerOutsetLoops = intercircle.getInsetSeparateLoopsFromLoops( - self.loopInnerOutset, boundaryLayer.loops )
			boundaryLayer.outerOutsetLoops = intercircle.getInsetSeparateLoopsFromLoops( - self.loopOuterOutset, boundaryLayer.loops )
			boundaryLayer.innerHorizontalTable = self.getHorizontalXIntersectionsTable( boundaryLayer.innerOutsetLoops )
			boundaryLayer.outerHorizontalTable = self.getHorizontalXIntersectionsTable( boundaryLayer.outerOutsetLoops )
			boundaryLayer.innerVerticalTable = self.getHorizontalXIntersectionsTable( getDiagonalFlippedLoops( boundaryLayer.innerOutsetLoops ) )
			boundaryLayer.outerVerticalTable = self.getHorizontalXIntersectionsTable( getDiagonalFlippedLoops( boundaryLayer.outerOutsetLoops ) )
		for boundaryLayerIndex in xrange( len( self.boundaryLayers ) - 2, - 1, - 1 ):
			boundaryLayer = self.boundaryLayers[ boundaryLayerIndex ]
			boundaryLayerBelow = self.boundaryLayers[ boundaryLayerIndex + 1 ]
			euclidean.joinXIntersectionsTables( boundaryLayerBelow.outerHorizontalTable, boundaryLayer.outerHorizontalTable )
			euclidean.joinXIntersectionsTables( boundaryLayerBelow.outerVerticalTable, boundaryLayer.outerVerticalTable )
		for boundaryLayerIndex in xrange( 1, len( self.boundaryLayers ) ):
			boundaryLayer = self.boundaryLayers[ boundaryLayerIndex ]
			boundaryLayerAbove = self.boundaryLayers[ boundaryLayerIndex - 1 ]
			euclidean.joinXIntersectionsTables( boundaryLayerAbove.innerHorizontalTable, boundaryLayer.innerHorizontalTable )
			euclidean.joinXIntersectionsTables( boundaryLayerAbove.innerVerticalTable, boundaryLayer.innerVerticalTable )
		for boundaryLayerIndex in xrange( len( self.boundaryLayers ) ):
			self.addSegmentTableLoops( boundaryLayerIndex )

	def parseInitialization( self ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine( '(<procedureDone> mill </procedureDone>)' )
				return
			elif firstWord == '(<perimeterWidth>':
				self.perimeterWidth = float( splitLine[ 1 ] )
				self.aroundWidth = 0.1 * self.perimeterWidth
				self.halfPerimeterWidth = 0.5 * self.perimeterWidth
				self.millWidth = self.perimeterWidth * self.repository.millWidthOverPerimeterWidth.value
				self.loopInnerOutset = self.halfPerimeterWidth + self.perimeterWidth * self.repository.loopInnerOutsetOverPerimeterWidth.value
				self.loopOuterOutset = self.halfPerimeterWidth + self.perimeterWidth * self.repository.loopOuterOutsetOverPerimeterWidth.value
			self.distanceFeedRate.addLine( line )

	def parseLine( self, line ):
		"Parse a gcode line and add it to the mill skein."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == 'G1':
			location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
			if self.isExtruderActive:
				self.average.addValue( location.z )
				if self.oldLocation != None:
					euclidean.addValueSegmentToPixelTable( self.oldLocation.dropAxis( 2 ), location.dropAxis( 2 ), self.aroundPixelTable, None, self.aroundWidth )
			self.oldLocation = location
		elif firstWord == 'M101':
			self.isExtruderActive = True
		elif firstWord == 'M103':
			self.isExtruderActive = False
		elif firstWord == '(<layer>':
			self.aroundPixelTable = {}
			self.average.reset()
		elif firstWord == '(</layer>)':
			if len( self.boundaryLayers ) > self.layerIndex:
				self.addMillThreads()
			self.layerIndex += 1
		self.distanceFeedRate.addLine( line )


def main():
	"Display the mill dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
