"""
This page is in the table of contents.
Hop is a script to raise the extruder when it is not extruding.

The default 'Activate Hop' checkbox is off.  It is off because Vik and Nophead found better results without hopping.  When it is on, the functions described below will work, when it is off, the functions will not be called.

The important value for the hop settings is "Hop Over Layer Thickness (ratio)" which is the ratio of the hop height over the layer thickness, the default is 1.0.  The 'Minimum Hop Angle (degrees)' is the minimum angle that the path of the extruder will be raised.  An angle of ninety means that the extruder will go straight up as soon as it is not extruding and a low angle means the extruder path will gradually rise to the hop height, the default is 20 degrees.

The following examples hop the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and hop.py.


> python hop.py
This brings up the hop dialog.


> python hop.py Screw Holder Bottom.stl
The hop tool is parsing the file:
Screw Holder Bottom.stl
..
The hop tool has created the file:
.. Screw Holder Bottom_hop.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import hop
>>> hop.main()
This brings up the hop dialog.


>>> hop.writeOutput( 'Screw Holder Bottom.stl' )
The hop tool is parsing the file:
Screw Holder Bottom.stl
..
The hop tool has created the file:
.. Screw Holder Bottom_hop.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools import profile
from skeinforge_tools.meta_plugins import polyfile
from skeinforge_tools.skeinforge_utilities import consecution
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.skeinforge_utilities import settings
import math
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getCraftedText( fileName, text, hopRepository = None ):
	"Hop a gcode linear move text."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, text ), hopRepository )

def getCraftedTextFromText( gcodeText, hopRepository = None ):
	"Hop a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'hop' ):
		return gcodeText
	if hopRepository == None:
		hopRepository = settings.getReadRepository( HopRepository() )
	if not hopRepository.activateHop.value:
		return gcodeText
	return HopSkein().getCraftedGcode( gcodeText, hopRepository )

def getNewRepository():
	"Get the repository constructor."
	return HopRepository()

def writeOutput( fileName = '' ):
	"Hop a gcode linear move file.  Chain hop the gcode if it is not already hopped. If no fileName is specified, hop the first unmodified gcode file in this folder."
	fileName = interpret.getFirstTranslatorFileNameUnmodified( fileName )
	if fileName != '':
		consecution.writeChainTextWithNounMessage( fileName, 'hop' )


class HopRepository:
	"A class to handle the hop settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		profile.addListsToCraftTypeRepository( 'skeinforge_tools.craft_plugins.hop.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File to be Hopped', self, '' )
		self.activateHop = settings.BooleanSetting().getFromValue( 'Activate Hop', self, False )
		self.hopOverLayerThickness = settings.FloatSpin().getFromValue( 0.5, 'Hop Over Layer Thickness (ratio):', self, 1.5, 1.0 )
		self.minimumHopAngle = settings.FloatSpin().getFromValue( 20.0, 'Minimum Hop Angle (degrees):', self, 60.0, 30.0 )
		self.executeTitle = 'Hop'

	def execute( self ):
		"Hop button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


class HopSkein:
	"A class to hop a skein of extrusions."
	def __init__( self ):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.extruderActive = False
		self.feedRateMinute = 961.0
		self.hopHeight = 0.4
		self.hopDistance = self.hopHeight
		self.justDeactivated = False
		self.lineIndex = 0
		self.lines = None
		self.oldLocation = None

	def getCraftedGcode( self, gcodeText, hopRepository ):
		"Parse gcode text and store the hop gcode."
		self.lines = gcodec.getTextLines( gcodeText )
		self.minimumSlope = math.tan( math.radians( hopRepository.minimumHopAngle.value ) )
		self.parseInitialization( hopRepository )
		for self.lineIndex in xrange( self.lineIndex, len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			self.parseLine( line )
		return self.distanceFeedRate.output.getvalue()

	def getHopLine( self, line ):
		"Get hopped gcode line."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		self.feedRateMinute = gcodec.getFeedRateMinute( self.feedRateMinute, splitLine )
		if self.extruderActive:
			return line
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		highestZ = location.z
		if self.oldLocation != None:
			highestZ = max( highestZ, self.oldLocation.z )
		highestZHop = highestZ + self.hopHeight
		locationComplex = location.dropAxis( 2 )
		if self.justDeactivated:
			oldLocationComplex = self.oldLocation.dropAxis( 2 )
			distance = abs( locationComplex - oldLocationComplex )
			if distance < self.minimumDistance:
				if self.isNextTravel():
					return self.distanceFeedRate.getLineWithZ( line, splitLine, highestZHop )
			alongRatio = min( 0.41666666, self.hopDistance / distance )
			oneMinusAlong = 1.0 - alongRatio
			closeLocation = oldLocationComplex * oneMinusAlong + locationComplex * alongRatio
			self.distanceFeedRate.addLine( self.distanceFeedRate.getLineWithZ( line, splitLine, highestZHop ) )
			if self.isNextTravel():
				return self.distanceFeedRate.getLineWithZ( line, splitLine, highestZHop )
			farLocation = oldLocationComplex * alongRatio + locationComplex * oneMinusAlong
			self.distanceFeedRate.addGcodeMovementZWithFeedRate( self.feedRateMinute, farLocation, highestZHop )
			return line
		if self.isNextTravel():
			return self.distanceFeedRate.getLineWithZ( line, splitLine, highestZHop )
		return line

	def isNextTravel( self ):
		"Determine if there is another linear travel before the thread ends."
		for afterIndex in xrange( self.lineIndex + 1, len( self.lines ) ):
			line = self.lines[ afterIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = "";
			if len( splitLine ) > 0:
				firstWord = splitLine[ 0 ]
			if firstWord == 'G1':
				return True
			if firstWord == 'M101':
				return False
		return False

	def parseInitialization( self, hopRepository ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(<layerThickness>':
				layerThickness = float( splitLine[ 1 ] )
				self.hopHeight = hopRepository.hopOverLayerThickness.value * layerThickness
				self.hopDistance = self.hopHeight / self.minimumSlope
				self.minimumDistance = 0.5 * layerThickness
			elif firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine( '(<procedureDone> hop </procedureDone>)' )
				return
			self.distanceFeedRate.addLine( line )

	def parseLine( self, line ):
		"Parse a gcode line and add it to the bevel gcode."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == 'G1':
			line = self.getHopLine( line )
			self.oldLocation = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
			self.justDeactivated = False
		elif firstWord == 'M101':
			self.extruderActive = True
		elif firstWord == 'M103':
			self.extruderActive = False
			self.justDeactivated = True
		self.distanceFeedRate.addLine( line )


def main():
	"Display the hop dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
