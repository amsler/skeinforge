"""
Gcodec is a collection of utilities to decode and encode gcode.

To run gcodec, install python 2.x on your machine, which is avaliable from http://www.python.org/download/

Then in the folder which gcodec is in, type 'python' in a shell to run the python interpreter.  Finally type 'from gcodec import *' to import this program.

Below is an example of gcodec use.  This example is run in a terminal in the folder which contains gcodec and Screw Holder Bottom_export.gcode.

>>> from gcodec import *
>>> getFileText('Screw Holder Bottom_export.gcode')
'G90\nG21\nM103\nM105\nM106\nM110 S60.0\nM111 S30.0\nM108 S210.0\nM104 S235.0\nG1 X0.37 Y-4.07 Z1.9 F60.0\nM101\n
..
many lines of text
..

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import archive
from fabmetheus_utilities import euclidean
import cStringIO
import math
import os
import sys
import traceback


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = '$Date: 2008/21/04 $'
__license__ = 'GPL 3.0'


def addLineAndNewlineIfNecessary(line, output):
	'Add the line and if the line does not end with a newline add a newline.'
	output.write(line)
	if len(line) < 1:
		return
	if not line.endswith('\n'):
		output.write('\n')

def getArcDistance(relativeLocation, splitLine):
	'Get arc distance.'
	halfPlaneLineDistance = 0.5 * abs(relativeLocation.dropAxis(2))
	radius = getDoubleFromCharacterSplitLine('R', splitLine)
	if radius == None:
		iFloat = getDoubleFromCharacterSplitLine('I', splitLine)
		jFloat = getDoubleFromCharacterSplitLine('J', splitLine)
		radius = abs(complex(iFloat, jFloat))
	angle = 0.0
	if radius > 0.0:
		halfPlaneLineDistanceOverRadius = halfPlaneLineDistance / radius
		if halfPlaneLineDistance < radius:
			angle = 2.0 * math.asin(halfPlaneLineDistanceOverRadius)
		else:
			angle = math.pi * halfPlaneLineDistanceOverRadius
	return abs(complex(angle * radius, relativeLocation.z))

def getDoubleAfterFirstLetter(word):
	'Get the double value of the word after the first letter.'
	return float(word[1 :])

def getDoubleForLetter(letter, splitLine):
	'Get the double value of the word after the first occurence of the letter in the split line.'
	return getDoubleAfterFirstLetter(splitLine[getIndexOfStartingWithSecond(letter, splitLine)])

def getDoubleFromCharacterSplitLine(character, splitLine):
	'Get the double value of the string after the first occurence of the character in the split line.'
	indexOfCharacter = getIndexOfStartingWithSecond(character, splitLine)
	if indexOfCharacter < 0:
		return None
	floatString = splitLine[indexOfCharacter][1 :]
	try:
		return float(floatString)
	except ValueError:
		return None

def getDoubleFromCharacterSplitLineValue(character, splitLine, value):
	'Get the double value of the string after the first occurence of the character in the split line, if it does not exist return the value.'
	splitLineFloat = getDoubleFromCharacterSplitLine(character, splitLine)
	if splitLineFloat == None:
		return value
	return splitLineFloat

def getFeedRateMinute(feedRateMinute, splitLine):
	'Get the feed rate per minute if the split line has a feed rate.'
	indexOfF = getIndexOfStartingWithSecond('F', splitLine)
	if indexOfF > 0:
		return getDoubleAfterFirstLetter( splitLine[indexOfF] )
	return feedRateMinute

def getFirstWord(splitLine):
	'Get the first word of a split line.'
	if len(splitLine) > 0:
		return splitLine[0]
	return ''

def getFirstWordFromLine(line):
	'Get the first word of a line.'
	return getFirstWord(line.split())

def getGcodeFileText(fileName, gcodeText):
	'Get the gcode text from a file if it the gcode text is empty and if the file is a gcode file.'
	if gcodeText != '':
		return gcodeText
	if fileName.endswith('.gcode'):
		return archive.getFileText(fileName)
	return ''

def getIndexOfStartingWithSecond(letter, splitLine):
	'Get index of the first occurence of the given letter in the split line, starting with the second word.  Return - 1 if letter is not found'
	for wordIndex in xrange( 1, len(splitLine) ):
		word = splitLine[ wordIndex ]
		firstLetter = word[0]
		if firstLetter == letter:
			return wordIndex
	return - 1

def getLineWithValueString(character, line, splitLine, valueString):
	'Get the line with a valueString.'
	roundedValueString = character + valueString
	indexOfValue = getIndexOfStartingWithSecond(character, splitLine)
	if indexOfValue == - 1:
		return line + ' ' + roundedValueString
	word = splitLine[indexOfValue]
	return line.replace(word, roundedValueString)

def getLocationFromSplitLine(oldLocation, splitLine):
	'Get the location from the split line.'
	if oldLocation == None:
		oldLocation = Vector3()
	return Vector3(
		getDoubleFromCharacterSplitLineValue('X', splitLine, oldLocation.x),
		getDoubleFromCharacterSplitLineValue('Y', splitLine, oldLocation.y),
		getDoubleFromCharacterSplitLineValue('Z', splitLine, oldLocation.z))

def getSplitLineBeforeBracketSemicolon(line):
	'Get the split line before a bracket or semicolon.'
	semicolonIndex = line.find(';')
	if semicolonIndex >= 0:
		line = line[ : semicolonIndex ]
	bracketIndex = line.find('(')
	if bracketIndex > 0:
		return line[: bracketIndex].split()
	return line.split()

def getStringFromCharacterSplitLine(character, splitLine):
	'Get the string after the first occurence of the character in the split line.'
	indexOfCharacter = getIndexOfStartingWithSecond(character, splitLine)
	if indexOfCharacter < 0:
		return None
	return splitLine[indexOfCharacter][1 :]

def getWithoutBracketsEqualTab(line):
	'Get a string without the greater than sign, the bracket and less than sign, the equal sign or the tab.'
	line = line.replace('=', ' ')
	line = line.replace('(<', '')
	line = line.replace('>', '')
	return line.replace('\t', '')

def isProcedureDone(gcodeText, procedure):
	'Determine if the procedure has been done on the gcode text.'
	if gcodeText == '':
		return False
	lines = archive.getTextLines(gcodeText)
	for line in lines:
		withoutBracketsEqualTabQuotes = getWithoutBracketsEqualTab(line).replace('"', '').replace("'", '')
		splitLine = getWithoutBracketsEqualTab( withoutBracketsEqualTabQuotes ).split()
		firstWord = getFirstWord(splitLine)
		if firstWord == 'procedureDone':
			if splitLine[1].find(procedure) != -1:
				return True
		elif firstWord == 'extrusionStart':
			return False
		procedureIndex = line.find(procedure)
		if procedureIndex != -1:
			if 'procedureDone' in splitLine:
				nextIndex = splitLine.index('procedureDone') + 1
				if nextIndex < len(splitLine):
					nextWordSplit = splitLine[nextIndex].split(',')
					if procedure in nextWordSplit:
						return True
	return False

def isProcedureDoneOrFileIsEmpty(gcodeText, procedure):
	'Determine if the procedure has been done on the gcode text or the file is empty.'
	if gcodeText == '':
		return True
	return isProcedureDone(gcodeText, procedure)

def isThereAFirstWord(firstWord, lines, startIndex):
	'Parse gcode until the first word if there is one.'
	for lineIndex in xrange(startIndex, len(lines)):
		line = lines[lineIndex]
		splitLine = getSplitLineBeforeBracketSemicolon(line)
		if firstWord == getFirstWord(splitLine):
			return True
	return False


class BoundingRectangle:
	'A class to get the corners of a gcode text.'
	def getFromGcodeLines(self, lines, radius):
		'Parse gcode text and get the minimum and maximum corners.'
		self.cornerMaximum = complex(-999999999.0, -999999999.0)
		self.cornerMinimum = complex(999999999.0, 999999999.0)
		self.oldLocation = None
		self.cornerRadius = complex(radius, radius)
		for line in lines:
			self.parseCorner(line)
		return self

	def isPointInside(self, point):
		'Determine if the point is inside the bounding rectangle.'
		return point.imag >= self.cornerMinimum.imag and point.imag <= self.cornerMaximum.imag and point.real >= self.cornerMinimum.real and point.real <= self.cornerMaximum.real

	def parseCorner(self, line):
		'Parse a gcode line and use the location to update the bounding corners.'
		splitLine = getSplitLineBeforeBracketSemicolon(line)
		firstWord = getFirstWord(splitLine)
		if firstWord == '(<boundaryPoint>':
			locationComplex = getLocationFromSplitLine(None, splitLine).dropAxis(2)
			self.cornerMaximum = euclidean.getMaximum(self.cornerMaximum, locationComplex)
			self.cornerMinimum = euclidean.getMinimum(self.cornerMinimum, locationComplex)
		elif firstWord == 'G1':
			location = getLocationFromSplitLine(self.oldLocation, splitLine)
			locationComplex = location.dropAxis(2)
			self.cornerMaximum = euclidean.getMaximum(self.cornerMaximum, locationComplex + self.cornerRadius)
			self.cornerMinimum = euclidean.getMinimum(self.cornerMinimum, locationComplex - self.cornerRadius)
			self.oldLocation = location


class DistanceFeedRate:
	'A class to limit the z feed rate and round values.'
	def __init__(self):
		'Initialize.'
		self.decimalPlacesCarried = 3
		self.output = cStringIO.StringIO()

	def addGcodeFromFeedRateThreadZ(self, feedRateMinute, thread, z):
		'Add a thread to the output.'
		if len(thread) > 0:
			self.addGcodeMovementZWithFeedRate(feedRateMinute, thread[0], z)
		else:
			print('zero length vertex positions array which was skipped over, this should never happen.')
		if len(thread) < 2:
			print('thread of only one point in addGcodeFromFeedRateThreadZ in gcodec, this should never happen.')
			print(thread)
			return
		self.addLine('M101') # Turn extruder on.
		for point in thread[1 :]:
			self.addGcodeMovementZWithFeedRate(feedRateMinute, point, z)
		self.addLine('M103') # Turn extruder off.

	def addGcodeFromLoop(self, loop, z):
		'Add the gcode loop.'
		euclidean.addSurroundingLoopBeginning(self, loop, z)
		self.addPerimeterBlock(loop, z)
		self.addLine('(</boundaryPerimeter>)')
		self.addLine('(</surroundingLoop>)')

	def addGcodeFromThreadZ(self, thread, z):
		'Add a thread to the output.'
		if len(thread) > 0:
			self.addGcodeMovementZ(thread[0], z)
		else:
			print('zero length vertex positions array which was skipped over, this should never happen.')
		if len(thread) < 2:
			print('thread of only one point in addGcodeFromThreadZ in gcodec, this should never happen.')
			print(thread)
			return
		self.addLine('M101') # Turn extruder on.
		for point in thread[1 :]:
			self.addGcodeMovementZ(point, z)
		self.addLine('M103') # Turn extruder off.

	def addGcodeMovementZ(self, point, z):
		'Add a movement to the output.'
		self.addLine(self.getLinearGcodeMovement(point, z))

	def addGcodeMovementZWithFeedRate(self, feedRateMinute, point, z):
		'Add a movement to the output.'
		self.addLine(self.getLinearGcodeMovementWithFeedRate(feedRateMinute, point, z))

	def addLine(self, line):
		'Add a line of text and a newline to the output.'
		if len(line) > 0:
			self.output.write(line + '\n')

	def addLines(self, lines):
		'Add lines of text to the output.'
		for line in lines:
			self.addLine(line)

	def addLinesSetAbsoluteDistanceMode(self, lines):
		'Add lines of text to the output and ensure the absolute mode is set.'
		if len(lines) < 1:
			return
		if len(lines[0]) < 1:
			return
		absoluteDistanceMode = True
		self.addLine('(<alteration>)')
		for line in lines:
			splitLine = line.split()
			firstWord = getFirstWord(splitLine)
			if firstWord == 'G90':
				absoluteDistanceMode = True
			elif firstWord == 'G91':
				absoluteDistanceMode = False
			self.addLine(line)
		if not absoluteDistanceMode:
			self.addLine('G90')
		self.addLine('(</alteration>)')

	def addParameter(self, firstWord, parameter):
		'Add the parameter.'
		self.addLine(firstWord + ' S' + euclidean.getRoundedToThreePlaces(parameter))

	def addPerimeterBlock(self, loop, z):
		'Add the perimeter gcode block for the loop.'
		if len(loop) < 2:
			return
		if euclidean.isWiddershins(loop): # Indicate that a perimeter is beginning.
			self.addLine('(<perimeter> outer )')
		else:
			self.addLine('(<perimeter> inner )')
		self.addGcodeFromThreadZ(loop + [loop[0]], z)
		self.addLine('(</perimeter>)') # Indicate that a perimeter is beginning.

	def addTagBracketedLine(self, tagName, value):
		'Add a begin tag, balue and end tag.'
		self.addLine('(<%s> %s </%s>)' % (tagName, value, tagName))

	def getBoundaryLine(self, location):
		'Get boundary gcode line.'
		return '(<boundaryPoint> X%s Y%s Z%s </boundaryPoint>)' % (self.getRounded(location.x), self.getRounded(location.y), self.getRounded(location.z))

	def getFirstWordMovement(self, firstWord, location):
		'Get the start of the arc line.'
		return '%s X%s Y%s Z%s' % (firstWord, self.getRounded(location.x), self.getRounded(location.y), self.getRounded(location.z))

	def getLinearGcodeMovement(self, point, z):
		'Get a linear gcode movement.'
		return 'G1 X%s Y%s Z%s' % ( self.getRounded( point.real ), self.getRounded( point.imag ), self.getRounded(z) )

	def getLinearGcodeMovementWithFeedRate(self, feedRateMinute, point, z):
		'Get a z limited gcode movement.'
		linearGcodeMovement = self.getLinearGcodeMovement(point, z)
		if feedRateMinute == None:
			return linearGcodeMovement
		return linearGcodeMovement + ' F' + self.getRounded(feedRateMinute)

	def getLineWithFeedRate(self, feedRateMinute, line, splitLine):
		'Get the line with a feed rate.'
		return getLineWithValueString('F', line, splitLine, self.getRounded(feedRateMinute))

	def getLineWithX(self, line, splitLine, x):
		'Get the line with an x.'
		return getLineWithValueString('X', line, splitLine, self.getRounded(x))

	def getLineWithY(self, line, splitLine, y):
		'Get the line with a y.'
		return getLineWithValueString('Y', line, splitLine, self.getRounded(y))

	def getLineWithZ(self, line, splitLine, z):
		'Get the line with a z.'
		return getLineWithValueString('Z', line, splitLine, self.getRounded(z))

	def getRounded(self, number):
		'Get number rounded to the number of carried decimal places as a string.'
		return euclidean.getRoundedToPlacesString(self.decimalPlacesCarried, number)

	def parseSplitLine(self, firstWord, splitLine):
		'Parse gcode split line and store the parameters.'
		firstWord = getWithoutBracketsEqualTab(firstWord)
		if firstWord == 'decimalPlacesCarried':
			self.decimalPlacesCarried = int(splitLine[1])
