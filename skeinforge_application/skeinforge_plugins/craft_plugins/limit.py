#! /usr/bin/env python
"""
This page is in the table of contents.

Limit limts the feed rate of the tool head, so that the stepper motors are not driven too fast and skip steps.

==Operation==
The default 'Activate Limit' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Maximum Initial Feed Rate===
Default is one millimeter per second.

Defines the maximum speed of the inital tool head will move.

===Maximum Z Feed Rate===
Default is one millimeter per second.

If your firmware limits the z feed rate, you do not need to set this setting.

Defines the maximum speed that the tool head will move in the z direction.

==Examples==
The following examples limit the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and limit.py.


> python limit.py
This brings up the limit dialog.


> python limit.py Screw Holder Bottom.stl
The limit tool is parsing the file:
Screw Holder Bottom.stl
..
The limit tool has created the file:
.. Screw Holder Bottom_limit.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import limit
>>> limit.main()
This brings up the limit dialog.


>>> limit.writeOutput('Screw Holder Bottom.stl')
The limit tool is parsing the file:
Screw Holder Bottom.stl
..
The limit tool has created the file:
.. Screw Holder Bottom_limit.gcode

"""

#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from datetime import date
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import intercircle
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_craft
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
from skeinforge_application.skeinforge_utilities import skeinforge_profile
import math
import os
import sys


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = '$Date: 2008/28/04 $'
__license__ = 'GPL 3.0'


def getCraftedText(fileName, gcodeText='', repository=None):
	'Limit a gcode file or text.'
	return getCraftedTextFromText( gcodec.getTextIfEmpty(fileName, gcodeText), repository )

def getCraftedTextFromText(gcodeText, repository=None):
	'Limit a gcode text.'
	if gcodec.isProcedureDoneOrFileIsEmpty(gcodeText, 'limit'):
		return gcodeText
	if repository == None:
		repository = settings.getReadRepository(LimitRepository())
	if not repository.activateLimit.value:
		return gcodeText
	return LimitSkein().getCraftedGcode(gcodeText, repository)

def getNewRepository():
	'Get the repository constructor.'
	return LimitRepository()

def writeOutput(fileName=''):
	'Limit a gcode file.'
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified(fileName)
	if fileName != '':
		skeinforge_craft.writeChainTextWithNounMessage( fileName, 'limit')


class LimitRepository:
	'A class to handle the limit settings.'
	def __init__(self):
		'Set the default settings, execute title & settings fileName.'
		skeinforge_profile.addListsToCraftTypeRepository('skeinforge_application.skeinforge_plugins.craft_plugins.limit.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Limit', self, '')
		self.activateLimit = settings.BooleanSetting().getFromValue('Activate Limit', self, True)
		self.maximumInitialFeedRate = settings.FloatSpin().getFromValue(0.5, 'Maximum Initial Feed Rate (mm/s):', self, 10.0, 1.0)
		self.maximumZFeedRatePerSecond = settings.FloatSpin().getFromValue(0.5, 'Maximum Z Feed Rate (mm/s):', self, 10.0, 1.0)
		self.executeTitle = 'Limit'

	def execute(self):
		'Limit button has been clicked.'
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode(self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled)
		for fileName in fileNames:
			writeOutput(fileName)


class LimitSkein:
	'A class to limit a skein of extrusions.'
	def __init__(self):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.feedRateMinute = None
		self.lineIndex = 0
		self.oldLocation = None

	def getCraftedGcode(self, gcodeText, repository):
		'Parse gcode text and store the limit gcode.'
		self.maximumZDrillFeedRatePerSecond = repository.maximumZFeedRatePerSecond.value
		self.maximumZTravelFeedRatePerSecond = repository.maximumZFeedRatePerSecond.value
		self.maximumZFeedRatePerSecond = self.maximumZTravelFeedRatePerSecond
		self.repository = repository
		self.lines = gcodec.getTextLines(gcodeText)
		self.parseInitialization()
		for lineIndex in xrange( self.lineIndex, len(self.lines) ):
			self.parseLine( lineIndex )
		return self.distanceFeedRate.output.getvalue()

	def getLimitedInitialMovement(self, line, splitLine):
		'Get a limited linear movement.'
		if self.oldLocation == None:
			line = self.distanceFeedRate.getLineWithFeedRate(60.0 * self.repository.maximumInitialFeedRate.value, line, splitLine)
		return line

	def getZLimitedLine(self, deltaZ, distance, line, splitLine):
		'Get a replaced z limited gcode movement line.'
		zFeedRateSecond = self.feedRateMinute * deltaZ / distance / 60.0
		if zFeedRateSecond <= self.maximumZFeedRatePerSecond:
			return line
		limitedFeedRateMinute = self.feedRateMinute * self.maximumZFeedRatePerSecond / zFeedRateSecond
		return self.distanceFeedRate.getLineWithFeedRate(limitedFeedRateMinute, line, splitLine)

	def getZLimitedLineArc(self, line, splitLine):
		'Get a replaced z limited gcode arc movement line.'
		self.feedRateMinute = gcodec.getFeedRateMinute(self.feedRateMinute, splitLine)
		if self.feedRateMinute == None or self.oldLocation == None:
			return line
		relativeLocation = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
		self.oldLocation += relativeLocation
		deltaZ = abs(relativeLocation.z)
		distance = gcodec.getArcDistance(relativeLocation, splitLine)
		return self.getZLimitedLine(deltaZ, distance, line, splitLine)

	def getZLimitedLineLinear(self, line, location, splitLine):
		'Get a replaced z limited gcode linear movement line.'
		self.feedRateMinute = gcodec.getFeedRateMinute(self.feedRateMinute, splitLine)
		if location == self.oldLocation:
			return ''
		if self.feedRateMinute == None or self.oldLocation == None:
			return line
		deltaZ = abs(location.z - self.oldLocation.z)
		distance = abs(location - self.oldLocation)
		return self.getZLimitedLine(deltaZ, distance, line, splitLine)

	def parseInitialization(self):
		'Parse gcode initialization and store the parameters.'
		for self.lineIndex in xrange(len(self.lines)):
			line = self.lines[self.lineIndex]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			self.distanceFeedRate.parseSplitLine(firstWord, splitLine)
			if firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine('(<procedureDone> limit </procedureDone>)')
				return
			elif firstWord == '(<maximumZDrillFeedRatePerSecond>':
				self.maximumZDrillFeedRatePerSecond = float(splitLine[1])
			elif firstWord == '(<perimeterWidth>':
				self.distanceFeedRate.addTagBracketedLine('maximumZTravelFeedRatePerSecond', self.maximumZTravelFeedRatePerSecond )
			self.distanceFeedRate.addLine(line)

	def parseLine( self, lineIndex ):
		'Parse a gcode line and add it to the limit skein.'
		line = self.lines[lineIndex].lstrip()
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
		if len(splitLine) < 1:
			return
		firstWord = gcodec.getFirstWord(splitLine)
		if firstWord == 'G1':
			location = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
			line = self.getLimitedInitialMovement(line, splitLine)
			line = self.getZLimitedLineLinear(line, location, splitLine)
			self.oldLocation = location
		elif firstWord == 'G2' or firstWord == 'G3':
			line = self.getZLimitedLineArc(line, splitLine)
		elif firstWord == 'M101':
			self.maximumZFeedRatePerSecond = self.maximumZDrillFeedRatePerSecond
		elif firstWord == 'M103':
			self.maximumZFeedRatePerSecond = self.maximumZTravelFeedRatePerSecond
		self.distanceFeedRate.addLine(line)


def main():
	'Display the limit dialog.'
	if len(sys.argv) > 1:
		writeOutput(' '.join(sys.argv[1 :]))
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == '__main__':
	main()
