"""
This page is in the table of contents.
Gcode step is an export plugin to convert gcode from float position to number of steps.

An export plugin is a script in the export_plugins folder which has the functions getOutput, isReplaceable and if it's output is not replaceable, writeOutput.  It is meant to be run from the export tool.  To ensure that the plugin works on platforms which do not handle file capitalization properly, give the plugin a lower case name.

The getOutput function of this script takes a gcode text and returns it with the positions converted into number of steps.  The writeOutput function of this script takes a gcode text and writes that with the positions converted into number of steps.

==Settings==
===Add Feed Rate Even When Unchanging===
Default is on.

When selected, the feed rate will be added even when it did not change from the previous line.

===Add Space Between Words===
Default is on.

When selected, a space will be added between each gcode word.

===Add Z Even When Unchanging===
Default is on.

When selected, the z word will be added even when it did not change.

===Feed Rate Step Length===
Default is 0.1 millimeters/second.

Defines the feed rate step length.

===Offset===
====X Offset====
Default is zero.

Defines the X Offset.

====Y Offset====
Default is zero.

Defines the Y Offset.

====Z Offset====
Default is zero.

Defines the Z Offset.

===Radius Rate Step Length===
Default is 0.1 millimeters/second.

Defines the radius step length.

===Step Length===
====X Step Length====
Default is 0.1 millimeters.

Defines the X axis step length.

====Y Step Length====
Default is 0.1 millimeters.

Defines the Y axis step length.

====Z Step Length====
Default is 0.01 millimeters.

Defines the Z axis step length.

"""


from __future__ import absolute_import
import __init__
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from skeinforge.skeinforge_utilities import skeinforge_polyfile
from struct import Struct
import cStringIO
import os
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getCharacterIntegerString( character, offset, splitLine, stepLength ):
	"Get a character and integer string."
	floatValue = getFloatFromCharacterSplitLine( character, splitLine )
	if floatValue == None:
		return None
	floatValue += offset
	integerValue = int( round( float( floatValue / stepLength ) ) )
	return character + str( integerValue )

def getFloatFromCharacterSplitLine( character, splitLine ):
	"Get the float after the first occurence of the character in the split line."
	lineFromCharacter = gcodec.getStringFromCharacterSplitLine( character, splitLine )
	if lineFromCharacter == None:
		return None
	return float( lineFromCharacter )

def getOutput( gcodeText, gcodeStepRepository = None ):
	"Get the exported version of a gcode file.  This function, isReplaceable and if it's output is not replaceable, writeOutput are the only necessary functions in a skeinforge export plugin."
	if gcodeText == '':
		return ''
	if gcodeStepRepository == None:
		gcodeStepRepository = GcodeStepRepository()
		settings.getReadRepository( gcodeStepRepository )
	return GcodeStepSkein().getCraftedGcode( gcodeStepRepository, gcodeText )

def getNewRepository():
	"Get the repository constructor."
	return GcodeStepRepository()

def isReplaceable():
	"Return whether or not the output from this plugin is replaceable.  This should be true if the output is text and false if it is binary."
	return True

def writeOutput( fileName, gcodeText = '' ):
	"Write the exported version of a gcode file."
	gcodeText = gcodec.getGcodeFileText( fileName, gcodeText )
	repository = GcodeStepRepository()
	settings.getReadRepository( repository )
	output = getOutput( gcodeText, repository )
	suffixFileName = fileName[ : fileName.rfind( '.' ) ] + '_gcode_step.gcode'
	gcodec.writeFileText( suffixFileName, output )
	print( 'The converted file is saved as ' + gcodec.getSummarizedFileName( suffixFileName ) )


class GcodeStepRepository:
	"A class to handle the export settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		#Set the default settings.
		settings.addListsToRepository( 'skeinforge.skeinforge_plugins.craft_plugins.export_plugins.gcode_step.html', '', self )
		self.addFeedRateEvenWhenUnchanging = settings.BooleanSetting().getFromValue( 'Add Feed Rate Even When Unchanging', self, True )
		self.addSpaceBetweenWords = settings.BooleanSetting().getFromValue( 'Add Space Between Words', self, True )
		self.addZEvenWhenUnchanging = settings.BooleanSetting().getFromValue( 'Add Z Even When Unchanging', self, True )
		self.fileNameInput = settings.FileNameInput().getFromFileName( [ ( 'Gcode text files', '*.gcode' ) ], 'Open File to be Converted to Gcode Step', self, '' )
		self.feedRateStepLength = settings.FloatSpin().getFromValue( 0.0, 'Feed Rate Step Length (millimeters/second)', self, 1.0, 0.1 )
		settings.LabelDisplay().getFromName( 'Offset:', self )
		self.xOffset = settings.FloatSpin().getFromValue( - 100.0, 'X Offset (millimeters)', self, 100.0, 0.0 )
		self.yOffset = settings.FloatSpin().getFromValue( -100.0, 'Y Offset (millimeters)', self, 100.0, 0.0 )
		self.zOffset = settings.FloatSpin().getFromValue( - 10.0, 'Z Offset (millimeters)', self, 10.0, 0.0 )
		self.radiusStepLength = settings.FloatSpin().getFromValue( 0.0, 'Radius Step Length (millimeters)', self, 1.0, 0.1 )
		settings.LabelDisplay().getFromName( 'Step Length:', self )
		self.xStepLength = settings.FloatSpin().getFromValue( 0.0, 'X Step Length (millimeters)', self, 1.0, 0.1 )
		self.yStepLength = settings.FloatSpin().getFromValue( 0.0, 'Y Step Length (millimeters)', self, 1.0, 0.1 )
		self.zStepLength = settings.FloatSpin().getFromValue( 0.0, 'Z Step Length (millimeters)', self, 0.2, 0.01 )
		#Create the archive, title of the execute button, title of the dialog & settings fileName.
		self.executeTitle = 'Convert to Gcode Step'

	def execute( self ):
		"Convert to gcode step button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, [ '.gcode' ], self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


class GcodeStepSkein:
	"A class to convert gcode into 16 byte binary segments."
	def __init__( self ):
		self.oldFeedRateString = None
		self.oldZString = None
		self.output = cStringIO.StringIO()

	def addCharacterInteger( self, character, lineStringIO, offset, splitLine, stepLength ):
		"Add a character and integer to line string."
		characterIntegerString = getCharacterIntegerString( character, offset, splitLine, stepLength )
		self.addStringToLine( lineStringIO, characterIntegerString )

	def addLine( self, line ):
		"Add a line of text and a newline to the output."
		self.output.write( line + '\n' )

	def addStringToLine( self, lineStringIO, wordString ):
		"Add a character and integer to line string."
		if wordString == None:
			return
		if self.gcodeStepRepository.addSpaceBetweenWords.value:
			lineStringIO.write( ' ' )
		lineStringIO.write( wordString )

	def getCraftedGcode( self, gcodeStepRepository, gcodeText ):
		"Parse gcode text and store the gcode."
		self.gcodeStepRepository = gcodeStepRepository
		lines = gcodec.getTextLines( gcodeText )
		for line in lines:
			self.parseLine( line )
		return self.output.getvalue()

	def parseLine( self, line ):
		"Parse a gcode line."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		firstWord = gcodec.getFirstWord( splitLine )
		if len( firstWord ) < 1:
			return
		firstLetter = firstWord[ 0 ]
		if firstLetter == '(':
			return
		if firstWord != 'G1' and firstWord != 'G2' and firstWord != 'G3':
			self.addLine( line )
			return
		lineStringIO = cStringIO.StringIO()
		lineStringIO.write( firstWord )
		self.addCharacterInteger( 'I', lineStringIO, 0.0, splitLine, self.gcodeStepRepository.xStepLength.value )
		self.addCharacterInteger( 'J', lineStringIO, 0.0, splitLine, self.gcodeStepRepository.yStepLength.value )
		self.addCharacterInteger( 'R', lineStringIO, 0.0, splitLine, self.gcodeStepRepository.radiusStepLength.value )
		self.addCharacterInteger( 'X', lineStringIO, self.gcodeStepRepository.xOffset.value, splitLine, self.gcodeStepRepository.xStepLength.value )
		self.addCharacterInteger( 'Y', lineStringIO, self.gcodeStepRepository.yOffset.value, splitLine, self.gcodeStepRepository.yStepLength.value )
		zString = getCharacterIntegerString( 'Z', self.gcodeStepRepository.zOffset.value, splitLine, self.gcodeStepRepository.zStepLength.value )
		feedRateString = getCharacterIntegerString( 'F', 0.0, splitLine, self.gcodeStepRepository.feedRateStepLength.value )
		if zString != None:
			if zString != self.oldZString or self.gcodeStepRepository.addZEvenWhenUnchanging.value:
				self.addStringToLine( lineStringIO, zString )
		if feedRateString != None:
			if feedRateString != self.oldFeedRateString or self.gcodeStepRepository.addFeedRateEvenWhenUnchanging.value:
				self.addStringToLine( lineStringIO, feedRateString )
		self.addLine( lineStringIO.getvalue() )
		self.oldFeedRateString = feedRateString
		self.oldZString = zString


def main():
	"Display the export dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
