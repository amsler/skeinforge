"""
Skeinview is a script to display each layer of a gcode file.

Skeinview is derived from Nophead's preview script.  The extruded lines are in the resistor colors red, orange, yellow, green, blue, purple & brown.  When the extruder is off, the travel line is grey.  Skeinview is useful for a detailed view of the extrusion, behold is better to see the orientation of the shape.  To get an initial overview of the skein, when the skeinview display window appears, click the Soar button (double right arrow button beside the layer field).

The default 'Activate Skeinview' checkbox is on.  When it is on, the functions described below will work when called from the skeinforge toolchain, when it is off, the functions will not be called from the toolchain.  The functions will still be called, whether or not the 'Activate Skeinview' checkbox is on, when skeinview is run directly.  Skeinview has trouble separating the layers when it reads gcode without comments.

If 'Draw Arrows' is selected, arrows will be drawn at the end of each line segment, the default is on.  If 'Go Around Extruder Off Travel' is selected, the display will include the travel when the extruder is off, which means it will include the nozzle wipe path if any.

The scale setting is the scale of the image in pixels per millimeter, the higher the number, the greater the size of the display.  The "Screen Horizontal Inset" determines how much the display will be inset in the horizontal direction from the edge of screen, the higher the number the more it will be inset and the smaller it will be, the default is one hundred.  The "Screen Vertical Inset" determines how much the display will be inset in the vertical direction from the edge of screen, the default is fifty.

When the submenu in the export menu item in the file menu is clicked, an export canvas dialog will be displayed, which can export the canvas to a file.

The mouse tool can be changed from the 'Mouse Mode' menu button or picture button.  The 'Display Line' tool will display the line index of the line clicked, counting from one, and the line itself.  The 'View Move' tool will move the viewpoint in the xy plane when the mouse is clicked and dragged on the canvas.  The mouse tools listen to the arrow keys when the canvas has the focus.  Clicking in the canvas gives the canvas the focus, and when the canvas has the focus a thick black border is drawn around the canvas.

On the display window, the layer spin box up button increases the 'Layer' by one, and the down button decreases the layer index by one.  When the layer displayed in the layer field is changed then <Return> is hit, the layer shown will be set to the layer field, to a mimimum of zero and to a maximum of the highest index layer.  The layer can also be changed from the skeinview dialog.  The Soar button increases the layer at the 'Animation Slide Show Rate', and the Dive (double left arrow button beside the layer field) button decreases the layer at the slide show rate.

Also on the display window, there is the line spin box, which is the index of the selected line on the layer.  The line spin box up button increases the 'Line' by one.  If the line index of the layer goes over the index of the last line, the layer index will be increased by one and the new line index will be zero.  The down button decreases the line index by one.  If the line index goes below the index of the first line, the layer index will be decreased by one and the new line index will be at the last line.  When the line displayed in the line field is changed then <Return> is hit, the line shown will be set to the line field, to a mimimum of zero and to a maximum of the highest index line.  The line can also be changed from the skeinview dialog.  The Soar button increases the line at the speed at which the extruder would move, times the 'Animation Line Quickening' ratio, and the Dive (double left arrow button beside the line field) button decreases the line at the line quickening ratio.

The "Width of Extrusion Thread" sets the width of the extrusion thread, the default is two.  The "Width of Selection Thread" sets the width of the selected line, the default is six.  The "Width of Travel Thread" sets the width of the grey extruder off travel threads, the default is one.

The zoom in mouse tool will zoom in the display at the point where the mouse was clicked, increasing the scale by a factor of two.  The zoom out tool will zoom out the display at the point where the mouse was clicked, decreasing the scale by a factor of two.

The dive, soar and zoom icons are from Mark James' soarSilk icon set 1.3 at:
http://www.famfamfam.com/lab/icons/silk/

An explanation of the gcodes is at:
http://reprap.org/bin/view/Main/Arduino_GCode_Interpreter

and at:
http://reprap.org/bin/view/Main/MCodeReference

A gode example is at:
http://forums.reprap.org/file.php?12,file=565

This example displays a skein view for the gcode file Screw Holder.gcode.  This example is run in a terminal in the folder which contains Screw Holder.gcode and skeinview.py.


> python skeinview.py
This brings up the skeinview dialog.


> python skeinview.py Screw Holder.gcode
This brings up a skein window to view each layer of a gcode file.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import skeinview
>>> skeinview.main()
This brings up the skeinview dialog.


>>> skeinview.displayFile()
This brings up a skein window to view each layer of a gcode file.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.analyze_plugins.analyze_utilities import display_line
from skeinforge_tools.analyze_plugins.analyze_utilities import tableau
from skeinforge_tools.analyze_plugins.analyze_utilities import view_move
from skeinforge_tools.skeinforge_utilities.vector3 import Vector3
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import preferences
from skeinforge_tools.meta_plugins import polyfile
import math
import os
import sys

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def displayFile( fileName ):
	"Display a gcode file in a skeinview window."
	gcodeText = gcodec.getFileText( fileName )
	displayFileGivenText( fileName, gcodeText )

def displayFileGivenText( fileName, gcodeText, skeinviewRepository = None ):
	"Display a gcode file in a skeinview window given the text."
	if gcodeText == '':
		return
	if skeinviewRepository == None:
		skeinviewRepository = SkeinviewRepository()
		preferences.getReadRepository( skeinviewRepository )
	skeinWindow = getWindowGivenTextRepository( fileName, gcodeText, skeinviewRepository )
	skeinWindow.updateDeiconify()

def getGeometricDifference( first, second ):
	"Get the geometric difference of the two numbers."
	return max( first, second ) / min( first, second )

def getNewRepository():
	"Get the repository constructor."
	return SkeinviewRepository()

def getRankIndex( rulingSeparationWidthMillimeters, screenOrdinate ):
	"Get rank index."
	return int( round( screenOrdinate / rulingSeparationWidthMillimeters ) )

def getWindowGivenTextRepository( fileName, gcodeText, skeinviewRepository ):
	"Display a gcode file in a skeinview window given the text and preferences."
	skein = SkeinviewSkein()
	skein.parseGcode( fileName, gcodeText, skeinviewRepository )
	return SkeinWindow( skeinviewRepository, skein )

def writeOutput( fileName, gcodeText = '' ):
	"Display a skeinviewed gcode file for a skeinforge gcode file, if 'Activate Skeinview' is selected."
	skeinviewRepository = SkeinviewRepository()
	preferences.getReadRepository( skeinviewRepository )
	if skeinviewRepository.activateSkeinview.value:
		gcodeText = gcodec.getTextIfEmpty( fileName, gcodeText )
		displayFileGivenText( fileName, gcodeText, skeinviewRepository )


class SkeinviewRepository( tableau.TableauRepository ):
	"A class to handle the skeinview preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		preferences.addListsToRepository( 'skeinforge_tools.analyze_plugins.skeinview.html', '', self )
		self.initializeUpdateFunctionsToNone()
		self.fileNameInput = preferences.FileNameInput().getFromFileName( [ ( 'Gcode text files', '*.gcode' ) ], 'Open File to Skeinview', self, '' )
		self.activateSkeinview = preferences.BooleanPreference().getFromValue( 'Activate Skeinview', self, True )
		self.addAnimation()
		self.drawArrows = preferences.BooleanPreference().getFromValue( 'Draw Arrows', self, True )
		self.drawArrows.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.goAroundExtruderOffTravel = preferences.BooleanPreference().getFromValue( 'Go Around Extruder Off Travel', self, False )
		self.goAroundExtruderOffTravel.setUpdateFunction( self.setToDisplaySavePhoenixUpdate )
		self.layer = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Layer (index):', self, 912345678, 0 )
		self.layer.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.line = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Line (index):', self, 912345678, 0 )
		self.line.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.mouseMode = preferences.MenuButtonDisplay().getFromName( 'Mouse Mode:', self )
		self.displayLine = preferences.MenuRadio().getFromMenuButtonDisplay( self.mouseMode, 'Display Line', self, True )
		self.setNewMouseToolUpdate( display_line.getNewMouseTool, self.displayLine )
		self.viewMove = preferences.MenuRadio().getFromMenuButtonDisplay( self.mouseMode, 'View Move', self, False )
		self.setNewMouseToolUpdate( view_move.getNewMouseTool, self.viewMove )
		self.addScaleScreenSlide()
		self.widthOfExtrusionThread = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Width of Extrusion Thread (pixels):', self, 5, 2 )
		self.widthOfExtrusionThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfSelectionThread = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Width of Selection Thread (pixels):', self, 10, 6 )
		self.widthOfSelectionThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfTravelThread = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Width of Travel Thread (pixels):', self, 5, 1 )
		self.widthOfTravelThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.executeTitle = 'Skeinview'

	def execute( self ):
		"Write button has been clicked."
		fileNames = polyfile.getFileOrGcodeDirectory( self.fileNameInput.value, self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			displayFile( fileName )


class SkeinviewSkein:
	"A class to write a get a scalable vector graphics text for a gcode skein."
	def __init__( self ):
		self.extrusionNumber = 0
		self.feedRateMinute = 960.1
		self.isThereALayerStartWord = False
		self.oldZ = - 999999999999.0
		self.skeinPane = None
		self.skeinPanes = []

	def addToPath( self, line, location ):
		"Add a point to travel and maybe extrusion."
		if self.oldLocation == None:
			return
		colorName = 'gray'
		locationComplex = location.dropAxis( 2 )
		oldLocationComplex = self.oldLocation.dropAxis( 2 )
		begin = self.getScreenCoordinates( oldLocationComplex )
		end = self.getScreenCoordinates( locationComplex )
		if self.extruderActive:
			colorName = self.colorNames[ self.extrusionNumber % len( self.colorNames ) ]
		displayString = '%s %s' % ( self.lineIndex + 1, line )
		tagString = 'colored_line_index: %s %s' % ( len( self.skeinPane ), len( self.skeinPanes ) - 1 )
		coloredLine = tableau.ColoredLine( begin, colorName, displayString, end, tagString )
		coloredLine.isExtrusionThread = self.extruderActive
		self.skeinPane.append( coloredLine )

	def getScreenCoordinates( self, pointComplex ):
		"Get the screen coordinates.self.cornerImaginaryTotal - self.marginCornerLow"
		pointComplex = complex( pointComplex.real, self.cornerImaginaryTotal - pointComplex.imag )
		return self.scale * pointComplex - self.marginCornerLow

	def initializeActiveLocation( self ):
		"Set variables to default."
		self.extruderActive = False
		self.oldLocation = None

	def isLayerStart( self, firstWord, splitLine ):
		"Parse a gcode line and add it to the vector output."
		if self.isThereALayerStartWord:
			return firstWord == '(<layer>'
		if firstWord != 'G1' and firstWord != 'G2' and firstWord != 'G3':
			return False
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		if location.z - self.oldZ > 0.1:
			self.oldZ = location.z
			return True
		return False

	def linearCorner( self, splitLine ):
		"Update the bounding corners."
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		if self.extruderActive or self.goAroundExtruderOffTravel:
			self.cornerHigh = euclidean.getPointMaximum( self.cornerHigh, location )
			self.cornerLow = euclidean.getPointMinimum( self.cornerLow, location )
		self.oldLocation = location

	def linearMove( self, line, location ):
		"Get statistics for a linear move."
		if self.skeinPane == None:
			return
		self.addToPath( line, location )

	def parseCorner( self, line ):
		"Parse a gcode line and use the location to update the bounding corners."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == 'G1':
			self.linearCorner( splitLine )
		elif firstWord == 'M101':
			self.extruderActive = True
		elif firstWord == 'M103':
			self.extruderActive = False

	def parseGcode( self, fileName, gcodeText, skeinviewRepository ):
		"Parse gcode text and store the vector output."
		self.fileName = fileName
		self.gcodeText = gcodeText
		self.initializeActiveLocation()
		self.cornerHigh = Vector3( - 999999999.0, - 999999999.0, - 999999999.0 )
		self.cornerLow = Vector3( 999999999.0, 999999999.0, 999999999.0 )
		self.goAroundExtruderOffTravel = skeinviewRepository.goAroundExtruderOffTravel.value
		self.lines = gcodec.getTextLines( gcodeText )
		self.isThereALayerStartWord = gcodec.isThereAFirstWord( '(<layer>', self.lines, 1 )
		self.parseInitialization()
		for line in self.lines[ self.lineIndex : ]:
			self.parseCorner( line )
		self.cornerHighComplex = self.cornerHigh.dropAxis( 2 )
		self.cornerLowComplex = self.cornerLow.dropAxis( 2 )
		self.scale = skeinviewRepository.scale.value
		self.scaleCornerHigh = self.scale * self.cornerHighComplex
		self.scaleCornerLow = self.scale * self.cornerLowComplex
		self.cornerImaginaryTotal = self.cornerHigh.y + self.cornerLow.y
		self.margin = complex( 10.0, 10.0 )
		self.marginCornerHigh = self.scaleCornerHigh + self.margin
		self.marginCornerLow = self.scaleCornerLow - self.margin
		self.screenSize = self.marginCornerHigh - self.marginCornerLow
		self.initializeActiveLocation()
		self.colorNames = [ 'brown', 'red', 'orange', 'yellow', 'green', 'blue', 'purple' ]
		for self.lineIndex in xrange( self.lineIndex, len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			self.parseLine( line )

	def parseInitialization( self ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			if firstWord == '(</extruderInitialization>)':
				return
			elif firstWord == '(<operatingFeedRatePerSecond>':
				self.feedRateMinute = 60.0 * float( splitLine[ 1 ] )

	def parseLine( self, line ):
		"Parse a gcode line and add it to the vector output."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if self.isLayerStart( firstWord, splitLine ):
			self.extrusionNumber = 0
			self.skeinPane = []
			self.skeinPanes.append( self.skeinPane )
		if firstWord == 'G1':
			location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
			self.linearMove( line, location )
			self.oldLocation = location
		elif firstWord == 'M101':
			self.extruderActive = True
			self.extrusionNumber += 1
		elif firstWord == 'M103':
			self.extruderActive = False
		if firstWord == 'G2' or firstWord == 'G3':
			relativeLocation = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
			relativeLocation.z = 0.0
			location = self.oldLocation + relativeLocation
			self.linearMove( line, location )
			self.oldLocation = location


class SkeinWindow( tableau.TableauWindow ):
	def __init__( self, repository, skein ):
		"Initialize the skein window."
		self.rulingExtent = 24
		self.rulingTargetSeparation = 150.0
		self.addCanvasMenuRootScrollSkein( repository, skein, '_skeinview', 'Skeinview Viewer from Hydraraptor' )
		horizontalRulerBoundingBox = ( 0, 0, int( skein.screenSize.real ), self.rulingExtent )
		self.horizontalRulerCanvas = preferences.Tkinter.Canvas( self.root, width = self.canvasWidth, height = self.rulingExtent, scrollregion = horizontalRulerBoundingBox )
		self.horizontalRulerCanvas.grid( row = 0, column = 2, columnspan = 96, sticky = preferences.Tkinter.E + preferences.Tkinter.W )
		self.horizontalRulerCanvas[ 'xscrollcommand' ] = self.xScrollbar.set
		verticalRulerBoundingBox = ( 0, 0, self.rulingExtent, int( skein.screenSize.imag ) )
		self.verticalRulerCanvas = preferences.Tkinter.Canvas( self.root, width = self.rulingExtent, height = self.canvasHeight, scrollregion = verticalRulerBoundingBox )
		self.verticalRulerCanvas.grid( row = 1, rowspan = 97, column = 1, sticky = preferences.Tkinter.N + preferences.Tkinter.S )
		self.verticalRulerCanvas[ 'yscrollcommand' ] = self.yScrollbar.set
		self.addMouseToolsBind()
		self.createRulers()

	def addHorizontalRulerRuling( self, xMillimeters ):
		"Add a ruling to the horizontal ruler."
		xPixel = self.skein.getScreenCoordinates( complex( xMillimeters, 0.0 ) ).real
		self.horizontalRulerCanvas.create_line( xPixel, 0.0, xPixel, self.rulingExtent, fill = 'black' )
		self.horizontalRulerCanvas.create_text( xPixel + 2, 0, anchor = preferences.Tkinter.NW, text = self.getRoundedRulingText( xMillimeters ) )

	def addVerticalRulerRuling( self, yMillimeters ):
		"Add a ruling to the vertical ruler."
		fontHeight = 12
		yPixel = self.skein.getScreenCoordinates( complex( 0.0, yMillimeters ) ).imag
		self.verticalRulerCanvas.create_line( 0.0, yPixel, self.rulingExtent, yPixel, fill = 'black' )
		yPixel += 2
		roundedRulingText = self.getRoundedRulingText( yMillimeters )
		effectiveRulingTextLength = len( roundedRulingText )
		if roundedRulingText.find( '.' ) != - 1:
			effectiveRulingTextLength -= 1
		if effectiveRulingTextLength < 4:
			self.verticalRulerCanvas.create_text( 0, yPixel, anchor = preferences.Tkinter.NW, text = roundedRulingText )
			return
		for character in roundedRulingText:
			if character == '.':
				yPixel -= fontHeight * 2 / 3
			self.verticalRulerCanvas.create_text( 0, yPixel, anchor = preferences.Tkinter.NW, text = character )
			yPixel += fontHeight

	def createRulers( self ):
		"Create the rulers.."
		rankZeroSeperation = self.getRulingSeparationWidthPixels( 0 )
		zoom = self.rulingTargetSeparation / rankZeroSeperation
		rank = euclidean.getRank( zoom )
		rankTop = rank + 1
		seperationBottom = self.getRulingSeparationWidthPixels( rank )
		seperationTop = self.getRulingSeparationWidthPixels( rankTop )
		bottomDifference = getGeometricDifference( self.rulingTargetSeparation, seperationBottom )
		topDifference = getGeometricDifference( self.rulingTargetSeparation, seperationTop )
		if topDifference < bottomDifference:
			rank = rankTop
		self.rulingSeparationWidthMillimeters = euclidean.getIncrementFromRank( rank )
		rulingSeparationWidthPixels = self.getRulingSeparationWidthPixels( rank )
		marginOverScale = self.skein.margin / self.skein.scale
		cornerHighMargin = self.skein.cornerHighComplex + marginOverScale
		cornerLowMargin = self.skein.cornerLowComplex - marginOverScale
		xRankIndexHigh = getRankIndex( self.rulingSeparationWidthMillimeters, cornerHighMargin.real )
		xRankIndexLow = getRankIndex( self.rulingSeparationWidthMillimeters, cornerLowMargin.real )
		for xRankIndex in xrange( xRankIndexLow - 2, xRankIndexHigh + 2 ): # 1 is enough, 2 is to be on the safe side
			self.addHorizontalRulerRuling( xRankIndex * self.rulingSeparationWidthMillimeters )
		yRankIndexHigh = getRankIndex( self.rulingSeparationWidthMillimeters, cornerHighMargin.imag )
		yRankIndexLow = getRankIndex( self.rulingSeparationWidthMillimeters, cornerLowMargin.imag )
		for yRankIndex in xrange( yRankIndexLow - 2, yRankIndexHigh + 2 ): # 1 is enough, 2 is to be on the safe side
			self.addVerticalRulerRuling( yRankIndex * self.rulingSeparationWidthMillimeters )

	def getColoredLines( self ):
		"Get the colored lines from the skein pane."
		return self.skeinPanes[ self.repository.layer.value ]

	def getCopy( self ):
		"Get a copy of this window."
		return SkeinWindow( self.repository, self.skein )

	def getCopyWithNewSkein( self ):
		"Get a copy of this window with a new skein."
		return getWindowGivenTextRepository( self.skein.fileName, self.skein.gcodeText, self.repository )

	def getDrawnColoredLine( self, coloredLine, width ):
		"Get the drawn colored line."
		return self.canvas.create_line(
			coloredLine.begin.real,
			coloredLine.begin.imag,
			coloredLine.end.real,
			coloredLine.end.imag,
			fill = coloredLine.colorName,
			arrow = self.arrowType,
			tags = coloredLine.tagString,
			width = width )

	def getDrawnColoredLineIfThick( self, coloredLine, width ):
		"Get the drawn colored line if it has a positive thickness."
		if width > 0:
			return self.getDrawnColoredLine( coloredLine, width )

	def getRoundedRulingText( self, number ):
		"Get the rounded ruling text."
		rulingText = euclidean.getRoundedToDecimalPlacesString( 1 - math.floor( math.log10( self.rulingSeparationWidthMillimeters ) ), number )
		if self.rulingSeparationWidthMillimeters < .99:
			return rulingText
		if rulingText[ - len( '.0' ) : ] == '.0':
			return rulingText[ : - len( '.0' ) ]
		return rulingText

	def getRulingSeparationWidthPixels( self, rank ):
		"Get the separation width in pixels."
		return euclidean.getIncrementFromRank( rank ) * self.skein.scale

	def getSelectedDrawnColoredLines( self, coloredLines ):
		"Get the selected drawn colored lines."
		selectedDrawnColoredLines = []
		for coloredLine in coloredLines:
			selectedDrawnColoredLines.append( self.getDrawnColoredLine( coloredLine, self.repository.widthOfSelectionThread.value ) )
		return selectedDrawnColoredLines

	def relayXview( self, *args ):
		"Relay xview changes."
		self.canvas.xview( *args )
		self.horizontalRulerCanvas.xview( *args )

	def relayYview( self, *args ):
		"Relay yview changes."
		self.canvas.yview( *args )
		self.verticalRulerCanvas.yview( *args )

	def update( self ):
		"Update the window."
		if len( self.skeinPanes ) < 1:
			return
		self.limitIndexSetArrowMouseDeleteCanvas()
		skeinPane = self.skeinPanes[ self.repository.layer.value ]
		for coloredLine in skeinPane:
			if coloredLine.isExtrusionThread:
				self.getDrawnColoredLineIfThick( coloredLine, self.repository.widthOfExtrusionThread.value )
			else:
				self.getDrawnColoredLineIfThick( coloredLine, self.repository.widthOfTravelThread.value )
		self.setDisplayLayerIndex()


def main():
	"Display the skeinview dialog."
	if len( sys.argv ) > 1:
		displayFile( ' '.join( sys.argv[ 1 : ] ) )
	else:
		preferences.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
