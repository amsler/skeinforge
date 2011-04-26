#! /usr/bin/env python
"""
This page is in the table of contents.
Dimension adds Adrian's extruder distance E value to the gcode movement lines, as described at:
http://blog.reprap.org/2009/05/4d-printing.html

and in Erik de Bruijn's conversion script page at:
http://objects.reprap.org/wiki/3D-to-5D-Gcode.php

The dimension manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Dimension

==Operation==
The default 'Activate Dimension' checkbox is off.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Extrusion Distance Format Choice===
Default is 'Absolute Extrusion Distance' because in Adrian's description the distance is absolute.  In future, because the relative distances are smaller than the cumulative absolute distances, hopefully the firmaware will be able to use relative distance.

====Absolute Extrusion Distance====
When selected, the extrusion distance output will be the total extrusion distance to that gcode line.

====Relative Extrusion Distance====
When selected, the extrusion distance output will be the extrusion distance from the last gcode line.

===Extruder Retraction Speed===
Default is 13.3 mm/s.

Defines the extruder retraction feed rate.

===Retraction Distance===
Default is zero.

Defines the retraction distance when the thread ends.

===Restart Extra Distance===
Default is zero.

Defines the restart extra distance when the thread restarts.  The restart distance will be the retraction distance plus the restart extra distance.

==Examples==
The following examples dimension the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and dimension.py.


> python dimension.py
This brings up the dimension dialog.


> python dimension.py Screw Holder Bottom.stl
The dimension tool is parsing the file:
Screw Holder Bottom.stl
..
The dimension tool has created the file:
.. Screw Holder Bottom_dimension.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import dimension
>>> dimension.main()
This brings up the dimension dialog.


>>> dimension.writeOutput('Screw Holder Bottom.stl')
The dimension tool is parsing the file:
Screw Holder Bottom.stl
..
The dimension tool has created the file:
.. Screw Holder Bottom_dimension.gcode

"""

from __future__ import absolute_import
try:
	import psyco
	psyco.full()
except:
	pass
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from datetime import date
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
__date__ = "$Date: 2008/28/04 $"
__license__ = 'GPL 3.0'


def getCraftedText( fileName, gcodeText = '', repository = None ):
	"Dimension a gcode file or text."
	return getCraftedTextFromText( gcodec.getTextIfEmpty(fileName, gcodeText), repository )

def getCraftedTextFromText( gcodeText, repository = None ):
	"Dimension a gcode text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'dimension'):
		return gcodeText
	if repository == None:
		repository = settings.getReadRepository( DimensionRepository() )
	if not repository.activateDimension.value:
		return gcodeText
	return DimensionSkein().getCraftedGcode( gcodeText, repository )

def getNewRepository():
	"Get the repository constructor."
	return DimensionRepository()

def writeOutput( fileName = ''):
	"Dimension a gcode file."
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified(fileName)
	if fileName != '':
		skeinforge_craft.writeChainTextWithNounMessage( fileName, 'dimension')


class DimensionRepository:
	"A class to handle the dimension settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository('skeinforge_application.skeinforge_plugins.craft_plugins.dimension.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Dimension', self, '')
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute('http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Dimension')
		self.activateDimension = settings.BooleanSetting().getFromValue('Activate Dimension', self, False )
		extrusionDistanceFormatLatentStringVar = settings.LatentStringVar()
		self.extrusionDistanceFormatChoiceLabel = settings.LabelDisplay().getFromName('Extrusion Distance Format Choice: ', self )
		settings.Radio().getFromRadio( extrusionDistanceFormatLatentStringVar, 'Absolute Extrusion Distance', self, True )
		self.relativeExtrusionDistance = settings.Radio().getFromRadio( extrusionDistanceFormatLatentStringVar, 'Relative Extrusion Distance', self, False )
		self.extruderRetractionSpeed = settings.FloatSpin().getFromValue( 4.0, 'Extruder Retraction Speed (mm/s):', self, 34.0, 13.3 )
		self.retractionDistance = settings.FloatSpin().getFromValue( 0.0, 'Retraction Distance (millimeters):', self, 100.0, 0.0 )
		self.restartExtraDistance = settings.FloatSpin().getFromValue( 0.0, 'Restart Extra Distance (millimeters):', self, 100.0, 0.0 )
		self.executeTitle = 'Dimension'

	def execute(self):
		"Dimension button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput(fileName)


class DimensionSkein:
	"A class to dimension a skein of extrusions."
	def __init__(self):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.feedRateMinute = None
		self.isExtruderActive = False
		self.lineIndex = 0
		self.oldLocation = None
		self.operatingFlowRate = None
		self.totalExtrusionDistance = 0.0

	def addLinearMoveExtrusionDistanceLine( self, extrusionDistance ):
		"Get the extrusion distance string from the extrusion distance."
		self.distanceFeedRate.output.write('G1 F%s\n' % self.extruderRetractionSpeedMinuteString )
		self.distanceFeedRate.output.write('G1%s\n' % self.getExtrusionDistanceStringFromExtrusionDistance( extrusionDistance ) )
		self.distanceFeedRate.output.write('G1 F%s\n' % self.distanceFeedRate.getRounded( self.feedRateMinute ) )

	def getCraftedGcode( self, gcodeText, repository ):
		"Parse gcode text and store the dimension gcode."
		self.repository = repository
		self.lines = gcodec.getTextLines(gcodeText)
		self.parseInitialization()
		if self.operatingFlowRate == None:
			print('There is no operatingFlowRate so dimension will do nothing.')
			return gcodeText
		self.restartDistance = self.repository.retractionDistance.value + self.repository.restartExtraDistance.value
		self.extruderRetractionSpeedMinuteString = self.distanceFeedRate.getRounded( 60.0 * self.repository.extruderRetractionSpeed.value )
		for lineIndex in xrange( self.lineIndex, len( self.lines ) ):
			self.parseLine( lineIndex )
		return self.distanceFeedRate.output.getvalue()

	def getDimensionedArcMovement( self, line, splitLine ):
		"Get a dimensioned arc movement."
		if self.oldLocation == None:
			return line
		relativeLocation = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
		location = self.oldLocation + relativeLocation
		self.oldLocation = location
		halfPlaneLineDistance = 0.5 * abs( relativeLocation.dropAxis(2) )
		radius = gcodec.getDoubleFromCharacterSplitLine('R', splitLine )
		if radius == None:
			relativeCenter = complex( gcodec.getDoubleFromCharacterSplitLine('I', splitLine ), gcodec.getDoubleFromCharacterSplitLine('J', splitLine ) )
			radius = abs( relativeCenter )
		angle = 0.0
		if radius > 0.0:
			angle = math.pi
			if halfPlaneLineDistance < radius:
				angle = 2.0 * math.asin( halfPlaneLineDistance / radius )
			else:
				angle *= halfPlaneLineDistance / radius
		deltaZ = abs( relativeLocation.z )
		arcDistanceZ = complex( abs(angle) * radius, relativeLocation.z )
		distance = abs( arcDistanceZ )
		return line + self.getExtrusionDistanceString( distance, splitLine )

	def getDimensionedLinearMovement( self, line, splitLine ):
		"Get a dimensioned linear movement."
		distance = 0.0
		if self.distanceFeedRate.absoluteDistanceMode:
			location = gcodec.getLocationFromSplitLine(self.oldLocation, splitLine)
			if self.oldLocation != None:
				distance = abs( location - self.oldLocation )
			self.oldLocation = location
		else:
			if self.oldLocation == None:
				print('Warning: There was no absolute location when the G91 command was parsed, so the absolute location will be set to the origin.')
				self.oldLocation = Vector3()
			location = gcodec.getLocationFromSplitLine(None, splitLine)
			distance = abs( location )
			self.oldLocation += location
		return line + self.getExtrusionDistanceString( distance, splitLine )

	def getExtrusionDistanceString( self, distance, splitLine ):
		"Get the extrusion distance string."
		self.feedRateMinute = gcodec.getFeedRateMinute( self.feedRateMinute, splitLine )
		if not self.isExtruderActive:
			return ''
		if distance <= 0.0:
			return ''
		return self.getExtrusionDistanceStringFromExtrusionDistance( self.flowRate * 60.0 / self.feedRateMinute * distance )

	def getExtrusionDistanceStringFromExtrusionDistance( self, extrusionDistance ):
		"Get the extrusion distance string from the extrusion distance."
		if self.repository.relativeExtrusionDistance.value:
			return ' E' + self.distanceFeedRate.getRounded( extrusionDistance )
		self.totalExtrusionDistance += extrusionDistance
		return ' E' + self.distanceFeedRate.getRounded( self.totalExtrusionDistance )

	def parseInitialization(self):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine('(<procedureDone> dimension </procedureDone>)')
				return
			elif firstWord == '(<operatingFeedRatePerSecond>':
				self.feedRateMinute = 60.0 * float(splitLine[1])
			elif firstWord == '(<operatingFlowRate>':
				self.operatingFlowRate = float(splitLine[1])
				self.flowRate = self.operatingFlowRate
			self.distanceFeedRate.addLine(line)

	def parseLine( self, lineIndex ):
		"Parse a gcode line and add it to the dimension skein."
		line = self.lines[lineIndex].lstrip()
		splitLine = line.split()
		if len(splitLine) < 1:
			return
		firstWord = splitLine[0]
		if firstWord == 'G2' or firstWord == 'G3':
			line = self.getDimensionedArcMovement( line, splitLine )
		if firstWord == 'G1':
			line = self.getDimensionedLinearMovement( line, splitLine )
		elif firstWord == 'M101':
			self.addLinearMoveExtrusionDistanceLine( self.restartDistance )
			if not self.repository.relativeExtrusionDistance.value:
				self.distanceFeedRate.addLine('G92 E0')
				self.totalExtrusionDistance = 0.0
			self.isExtruderActive = True
		elif firstWord == 'M103':
			self.addLinearMoveExtrusionDistanceLine( - self.repository.retractionDistance.value )
			self.isExtruderActive = False
		elif firstWord == 'M108':
			self.flowRate = float( splitLine[1][1 :] )
		self.distanceFeedRate.addLine(line)


def main():
	"Display the dimension dialog."
	if len( sys.argv ) > 1:
		writeOutput(' '.join( sys.argv[1 :] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
