"""
Speed is a script to set the feed rate, and flow rate.

The default 'Activate Speed' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.  The speed script sets the feed rate, and flow rate.

The feed rate for the shape will be set to the 'Feed Rate" preference.  The 'Bridge Feed Rate Multiplier' is the ratio of the feed rate on the bridge layers over the feed rate of the typical non bridge layers, the default is 1.0.  The speed of the orbit compared to the operating extruder speed will be set to the "Orbital Feed Rate over Operating Feed Rate" preference.  If you want the orbit to be very short, set the "Orbital Feed Rate over Operating Feed Rate" preference to a low value like 0.1.  The 'Travel Feed Rate' is the feed rate when the extruder is off.  The default is 16 mm / s and it could be set as high as the extruder can be moved, it does not have to be limited by the maximum extrusion rate.

The default 'Add Flow Rate' checkbox is on.  When it is on, the flow rate will be added to the gcode.  The 'Bridge Flow Rate Multiplier' is the ratio of the flow rate on the bridge layers over the flow rate of the typical non bridge layers, the default is 1.0.  The 'Flow Rate Setting' sets the operating flow rate, the default is 210.

The 'Maximum Z Feed Rate' is the maximum speed that the tool head will move in the z direction.  If your firmware limits the z feed rate, you do not need to set this preference.  The default of 8 millimeters per second is the maximum z speed of Nophead's direct drive z stage, the belt driven z stages have a lower maximum feed rate.

The 'Perimeter Feed Rate over Operating Feed Rate' is the ratio of the feed rate of the perimeter over the feed rate of the infill.  With the default of 1.0, the perimeter feed rate will be the same as the infill feed rate.  The 'Perimeter Flow Rate over Operating Flow Rate' is the ratio of the flow rate of the perimeter over the flow rate of the infill.  With the default of 1.0, the perimeter flow rate will be the same as the infill flow rate.  To have higher build quality on the outside at the expense of slower build speed, a typical setting for the 'Perimeter Feed Rate over Operating Feed Rate' would be 0.5.  To go along with that, if you are using a speed controlled extruder, the 'Perimeter Flow Rate over Operating Flow Rate' should also be 0.5.  If you are using Pulse Width Modulation to control the speed, then you'll probably need a slightly higher ratio because there is a minimum voltage 'Flow Rate PWM Setting' required for the extruder motor to turn.  The flow rate PWM ratio would be determined by trial and error, with the first trial being:
Perimeter Flow Rate over Operating Flow Rate ~ Perimeter Feed Rate over Operating Feed Rate * ( Flow Rate PWM Setting - Minimum Flow Rate PWM Setting ) + Minimum Flow Rate PWM Setting

The following examples speed the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and speed.py.


> python speed.py
This brings up the speed dialog.


> python speed.py Screw Holder Bottom.stl
The speed tool is parsing the file:
Screw Holder Bottom.stl
..
The speed tool has created the file:
.. Screw Holder Bottom_speed.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import speed
>>> speed.main()
This brings up the speed dialog.


>>> speed.writeOutput( 'Screw Holder Bottom.stl' )
The speed tool is parsing the file:
Screw Holder Bottom.stl
..
The speed tool has created the file:
.. Screw Holder Bottom_speed.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import consecution
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import intercircle
from skeinforge_tools.skeinforge_utilities import preferences
from skeinforge_tools import analyze
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.meta_plugins import polyfile
import math
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getCraftedText( fileName, text = '', speedRepository = None ):
	"Speed the file or text."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, text ), speedRepository )

def getCraftedTextFromText( gcodeText, speedRepository = None ):
	"Speed a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'speed' ):
		return gcodeText
	if speedRepository == None:
		speedRepository = preferences.getReadRepository( SpeedRepository() )
	if not speedRepository.activateSpeed.value:
		return gcodeText
	return SpeedSkein().getCraftedGcode( gcodeText, speedRepository )

def getNewRepository():
	"Get the repository constructor."
	return SpeedRepository()

def writeOutput( fileName = '' ):
	"Speed a gcode linear move file."
	fileName = interpret.getFirstTranslatorFileNameUnmodified( fileName )
	if fileName != '':
		consecution.writeChainTextWithNounMessage( fileName, 'speed' )


class SpeedRepository:
	"A class to handle the speed preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		preferences.addListsToCraftTypeRepository( 'skeinforge_tools.craft_plugins.speed.html', self )
		self.fileNameInput = preferences.FileNameInput().getFromFileName( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Speed', self, '' )
		self.activateSpeed = preferences.BooleanPreference().getFromValue( 'Activate Speed:', self, True )
		self.addFlowRate = preferences.BooleanPreference().getFromValue( 'Add Flow Rate:', self, True )
		self.bridgeFeedRateMultiplier = preferences.FloatSpin().getFromValue( 0.8, 'Bridge Feed Rate Multiplier (ratio):', self, 1.2, 1.0 )
		self.bridgeFlowRateMultiplier = preferences.FloatSpin().getFromValue( 0.8, 'Bridge Flow Rate Multiplier (ratio):', self, 1.2, 1.0 )
		self.feedRatePerSecond = preferences.FloatSpin().getFromValue( 2.0, 'Feed Rate (mm/s):', self, 50.0, 16.0 )
		self.flowRateSetting = preferences.FloatSpin().getFromValue( 50.0, 'Flow Rate Setting (float):', self, 250.0, 210.0 )
		self.maximumZFeedRatePerSecond = preferences.FloatSpin().getFromValue( 0.5, 'Maximum Z Feed Rate (mm/s):', self, 10.0, 8.0 )
		self.orbitalFeedRateOverOperatingFeedRate = preferences.FloatSpin().getFromValue( 0.1, 'Orbital Feed Rate over Operating Feed Rate (ratio):', self, 0.9, 0.5 )
		self.perimeterFeedRateOverOperatingFeedRate = preferences.FloatSpin().getFromValue( 0.5, 'Perimeter Feed Rate over Operating Feed Rate (ratio):', self, 1.0, 1.0 )
		self.perimeterFlowRateOverOperatingFlowRate = preferences.FloatSpin().getFromValue( 0.5, 'Perimeter Flow Rate over Operating Flow Rate (ratio):', self, 1.0, 1.0 )
		self.travelFeedRatePerSecond = preferences.FloatSpin().getFromValue( 2.0, 'Travel Feed Rate (mm/s):', self, 50.0, 16.0 )
		self.executeTitle = 'Speed'

	def execute( self ):
		"Speed button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


class SpeedSkein:
	"A class to speed a skein of extrusions."
	def __init__( self ):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.feedRatePerSecond = 16.0
		self.isExtruderActive = False
		self.isBridgeLayer = False
		self.isSurroundingLoopBeginning = False
		self.lineIndex = 0
		self.lines = None
		self.oldFlowRateString = None
		self.oldLocation = None

	def addFlowRateLineIfNecessary( self ):
		"Add flow rate line."
		flowRateString = self.getFlowRateString()
		if flowRateString != self.oldFlowRateString:
			self.distanceFeedRate.addLine( 'M108 S' + flowRateString )
		self.oldFlowRateString = flowRateString

	def getCraftedGcode( self, gcodeText, speedRepository ):
		"Parse gcode text and store the speed gcode."
		self.distanceFeedRate.maximumZDrillFeedRatePerSecond = speedRepository.maximumZFeedRatePerSecond.value
		self.distanceFeedRate.maximumZTravelFeedRatePerSecond = speedRepository.maximumZFeedRatePerSecond.value
		self.speedRepository = speedRepository
		self.feedRatePerSecond = speedRepository.feedRatePerSecond.value
		self.travelFeedRatePerMinute = 60.0 * self.speedRepository.travelFeedRatePerSecond.value
		self.lines = gcodec.getTextLines( gcodeText )
		self.parseInitialization()
		for line in self.lines[ self.lineIndex : ]:
			self.parseLine( line )
		return self.distanceFeedRate.output.getvalue()

	def getFlowRateString( self ):
		"Get the flow rate string."
		if not self.speedRepository.addFlowRate.value:
			return None
		flowRate = self.speedRepository.flowRateSetting.value
		if self.isBridgeLayer:
			flowRate *= self.speedRepository.bridgeFlowRateMultiplier.value
		if self.isSurroundingLoopBeginning:
			flowRate *= self.speedRepository.perimeterFlowRateOverOperatingFlowRate.value
		return euclidean.getFourSignificantFigures( flowRate )

	def getSpeededLine( self, splitLine ):
		"Get gcode line with feed rate."
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		self.oldLocation = location
		feedRateMinute = 60.0 * self.feedRatePerSecond
		if self.isBridgeLayer:
			feedRateMinute *= self.speedRepository.bridgeFeedRateMultiplier.value
		if self.isSurroundingLoopBeginning:
			feedRateMinute *= self.speedRepository.perimeterFeedRateOverOperatingFeedRate.value
		self.addFlowRateLineIfNecessary()
		if not self.isExtruderActive:
			feedRateMinute = self.travelFeedRatePerMinute
		return self.distanceFeedRate.getLinearGcodeMovementWithFeedRate( feedRateMinute, location.dropAxis( 2 ), location.z )

	def parseInitialization( self ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(<layerThickness>':
				self.layerThickness = float( splitLine[ 1 ] )
			elif firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine( '(<procedureDone> speed </procedureDone>)' )
				return
			elif firstWord == '(<perimeterWidth>':
				self.absolutePerimeterWidth = abs( float( splitLine[ 1 ] ) )
				self.distanceFeedRate.addTagBracketedLine( 'maximumZDrillFeedRatePerSecond', self.distanceFeedRate.maximumZDrillFeedRatePerSecond )
				self.distanceFeedRate.addTagBracketedLine( 'maximumZTravelFeedRatePerSecond', self.distanceFeedRate.maximumZTravelFeedRatePerSecond )
				self.distanceFeedRate.addTagBracketedLine( 'operatingFeedRatePerSecond', self.feedRatePerSecond )
				orbitalFeedRatePerSecond = self.feedRatePerSecond * self.speedRepository.orbitalFeedRateOverOperatingFeedRate.value
				self.distanceFeedRate.addTagBracketedLine( 'orbitalFeedRatePerSecond', orbitalFeedRatePerSecond )
				self.distanceFeedRate.addTagBracketedLine( 'travelFeedRatePerSecond', self.speedRepository.travelFeedRatePerSecond.value )
			self.distanceFeedRate.addLine( line )

	def parseLine( self, line ):
		"Parse a gcode line and add it to the speed skein."
		if not self.distanceFeedRate.absoluteDistanceMode:
			self.distanceFeedRate.addLine( line )
			return
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == 'G1':
			line = self.getSpeededLine( splitLine )
		elif firstWord == 'M101':
			self.isExtruderActive = True
		elif firstWord == 'M103':
			self.isSurroundingLoopBeginning = False
			self.isExtruderActive = False
		elif firstWord == '(<bridgeRotation>':
			self.isBridgeLayer = True
		elif firstWord == '(<layer>':
			self.isBridgeLayer = False
			self.addFlowRateLineIfNecessary()
		elif firstWord == '(<surroundingLoop>)':
			self.isSurroundingLoopBeginning = True
		self.distanceFeedRate.addLine( line )


def main():
	"Display the speed dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		preferences.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
