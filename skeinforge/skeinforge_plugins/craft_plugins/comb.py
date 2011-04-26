"""
This page is in the table of contents.
Comb is a script to comb the extrusion hair of a gcode file.

The comb manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Comb

Comb bends the extruder travel paths around holes in the slices, to avoid stringers.  It moves the extruder to the inside of perimeters before turning the extruder on so any start up ooze will be inside the shape.

==Operation==
The default 'Activate Comb' checkbox is off.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Minimum Departure Distance over Perimeter Width===
Default is zero.

Defines the ratio of the minimum distance that the extruder will travel and loop before leaving a perimeter.  A high value means the extruder will loop many times before leaving, so that the ooze will finish within the perimeter, a low value means the extruder will not loop and the stringers will be thicker.  Since it sometimes loops when there's no need, the default is zero.

==Examples==

The following examples comb the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and comb.py.


> python comb.py
This brings up the comb dialog.


> python comb.py Screw Holder Bottom.stl
The comb tool is parsing the file:
Screw Holder Bottom.stl
..
The comb tool has created the file:
.. Screw Holder Bottom_comb.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import comb
>>> comb.main()
This brings up the comb dialog.


>>> comb.writeOutput( 'Screw Holder Bottom.stl' )
The comb tool is parsing the file:
Screw Holder Bottom.stl
..
The comb tool has created the file:
.. Screw Holder Bottom_comb.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import intercircle
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities import settings
from skeinforge.skeinforge_utilities import skeinforge_craft
from skeinforge.skeinforge_utilities import skeinforge_polyfile
from skeinforge.skeinforge_utilities import skeinforge_profile
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


#maybe remove getBetweenAdded because widdershins loops have been removed
def getCraftedText( fileName, text, combRepository = None ):
	"Comb a gcode linear move text."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, text ), combRepository )

def getCraftedTextFromText( gcodeText, combRepository = None ):
	"Comb a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'comb' ):
		return gcodeText
	if combRepository == None:
		combRepository = settings.getReadRepository( CombRepository() )
	if not combRepository.activateComb.value:
		return gcodeText
	return CombSkein().getCraftedGcode( combRepository, gcodeText )

def getNewRepository():
	"Get the repository constructor."
	return CombRepository()

def writeOutput( fileName = '' ):
	"Comb a gcode linear move file."
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified( fileName )
	if fileName != '':
		skeinforge_craft.writeChainTextWithNounMessage( fileName, 'comb' )


class CombRepository:
	"A class to handle the comb settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository( 'skeinforge.skeinforge_plugins.craft_plugins.comb.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Comb', self, '' )
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute( 'http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Comb' )
		self.activateComb = settings.BooleanSetting().getFromValue( 'Activate Comb', self, False )
		self.minimumDepartureDistanceOverPerimeterWidth = settings.FloatSpin().getFromValue( 0.0, 'Minimum Departure Distance over Perimeter Width (ratio):', self, 50.0, 0.0 )
		self.executeTitle = 'Comb'

	def execute( self ):
		"Comb button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


class CombSkein:
	"A class to comb a skein of extrusions."
	def __init__( self ):
		self.betweenTable = {}
		self.boundaryLoop = None
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.extruderActive = False
		self.layer = None
		self.layerTable = {}
		self.layerZ = None
		self.lineIndex = 0
		self.lines = None
		self.nextLayerZ = None
		self.oldLocation = None
		self.oldZ = None
		self.operatingFeedRatePerMinute = None
		self.travelFeedRatePerMinute = None

	def addGcodePathZ( self, feedRateMinute, path, z ):
		"Add a gcode path, without modifying the extruder, to the output."
		for point in path:
			self.distanceFeedRate.addGcodeMovementZWithFeedRate( feedRateMinute, point, z )

	def addIfTravel( self, splitLine ):
		"Add travel move around loops if the extruder is off."
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		if not self.extruderActive and self.oldLocation != None:
			if len( self.getBoundaries() ) > 0:
				highestZ = max( location.z, self.oldLocation.z )
				self.addGcodePathZ( self.travelFeedRatePerMinute, self.getPathsBetween( self.oldLocation.dropAxis( 2 ), location.dropAxis( 2 ) ), highestZ )
		self.oldLocation = location

	def addToLoop( self, location ):
		"Add a location to loop."
		if self.layer == None:
			if not self.oldZ in self.layerTable:
				self.layerTable[ self.oldZ ] = []
			self.layer = self.layerTable[ self.oldZ ]
		if self.boundaryLoop == None:
			self.boundaryLoop = [] #starting with an empty array because a closed loop does not have to restate its beginning
			self.layer.append( self.boundaryLoop )
		if self.boundaryLoop != None:
			self.boundaryLoop.append( location.dropAxis( 2 ) )

	def getBetweens( self ):
		"Set betweens for the layer."
		if self.layerZ in self.betweenTable:
			return self.betweenTable[ self.layerZ ]
		if self.layerZ not in self.layerTable:
			return []
		self.betweenTable[ self.layerZ ] = []
		for boundaryLoop in self.layerTable[ self.layerZ ]:
			self.betweenTable[ self.layerZ ] += intercircle.getInsetLoopsFromLoop( self.betweenInset, boundaryLoop )
		return self.betweenTable[ self.layerZ ]

	def getBoundaries( self ):
		"Get boundaries for the layer."
		if self.layerZ in self.layerTable:
			return self.layerTable[ self.layerZ ]
		return []

	def getCraftedGcode( self, combRepository, gcodeText ):
		"Parse gcode text and store the comb gcode."
		self.combRepository = combRepository
		self.lines = gcodec.getTextLines( gcodeText )
		self.parseInitialization( combRepository )
		for lineIndex in xrange( self.lineIndex, len( self.lines ) ):
			line = self.lines[ lineIndex ]
			self.parseBoundariesLayers( combRepository, line )
		for layerTableKey in self.layerTable.keys():
			self.layerTable[ layerTableKey ] = intercircle.getLoopsFromLoopsDirection( False, self.layerTable[ layerTableKey ] )
		for lineIndex in xrange( self.lineIndex, len( self.lines ) ):
			line = self.lines[ lineIndex ]
			self.parseLine( line )
		return self.distanceFeedRate.output.getvalue()

	def getIsAsFarAndNotIntersecting( self, begin, end ):
		"Determine if the point on the line is at least as far from the loop as the center point."
		if begin == end:
			print( 'this should never happen but it does not really matter, begin == end in getIsAsFarAndNotIntersecting in comb.' )
			print( begin )
			return True
		return not euclidean.isLineIntersectingLoops( self.getBetweens(), begin, end )

	def getIsRunningJumpPathAdded( self, betweens, end, lastPoint, nearestEndMinusLastSegment, pathAround, penultimatePoint, runningJumpSpace ):
		"Add a running jump path if possible, and return if it was added."
		jumpStartPoint = lastPoint - nearestEndMinusLastSegment * runningJumpSpace
		if euclidean.isLineIntersectingLoops( betweens, penultimatePoint, jumpStartPoint ):
			return False
		pathAround[ - 1 ] = jumpStartPoint
		return True

	def getPathBetween( self, betweenFirst, betweenSecond, isLeavingPerimeter, loopFirst ):
		"Add a path between the perimeter and the fill."
		loopFirst = intercircle.getLargestInsetLoopFromLoopNoMatterWhat( loopFirst, self.combInset )
		nearestFirstDistanceIndex = euclidean.getNearestDistanceIndex( betweenFirst, loopFirst )
		nearestSecondDistanceIndex = euclidean.getNearestDistanceIndex( betweenSecond, loopFirst )
		firstBeginIndex = ( nearestFirstDistanceIndex.index + 1 ) % len( loopFirst )
		secondBeginIndex = ( nearestSecondDistanceIndex.index + 1 ) % len( loopFirst )
		nearestFirst = euclidean.getNearestPointOnSegment( loopFirst[ nearestFirstDistanceIndex.index ], loopFirst[ firstBeginIndex ], betweenFirst )
		nearestSecond = euclidean.getNearestPointOnSegment( loopFirst[ nearestSecondDistanceIndex.index ], loopFirst[ secondBeginIndex ], betweenSecond )
		clockwisePath = [ nearestFirst ]
		widdershinsPath = [ nearestFirst ]
		loopBeforeLeaving = euclidean.getAroundLoop( firstBeginIndex, firstBeginIndex, loopFirst )
		if nearestFirstDistanceIndex.index == nearestSecondDistanceIndex.index:
			if euclidean.getPathLength( widdershinsPath ) < self.minimumDepartureDistance:
				widdershinsPath = [ nearestFirst ] + loopBeforeLeaving
				reversedLoop = loopBeforeLeaving[ : ]
				reversedLoop.reverse()
				clockwisePath = [ nearestFirst ] + reversedLoop
		else:
			widdershinsLoop = euclidean.getAroundLoop( firstBeginIndex, secondBeginIndex, loopFirst )
			widdershinsPath += widdershinsLoop
			clockwiseLoop = euclidean.getAroundLoop( secondBeginIndex, firstBeginIndex, loopFirst )
			clockwiseLoop.reverse()
			clockwisePath += clockwiseLoop
		clockwisePath.append( nearestSecond )
		widdershinsPath.append( nearestSecond )
		if euclidean.getPathLength( widdershinsPath ) > euclidean.getPathLength( clockwisePath ):
			loopBeforeLeaving.reverse()
			widdershinsPath = clockwisePath
		if isLeavingPerimeter:
			totalDistance = euclidean.getPathLength( widdershinsPath )
			loopLength = euclidean.getPolygonLength( loopBeforeLeaving )
			while totalDistance < self.minimumDepartureDistance:
				widdershinsPath = [ nearestFirst ] + loopBeforeLeaving + widdershinsPath[ 1 : ]
				totalDistance += loopLength
		return widdershinsPath

	def getPathsBetween( self, begin, end ):
		"Insert paths between the perimeter and the fill."
		aroundBetweenPath = []
		points = [ begin ]
		lineX = []
		switchX = []
		segment = euclidean.getNormalized( end - begin )
		segmentYMirror = complex( segment.real, - segment.imag )
		beginRotated = segmentYMirror * begin
		endRotated = segmentYMirror * end
		y = beginRotated.imag
		boundaries = self.getBoundaries()
		for boundaryIndex in xrange( len( boundaries ) ):
			boundary = boundaries[ boundaryIndex ]
			boundaryRotated = euclidean.getPointsRoundZAxis( segmentYMirror, boundary )
			euclidean.addXIntersectionIndexesFromLoopY( boundaryRotated, boundaryIndex, switchX, y )
		switchX.sort()
		maximumX = max( beginRotated.real, endRotated.real )
		minimumX = min( beginRotated.real, endRotated.real )
		for xIntersection in switchX:
			if xIntersection.x > minimumX and xIntersection.x < maximumX:
				point = segment * complex( xIntersection.x, y )
				points.append( point )
				lineX.append( xIntersection )
		points.append( end )
		lineXIndex = 0
		pathBetweenAdded = False
		while lineXIndex < len( lineX ) - 1:
			lineXFirst = lineX[ lineXIndex ]
			lineXSecond = lineX[ lineXIndex + 1 ]
			loopFirst = boundaries[ lineXFirst.index ]
			isLeavingPerimeter = False
			if lineXSecond.index != lineXFirst.index:
				isLeavingPerimeter = True
			pathBetween = self.getPathBetween( points[ lineXIndex + 1 ], points[ lineXIndex + 2 ], isLeavingPerimeter, loopFirst )
			if isLeavingPerimeter:
				pathBetweenAdded = True
			else:
				pathBetween = self.getSimplifiedAroundPath( points[ lineXIndex ], points[ lineXIndex + 3 ], loopFirst, pathBetween )
				pathBetweenAdded = True
			aroundBetweenPath += pathBetween
			lineXIndex += 2
		return aroundBetweenPath

	def getSimplifiedAroundPath( self, begin, end, loop, pathAround ):
		"Get the simplified path between the perimeter and the fill."
		pathAround = self.getSimplifiedBeginPath( begin, loop, pathAround )
		return self.getSimplifiedEndPath( end, loop, pathAround )

	def getSimplifiedBeginPath( self, begin, loop, pathAround ):
		"Get the simplified begin path between the perimeter and the fill."
		if len( pathAround ) < 2:
			return pathAround
		pathIndex = 0
		while pathIndex < len( pathAround ) - 1:
			if not self.getIsAsFarAndNotIntersecting( begin, pathAround[ pathIndex + 1 ] ):
				return pathAround[ pathIndex : ]
			pathIndex += 1
		return pathAround[ - 1 : ]

	def getSimplifiedEndPath( self, end, loop, pathAround ):
		"Get the simplified end path between the perimeter and the fill."
		if len( pathAround ) < 2:
			return pathAround
		pathIndex = len( pathAround ) - 1
		while pathIndex > 0:
			if not self.getIsAsFarAndNotIntersecting( end, pathAround[ pathIndex - 1 ] ):
				return pathAround[ : pathIndex + 1 ]
			pathIndex -= 1
		return pathAround[ : 1 ]

	def parseBoundariesLayers( self, combRepository, line ):
		"Parse a gcode line."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == 'M103':
			self.boundaryLoop = None
		elif firstWord == '(<boundaryPoint>':
			location = gcodec.getLocationFromSplitLine( None, splitLine )
			self.addToLoop( location )
		elif firstWord == '(<layer>':
			self.boundaryLoop = None
			self.layer = None
			self.oldZ = float( splitLine[ 1 ] )

	def parseInitialization( self, combRepository ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine( '(<procedureDone> comb </procedureDone>)' )
				return
			elif firstWord == '(<perimeterWidth>':
				perimeterWidth = float( splitLine[ 1 ] )
				self.combInset = 1.2 * perimeterWidth
				self.betweenInset = 0.4 * perimeterWidth
				self.uTurnWidth = 0.5 * self.betweenInset
				self.minimumDepartureDistance = combRepository.minimumDepartureDistanceOverPerimeterWidth.value * perimeterWidth
			elif firstWord == '(<travelFeedRatePerSecond>':
				self.travelFeedRatePerMinute = 60.0 * float( splitLine[ 1 ] )
			self.distanceFeedRate.addLine( line )

	def parseLine( self, line ):
		"Parse a gcode line and add it to the comb skein."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == 'G1':
			self.addIfTravel( splitLine )
			self.layerZ = self.nextLayerZ
		elif firstWord == 'M101':
			self.extruderActive = True
		elif firstWord == 'M103':
			self.extruderActive = False
		elif firstWord == '(<layer>':
			self.nextLayerZ = float( splitLine[ 1 ] )
			if self.layerZ == None:
				self.layerZ = self.nextLayerZ
		self.distanceFeedRate.addLine( line )


def main():
	"Display the comb dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
