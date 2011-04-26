"""
This page is in the table of contents.
Home is a script to home the tool.

The home manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Home

==Operation==
The default 'Activate Home' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Name of Homing File===
Default is homing.gcode.

At the beginning of a each layer, home will add the commands of a gcode script with the name of the "Name of Homing File" setting, if one exists.  Home does not care if the text file names are capitalized, but some file systems do not handle file name cases properly, so to be on the safe side you should give them lower case names.  Home looks for those files in the alterations folder in the .skeinforge folder in the home directory. If it doesn't find the file it then looks in the alterations folder in the skeinforge_plugins folder.  If it doesn't find anything there it looks in the craft_plugins folder.

==Examples==
The following examples home the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and home.py.


> python home.py
This brings up the home dialog.


> python home.py Screw Holder Bottom.stl
The home tool is parsing the file:
Screw Holder Bottom.stl
..
The home tool has created the file:
.. Screw Holder Bottom_home.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import home
>>> home.main()
This brings up the home dialog.


>>> home.writeOutput('Screw Holder Bottom.stl')
The home tool is parsing the file:
Screw Holder Bottom.stl
..
The home tool has created the file:
.. Screw Holder Bottom_home.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_craft
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
import math
import os
import sys


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = '$Date: 2008/21/04 $'
__license__ = 'GPL 3.0'


def getCraftedText( fileName, text, homeRepository = None ):
	"Home a gcode linear move file or text."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, text ), homeRepository )

def getCraftedTextFromText( gcodeText, homeRepository = None ):
	"Home a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'home'):
		return gcodeText
	if homeRepository == None:
		homeRepository = settings.getReadRepository( HomeRepository() )
	if not homeRepository.activateHome.value:
		return gcodeText
	return HomeSkein().getCraftedGcode( gcodeText, homeRepository )

def getNewRepository():
	"Get the repository constructor."
	return HomeRepository()

def writeOutput(fileName=''):
	"Home a gcode linear move file.  Chain home the gcode if it is not already homed. If no fileName is specified, home the first unmodified gcode file in this folder."
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified(fileName)
	if fileName != '':
		skeinforge_craft.writeChainTextWithNounMessage( fileName, 'home')


class HomeRepository:
	"A class to handle the home settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository('skeinforge_application.skeinforge_plugins.craft_plugins.home.html', None, self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Home', self, '')
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute('http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_home')
		self.activateHome = settings.BooleanSetting().getFromValue('Activate Home', self, True )
		self.nameOfHomingFile = settings.StringSetting().getFromValue('Name of Homing File:', self, 'homing.gcode')
		self.executeTitle = 'Home'

	def execute(self):
		"Home button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode(self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled)
		for fileName in fileNames:
			writeOutput(fileName)


class HomeSkein:
	"A class to home a skein of extrusions."
	def __init__(self):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.extruderActive = False
		self.highestZ = None
		self.homingText = ''
		self.layerCount = settings.LayerCount()
		self.lineIndex = 0
		self.lines = None
		self.oldLocation = None
		self.shouldHome = False
		self.travelFeedRatePerMinute = 957.0

	def addFloat( self, begin, end ):
		"Add dive to the original height."
		beginEndDistance = begin.distance(end)
		alongWay = self.absolutePerimeterWidth / beginEndDistance
		closeToEnd = euclidean.getIntermediateLocation( alongWay, end, begin )
		closeToEnd.z = self.highestZ
		self.distanceFeedRate.addLine( self.distanceFeedRate.getLinearGcodeMovementWithFeedRate( self.travelFeedRatePerMinute, closeToEnd.dropAxis(2), closeToEnd.z ) )

	def addHopUp(self, location):
		"Add hop to highest point."
		locationUp = Vector3( location.x, location.y, self.highestZ )
		self.distanceFeedRate.addLine( self.distanceFeedRate.getLinearGcodeMovementWithFeedRate( self.travelFeedRatePerMinute, locationUp.dropAxis(2), locationUp.z ) )

	def addHomeTravel( self, splitLine ):
		"Add the home travel gcode."
		location = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
		self.highestZ = max( self.highestZ, location.z )
		if not self.shouldHome:
			return
		self.shouldHome = False
		if self.oldLocation == None:
			return
		if self.extruderActive:
			self.distanceFeedRate.addLine('M103')
		self.addHopUp( self.oldLocation )
		self.distanceFeedRate.addLinesSetAbsoluteDistanceMode( self.homingLines )
		self.addHopUp( self.oldLocation )
		self.addFloat( self.oldLocation, location )
		if self.extruderActive:
			self.distanceFeedRate.addLine('M101')

	def getCraftedGcode( self, gcodeText, homeRepository ):
		"Parse gcode text and store the home gcode."
		self.homingText = settings.getFileInAlterationsOrGivenDirectory( os.path.dirname( __file__ ), homeRepository.nameOfHomingFile.value )
		if len( self.homingText ) < 1:
			return gcodeText
		self.lines = gcodec.getTextLines(gcodeText)
		self.homeRepository = homeRepository
		self.parseInitialization( homeRepository )
		self.homingLines = gcodec.getTextLines( self.homingText )
		for self.lineIndex in xrange( self.lineIndex, len(self.lines) ):
			line = self.lines[self.lineIndex]
			self.parseLine(line)
		return self.distanceFeedRate.output.getvalue()

	def parseInitialization( self, homeRepository ):
		'Parse gcode initialization and store the parameters.'
		for self.lineIndex in xrange(len(self.lines)):
			line = self.lines[self.lineIndex]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			self.distanceFeedRate.parseSplitLine(firstWord, splitLine)
			if firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine('(<procedureDone> home </procedureDone>)')
				return
			elif firstWord == '(<perimeterWidth>':
				self.absolutePerimeterWidth = abs(float(splitLine[1]))
			elif firstWord == '(<travelFeedRatePerSecond>':
				self.travelFeedRatePerMinute = 60.0 * float(splitLine[1])
			self.distanceFeedRate.addLine(line)

	def parseLine(self, line):
		"Parse a gcode line and add it to the bevel gcode."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
		if len(splitLine) < 1:
			return
		firstWord = splitLine[0]
		if firstWord == 'G1':
			self.addHomeTravel(splitLine)
			self.oldLocation = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
		elif firstWord == '(<layer>':
			self.layerCount.printProgressIncrement('home')
			if self.homingText != '':
				self.shouldHome = True
		elif firstWord == 'M101':
			self.extruderActive = True
		elif firstWord == 'M103':
			self.extruderActive = False
		self.distanceFeedRate.addLine(line)


def main():
	"Display the home dialog."
	if len(sys.argv) > 1:
		writeOutput(' '.join(sys.argv[1 :]))
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
