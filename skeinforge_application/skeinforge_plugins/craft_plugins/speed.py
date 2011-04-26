"""
This page is in the table of contents.
Speed is a script to set the feed rate, and flow rate.

The speed manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Speed

==Operation==
The default 'Activate Speed' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.  The speed script sets the feed rate, and flow rate.

==Settings==
===Add Flow Rate===
Default is on.

When selected, the flow rate will be added to the gcode.

===Bridge===
====Bridge Feed Rate Multiplier====
Default is one.

Defines the ratio of the feed rate on the bridge layers over the feed rate of the typical non bridge layers.

====Bridge Flow Rate Multiplier====
Default is one.

Defines the ratio of the flow rate on the bridge layers over the flow rate of the typical non bridge layers.

===Duty Cyle===
====Duty Cyle at Beginning====
Default is one, which will set the extruder motor to full current.

Defines the duty cycle of the stepper motor pulse width modulation by adding an M113 command toward the beginning of the gcode text.  If the hardware has the option of using a potentiometer to set the duty cycle, to select the potentiometer option set 'Duty Cyle at Beginning' to an empty string.  To turn off the extruder, set the 'Duty Cyle at Beginning' to zero.

====Duty Cyle at Ending====
Default is zero, which will turn off the extruder motor.

Defines the duty cycle of the stepper motor pulse width modulation by adding an M113 command toward the ending of the gcode text.  If the hardware has the option of using a potentiometer to set the duty cycle, to select the potentiometer option set 'Duty Cyle at Beginning' to an empty string.  To turn off the extruder, set the 'Duty Cyle at Ending' to zero.

===Feed Rate===
Default is sixteen millimeters per second.

Defines the operating feed rate.

===Flow Rate Setting===
Default is 210.

Defines the operating flow rate.

===Orbital Feed Rate over Operating Feed Rate===
Default is 0.5.

Defines the speed of the orbit compared to the operating extruder speed.  If you want the orbit to be very short, set the "Orbital Feed Rate over Operating Feed Rate" setting to a low value like 0.1.

===Perimeter===
To have higher build quality on the outside at the expense of slower build speed, a typical setting for the 'Perimeter Feed Rate over Operating Feed Rate' would be 0.5.  To go along with that, if you are using a speed controlled extruder, the 'Perimeter Flow Rate over Operating Flow Rate' should also be 0.5.  If you are using Pulse Width Modulation to control the speed, then you'll probably need a slightly higher ratio because there is a minimum voltage 'Flow Rate PWM Setting' required for the extruder motor to turn.  The flow rate PWM ratio would be determined by trial and error, with the first trial being:
Perimeter Flow Rate over Operating Flow Rate ~ Perimeter Feed Rate over Operating Feed Rate * ( Flow Rate PWM Setting - Minimum Flow Rate PWM Setting ) + Minimum Flow Rate PWM Setting

====Perimeter Feed Rate over Operating Feed Rate====
Default is one.

Defines the ratio of the feed rate of the perimeter over the feed rate of the infill.

====Perimeter Flow Rate over Operating Feed Rate====
Default is one.

Defines the ratio of the flow rate of the perimeter over the flow rate of the infill.

===Travel Feed Rate===
Default is sixteen millimeters per second.

Defines the feed rate when the extruder is off.  The 'Travel Feed Rate' could be set as high as the extruder can be moved, it is not limited by the maximum extrusion rate.

==Examples==
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


>>> speed.writeOutput('Screw Holder Bottom.stl')
The speed tool is parsing the file:
Screw Holder Bottom.stl
..
The speed tool has created the file:
.. Screw Holder Bottom_speed.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities import archive
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import intercircle
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_craft
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
from skeinforge_application.skeinforge_utilities import skeinforge_profile
import math
import sys


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = '$Date: 2008/21/04 $'
__license__ = 'GPL 3.0'


def getCraftedText( fileName, text = '', repository=None):
	"Speed the file or text."
	return getCraftedTextFromText( archive.getTextIfEmpty( fileName, text ), repository )

def getCraftedTextFromText(gcodeText, repository=None):
	"Speed a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'speed'):
		return gcodeText
	if repository == None:
		repository = settings.getReadRepository( SpeedRepository() )
	if not repository.activateSpeed.value:
		return gcodeText
	return SpeedSkein().getCraftedGcode(gcodeText, repository)

def getNewRepository():
	"Get the repository constructor."
	return SpeedRepository()

def writeOutput(fileName=''):
	"Speed a gcode linear move file."
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified(fileName)
	if fileName != '':
		skeinforge_craft.writeChainTextWithNounMessage( fileName, 'speed')


class SpeedRepository:
	"A class to handle the speed settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository('skeinforge_application.skeinforge_plugins.craft_plugins.speed.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Speed', self, '')
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute('http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Speed')
		self.activateSpeed = settings.BooleanSetting().getFromValue('Activate Speed:', self, True )
		self.addFlowRate = settings.BooleanSetting().getFromValue('Add Flow Rate:', self, True )
		settings.LabelSeparator().getFromRepository(self)
		settings.LabelDisplay().getFromName('- Bridge -', self )
		self.bridgeFeedRateMultiplier = settings.FloatSpin().getFromValue( 0.8, 'Bridge Feed Rate Multiplier (ratio):', self, 1.2, 1.0 )
		self.bridgeFlowRateMultiplier = settings.FloatSpin().getFromValue( 0.8, 'Bridge Flow Rate Multiplier (ratio):', self, 1.2, 1.0 )
		settings.LabelSeparator().getFromRepository(self)
		settings.LabelDisplay().getFromName('- Duty Cyle -', self )
		self.dutyCycleAtBeginning = settings.FloatSpin().getFromValue( 0.0, 'Duty Cyle at Beginning (portion):', self, 1.0, 1.0 )
		self.dutyCycleAtEnding = settings.FloatSpin().getFromValue( 0.0, 'Duty Cyle at Ending (portion):', self, 1.0, 0.0 )
		settings.LabelSeparator().getFromRepository(self)
		self.feedRatePerSecond = settings.FloatSpin().getFromValue( 2.0, 'Feed Rate (mm/s):', self, 50.0, 16.0 )
		self.flowRateSetting = settings.FloatSpin().getFromValue( 50.0, 'Flow Rate Setting (float):', self, 250.0, 210.0 )
		self.orbitalFeedRateOverOperatingFeedRate = settings.FloatSpin().getFromValue( 0.1, 'Orbital Feed Rate over Operating Feed Rate (ratio):', self, 0.9, 0.5 )
		settings.LabelSeparator().getFromRepository(self)
		settings.LabelDisplay().getFromName('- Perimeter -', self )
		self.perimeterFeedRateOverOperatingFeedRate = settings.FloatSpin().getFromValue( 0.5, 'Perimeter Feed Rate over Operating Feed Rate (ratio):', self, 1.0, 1.0 )
		self.perimeterFlowRateOverOperatingFlowRate = settings.FloatSpin().getFromValue( 0.5, 'Perimeter Flow Rate over Operating Flow Rate (ratio):', self, 1.0, 1.0 )
		settings.LabelSeparator().getFromRepository(self)
		self.travelFeedRatePerSecond = settings.FloatSpin().getFromValue( 2.0, 'Travel Feed Rate (mm/s):', self, 50.0, 16.0 )
		self.executeTitle = 'Speed'

	def execute(self):
		"Speed button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode(self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled)
		for fileName in fileNames:
			writeOutput(fileName)


class SpeedSkein:
	"A class to speed a skein of extrusions."
	def __init__(self):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.feedRatePerSecond = 16.0
		self.isExtruderActive = False
		self.isBridgeLayer = False
		self.isPerimeter = False
		self.lineIndex = 0
		self.lines = None
		self.oldFlowRateString = None

	def addFlowRateLineIfNecessary(self):
		"Add flow rate line."
		flowRateString = self.getFlowRateString()
		if flowRateString != self.oldFlowRateString:
			self.distanceFeedRate.addLine('M108 S' + flowRateString )
		self.oldFlowRateString = flowRateString

	def addParameterString( self, firstWord, parameterWord ):
		"Add parameter string."
		if parameterWord == '':
			self.distanceFeedRate.addLine(firstWord)
			return
		self.distanceFeedRate.addParameter( firstWord, parameterWord )

	def getCraftedGcode(self, gcodeText, repository):
		"Parse gcode text and store the speed gcode."
		self.repository = repository
		self.feedRatePerSecond = repository.feedRatePerSecond.value
		self.travelFeedRatePerMinute = 60.0 * self.repository.travelFeedRatePerSecond.value
		self.lines = archive.getTextLines(gcodeText)
		self.parseInitialization()
		for line in self.lines[self.lineIndex :]:
			self.parseLine(line)
		self.addParameterString('M113', self.repository.dutyCycleAtEnding.value ) # Set duty cycle .
		return self.distanceFeedRate.output.getvalue()

	def getFlowRateString(self):
		"Get the flow rate string."
		if not self.repository.addFlowRate.value:
			return None
		flowRate = self.repository.flowRateSetting.value
		if self.isBridgeLayer:
			flowRate *= self.repository.bridgeFlowRateMultiplier.value
		if self.isPerimeter:
			flowRate *= self.repository.perimeterFlowRateOverOperatingFlowRate.value
		return euclidean.getFourSignificantFigures( flowRate )

	def getSpeededLine(self, line, splitLine):
		"Get gcode line with feed rate."
		if gcodec.indexOfStartingWithSecond('F', splitLine) > 0:
			return line
		feedRateMinute = 60.0 * self.feedRatePerSecond
		if self.isBridgeLayer:
			feedRateMinute *= self.repository.bridgeFeedRateMultiplier.value
		if self.isPerimeter:
			feedRateMinute *= self.repository.perimeterFeedRateOverOperatingFeedRate.value
		self.addFlowRateLineIfNecessary()
		if not self.isExtruderActive:
			feedRateMinute = self.travelFeedRatePerMinute
		return line + ' ' + self.distanceFeedRate.getRounded(feedRateMinute)

	def parseInitialization(self):
		'Parse gcode initialization and store the parameters.'
		for self.lineIndex in xrange(len(self.lines)):
			line = self.lines[self.lineIndex]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord(splitLine)
			self.distanceFeedRate.parseSplitLine(firstWord, splitLine)
			if firstWord == '(<layerThickness>':
				self.layerThickness = float(splitLine[1])
			elif firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine('(<procedureDone> speed </procedureDone>)')
				return
			elif firstWord == '(<perimeterWidth>':
				self.absolutePerimeterWidth = abs(float(splitLine[1]))
				self.distanceFeedRate.addTagBracketedLine('operatingFeedRatePerSecond', self.feedRatePerSecond )
				if self.repository.addFlowRate.value:
					self.distanceFeedRate.addTagBracketedLine('operatingFlowRate', self.repository.flowRateSetting.value )
				orbitalFeedRatePerSecond = self.feedRatePerSecond * self.repository.orbitalFeedRateOverOperatingFeedRate.value
				self.distanceFeedRate.addTagBracketedLine('orbitalFeedRatePerSecond', orbitalFeedRatePerSecond )
				self.distanceFeedRate.addTagBracketedLine('travelFeedRatePerSecond', self.repository.travelFeedRatePerSecond.value )
			self.distanceFeedRate.addLine(line)

	def parseLine(self, line):
		"Parse a gcode line and add it to the speed skein."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
		if len(splitLine) < 1:
			return
		firstWord = splitLine[0]
		if firstWord == '(<extrusion>)':
			self.distanceFeedRate.addLine(line)
			self.addParameterString('M113', self.repository.dutyCycleAtBeginning.value ) # Set duty cycle .
			return
		elif firstWord == 'G1':
			line = self.getSpeededLine(line, splitLine)
		elif firstWord == 'M101':
			self.isExtruderActive = True
		elif firstWord == 'M103':
			self.isPerimeter = False
			self.isExtruderActive = False
		elif firstWord == '(<bridgeRotation>':
			self.isBridgeLayer = True
		elif firstWord == '(<layer>':
			self.isBridgeLayer = False
			self.addFlowRateLineIfNecessary()
		elif firstWord == '(<perimeter>':
			self.isPerimeter = True
		self.distanceFeedRate.addLine(line)


def main():
	"Display the speed dialog."
	if len(sys.argv) > 1:
		writeOutput(' '.join(sys.argv[1 :]))
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
