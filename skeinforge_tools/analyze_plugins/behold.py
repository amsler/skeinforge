"""
This page is in the table of contents.
Behold is an analysis script to display a gcode file in an isometric view.

The behold manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Behold

==Operation==
The default 'Activate Behold' checkbox is on.  When it is on, the functions described below will work when called from the skeinforge toolchain, when it is off, the functions will not be called from the toolchain.  The functions will still be called, whether or not the 'Activate Behold' checkbox is on, when behold is run directly.  Behold can not separate the layers when it reads gcode without comments.

The viewer is simple, the viewpoint can only be moved in a sphere around the center of the model by changing the viewpoint latitude and longitude.  Different regions of the model can be hidden by setting the width of the thread to zero.  The alternating bands act as contour bands and their brightness and width can be changed.  The layers will be displayed starting at the "Layers From" index up until the "Layers To" index.  All of the settings can be set in the initial "Behold Settings" window and some can be changed after the viewer is running in the "Behold Dynamic Settings" window.  In the viewer, dragging the mouse will change the viewpoint.

==Settings==

===Animation===

====Animation Line Quickening====
Default is one.

The quickness of the tool animation over the quickness of the actual tool.

====Animation Slide Show Rate====
Default is two layers per second.

The rate, in layers per second, at which the layer changes when the soar or dive button is pressed..

===Banding===

====Band Height====
Default is five layers.

Defines the height of the band in layers, a pair of bands is twice that height.

====Bottom Band Brightness====
Default is 0.7.

Defines the ratio of the brightness of the bottom band over the brightness of the top band.  The higher it is the brighter the bottom band will be.

====Bottom Layer Brightness====
Default is one.

Defines the ratio of the brightness of the bottom layer over the brightness of the top layer.  With a low bottom layer brightness ratio the bottom of the model will be darker than the top of the model, as if it was being illuminated by a light just above the top.

====Bright Band Start====
Default choice is 'From the Top'.

The button group that determines where the bright band starts from.

=====From the Bottom=====

When selected, the bright bands will start from the bottom.

=====From the Top=====

When selected, the bright bands will start from the top.

===Draw Arrows===
Default is on.

When selected, arrows will be drawn at the end of each line segment.

===Export Menu===

When the submenu in the export menu item in the file menu is clicked, an export canvas dialog will be displayed, which can export the canvas to a file.

===Go Around Extruder Off Travel===
Default is off.

When selected, the display will include the travel when the extruder is off, which means it will include the nozzle wipe path if any.

===Layers===

====Layer====
Default is a huge number, which will be limited to the highest index layer.

On the display window, the Up button increases the 'Layer' by one, and the Down button decreases the layer by one.  When the layer displayed in the layer spin box is changed then <Return> is hit, the layer shown will be set to the spin box, to a mimimum of zero and to a maximum of the highest index layer.The Soar button increases the layer at the 'Animation Slide Show Rate', and the Dive (double left arrow button beside the layer field) button decreases the layer at the slide show rate.

====Layers From====
Default is zero.

The layers displayed will start from the minimum of the "Layers From" setting and the layer.

====Layers To====
Default is zero.

The layers displayed will go until the maximum of the 'Layers To' setting and the layer.  If the layer to setting is a huge number like the 912345678, the display will go to the top of the model.

===Line===
Default is zero.

The index of the selected line on the layer that is highlighted when the 'Display Line' mouse tool is chosen.  The line spin box up button increases the 'Line' by one.  If the line index of the layer goes over the index of the last line, the layer index will be increased by one and the new line index will be zero.  The down button decreases the line index by one.  If the line index goes below the index of the first line, the layer index will be decreased by one and the new line index will be at the last line.  When the line displayed in the line field is changed then <Return> is hit, the line shown will be set to the line field, to a mimimum of zero and to a maximum of the highest index line.  The Soar button increases the line at the speed at which the extruder would move, times the 'Animation Line Quickening' ratio, and the Dive (double left arrow button beside the line field) button decreases the line at the animation line quickening ratio.

===Mouse Mode===
Default is 'Display Line'.

The mouse tool can be changed from the 'Mouse Mode' menu button or picture button.  The mouse tools listen to the arrow keys when the canvas has the focus.  Clicking in the canvas gives the canvas the focus, and when the canvas has the focus a thick black border is drawn around the canvas.

====Display Line====
The 'Display Line' tool will display the highlight the selected line, and display the file line count, counting from one, and the gcode line itself.  When the 'Display Line' tool is active, clicking the canvas will select the nearest line to the mouse click.

====Viewpoint Move====
The 'Viewpoint Move' tool will move the viewpoint in the xy plane when the mouse is clicked and dragged on the canvas.

====Viewpoint Rotate====
The 'Viewpoint Rotate' tool will rotate the viewpoint around the origin, when the mouse is clicked and dragged on the canvas, or the arrow keys have been used and <Return> is pressed.  The viewpoint can also be moved by dragging the mouse.  The viewpoint latitude will be increased when the mouse is dragged from the center towards the edge.  The viewpoint longitude will be changed by the amount around the center the mouse is dragged.  This is not very intuitive, but I don't know how to do this the intuitive way and I have other stuff to develop.  If the shift key is pressed; if the latitude is changed more than the longitude, only the latitude will be changed, if the longitude is changed more only the longitude will be changed.

===Number of Fill Bottom Layers===
Default is one.

The "Number of Fill Bottom Layers" is the number of layers at the bottom which will be colored olive.

===Number of Fill Top Layers===
Default is one.

The "Number of Fill Top Layers" is the number of layers at the top which will be colored blue.

===Scale===
Default is ten.

The scale setting is the scale of the image in pixels per millimeter, the higher the number, the greater the size of the display.

The zoom in mouse tool will zoom in the display at the point where the mouse was clicked, increasing the scale by a factor of two.  The zoom out tool will zoom out the display at the point where the mouse was clicked, decreasing the scale by a factor of two.

===Screen Inset===

====Screen Horizontal Inset====
Default is one hundred.

The "Screen Horizontal Inset" determines how much the canvas will be inset in the horizontal direction from the edge of screen, the higher the number the more it will be inset and the smaller it will be.

====Screen Vertical Inset====
Default is two hundred.

The "Screen Vertical Inset" determines how much the canvas will be inset in the vertical direction from the edge of screen.

===Viewpoint Latitude===
Default is fifteen degrees.

The "Viewpoint Latitude" is the latitude of the viewpoint, a latitude of zero is the top pole giving a top view, a latitude of ninety gives a side view and a latitude of 180 gives a bottom view.

===Viewpoint Longitude===
Default is 210 degrees.

The "Viewpoint Longitude" is the longitude of the viewpoint.

===Width===
The width of each type of thread and of each axis can be changed.  If the width is set to zero, the thread will not be visible.

====Width of Infill Thread====
Default is one.

The "Width of Infill Thread" sets the width of the green extrusion threads, those threads which are not loops and not part of the raft.

====Width of Fill Bottom Thread====
Default is three.

The "Width of Fill Bottom Thread" sets the width of the olive extrusion threads at the bottom of the model.

====Width of Fill Top Thread====
Default is three.

The "Width of Fill Top Thread" sets the width of the blue extrusion threads at the top of the model.

====Width of Loop Thread====
Default is three.

The "Width of Loop Thread" sets the width of the yellow loop threads, which are not perimeters.

====Width of Perimeter Inside Thread====
Default is eight.

The "Width of Perimeter Inside Thread" sets the width of the orange inside perimeter threads.

====Width of Perimeter Outside Thread====
Default is eight.

The "Width of Perimeter Outside Thread" sets the width of the red outside perimeter threads.

====Width of Raft Thread====
Default is one.

The "Width of Raft Thread" sets the width of the brown raft threads.

====Width of Selection Thread====
Default is six.

The "Width of Selection Thread" sets the width of the selected line.

====Width of Travel Thread====
Default is zero.

The "Width of Travel Thread" sets the width of the grey extruder off travel threads.

====Width of X Axis====
Default is five.

The "Width of X Axis" setting sets the width of the dark orange X Axis.

====Width of Y Axis====
Default is five.

The "Width of Y Axis" sets the width of the gold Y Axis.

====Width of Z Axis====
Default is five.

The "Width of Z Axis" sets the width of the sky blue Z Axis.

==Icons==

The dive, soar and zoom icons are from Mark James' soarSilk icon set 1.3 at:
http://www.famfamfam.com/lab/icons/silk/

==Gcodes==

An explanation of the gcodes is at:
http://reprap.org/bin/view/Main/Arduino_GCode_Interpreter

and at:
http://reprap.org/bin/view/Main/MCodeReference

A gode example is at:
http://forums.reprap.org/file.php?12,file=565

==Examples==

Below are examples of behold being used.  These examples are run in a terminal in the folder which contains Screw Holder_penultimate.gcode and behold.py.


> python behold.py
This brings up the behold dialog.


> python behold.py Screw Holder_penultimate.gcode
This brings up the behold viewer to view the gcode file.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import behold
>>> behold.main()
This brings up the behold dialog.


>>> behold.analyzeFile( 'Screw Holder_penultimate.gcode' )
This brings up the behold viewer to view the gcode file.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.analyze_plugins.analyze_utilities import display_line
from skeinforge_tools.analyze_plugins.analyze_utilities import tableau
from skeinforge_tools.analyze_plugins.analyze_utilities import view_move
from skeinforge_tools.analyze_plugins.analyze_utilities import view_rotate
from skeinforge_tools.skeinforge_utilities.vector3 import Vector3
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import settings
from skeinforge_tools.meta_plugins import polyfile
import math
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def analyzeFile( fileName ):
	"Behold a gcode file."
	gcodeText = gcodec.getFileText( fileName )
	analyzeFileGivenText( fileName, gcodeText )

def analyzeFileGivenText( fileName, gcodeText, repository = None ):
	"Display a beholded gcode file for a gcode file."
	if gcodeText == '':
		return ''
	if repository == None:
		repository = settings.getReadRepository( BeholdRepository() )
	skeinWindow = getWindowGivenTextRepository( fileName, gcodeText, repository )
	skeinWindow.updateDeiconify()

def compareLayerSequence( first, second ):
	"Get comparison in order to sort skein panes in ascending order of layer zone index then sequence index."
	if first.layerZoneIndex < second.layerZoneIndex:
		return - 1
	if first.layerZoneIndex > second.layerZoneIndex:
		return 1
	if first.sequenceIndex < second.sequenceIndex:
		return - 1
	return int( first.sequenceIndex > second.sequenceIndex )

def getNewRepository():
	"Get the repository constructor."
	return BeholdRepository()

def getWindowGivenTextRepository( fileName, gcodeText, repository ):
	"Display the gcode text in a behold viewer."
	skein = BeholdSkein()
	skein.parseGcode( fileName, gcodeText, repository )
	return SkeinWindow( repository, skein )

def writeOutput( fileName, gcodeText = '' ):
	"Write a beholded gcode file for a skeinforge gcode file, if 'Activate Behold' is selected."
	repository = settings.getReadRepository( BeholdRepository() )
	if repository.activateBehold.value:
		gcodeText = gcodec.getTextIfEmpty( fileName, gcodeText )
		analyzeFileGivenText( fileName, gcodeText, repository )


class BeholdRepository( tableau.TableauRepository ):
	"A class to handle the behold settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge_tools.analyze_plugins.behold.html', '', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( [ ( 'Gcode text files', '*.gcode' ) ], 'Open File to Behold', self, '' )
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute( 'http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Behold' )
		self.activateBehold = settings.BooleanSetting().getFromValue( 'Activate Behold', self, True )
		self.addAnimation()
		self.bandHeight = settings.IntSpinUpdate().getFromValue( 0, 'Band Height (layers):', self, 10, 5 )
		self.bottomBandBrightness = settings.FloatSpinUpdate().getFromValue( 0.0, 'Bottom Band Brightness (ratio):', self, 1.0, 0.7 )
		self.bottomLayerBrightness = settings.FloatSpinUpdate().getFromValue( 0.0, 'Bottom Layer Brightness (ratio):', self, 1.0, 1.0 )
		self.brightBandStart = settings.MenuButtonDisplay().getFromName( 'Bright Band Start:', self )
		self.fromTheBottom = settings.MenuRadio().getFromMenuButtonDisplay( self.brightBandStart, 'From the Bottom', self, False )
		self.fromTheTop = settings.MenuRadio().getFromMenuButtonDisplay( self.brightBandStart, 'From the Top', self, True )
		self.drawArrows = settings.BooleanSetting().getFromValue( 'Draw Arrows', self, False )
		self.goAroundExtruderOffTravel = settings.BooleanSetting().getFromValue( 'Go Around Extruder Off Travel', self, False )
		self.layer = settings.IntSpinNotOnMenu().getSingleIncrementFromValue( 0, 'Layer (index):', self, 912345678, 912345678 )
		self.layersFrom = settings.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Layers From (index):', self, 912345678, 0 )
		self.layersTo = settings.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Layers To (index):', self, 912345678, 0 )
		self.line = settings.IntSpinNotOnMenu().getSingleIncrementFromValue( 0, 'Line (index):', self, 912345678, 0 )
		self.mouseMode = settings.MenuButtonDisplay().getFromName( 'Mouse Mode:', self )
		self.displayLine = settings.MenuRadio().getFromMenuButtonDisplay( self.mouseMode, 'Display Line', self, True )
		self.viewMove = settings.MenuRadio().getFromMenuButtonDisplay( self.mouseMode, 'View Move', self, False )
		self.viewRotate = settings.MenuRadio().getFromMenuButtonDisplay( self.mouseMode, 'View Rotate', self, False )
		self.numberOfFillBottomLayers = settings.IntSpinUpdate().getFromValue( 0, 'Number of Fill Bottom Layers (integer):', self, 5, 1 )
		self.numberOfFillTopLayers = settings.IntSpinUpdate().getFromValue( 0, 'Number of Fill Top Layers (integer):', self, 5, 1 )
		self.addScaleScreenSlide()
		self.viewpointLatitude = settings.FloatSpin().getFromValue( 0.0, 'Viewpoint Latitude (degrees):', self, 180.0, 15.0 )
		self.viewpointLongitude = settings.FloatSpin().getFromValue( 0.0, 'Viewpoint Longitude (degrees):', self, 360.0, 210.0 )
		self.widthOfFillBottomThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Fill Bottom Thread (pixels):', self, 10, 2 )
		self.widthOfFillTopThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Fill Top Thread (pixels):', self, 10, 2 )
		self.widthOfInfillThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Infill Thread (pixels):', self, 10, 1 )
		self.widthOfLoopThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Loop Thread (pixels):', self, 10, 2 )
		self.widthOfPerimeterInsideThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Perimeter Inside Thread (pixels):', self, 10, 8 )
		self.widthOfPerimeterOutsideThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Perimeter Outside Thread (pixels):', self, 10, 8 )
		self.widthOfRaftThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Raft Thread (pixels):', self, 10, 1 )
		self.widthOfSelectionThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Selection Thread (pixels):', self, 10, 6 )
		self.widthOfTravelThread = settings.IntSpinUpdate().getFromValue( 0, 'Width of Travel Thread (pixels):', self, 10, 0 )
		self.widthOfXAxis = settings.IntSpinUpdate().getFromValue( 0, 'Width of X Axis (pixels):', self, 10, 5 )
		self.widthOfYAxis = settings.IntSpinUpdate().getFromValue( 0, 'Width of Y Axis (pixels):', self, 10, 5 )
		self.widthOfZAxis = settings.IntSpinUpdate().getFromValue( 0, 'Width of Z Axis (pixels):', self, 10, 5 )
		self.executeTitle = 'Behold'

	def execute( self ):
		"Write button has been clicked."
		fileNames = polyfile.getFileOrGcodeDirectory( self.fileNameInput.value, self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			analyzeFile( fileName )


class BeholdSkein:
	"A class to write a get a scalable vector graphics text for a gcode skein."
	def __init__( self ):
		self.coloredThread = []
		self.feedRateMinute = 960.1
		self.hasASurroundingLoopBeenReached = False
		self.isLoop = False
		self.isPerimeter = False
		self.isOuter = False
		self.isThereALayerStartWord = False
		self.layerTops = []
		self.oldLayerZoneIndex = 0
		self.oldZ = - 999999999999.0
		self.skeinPane = None
		self.skeinPanes = []
		self.thirdLayerThickness = 0.133333

	def addToPath( self, line, location ):
		'Add a point to travel and maybe extrusion.'
		if self.oldLocation == None:
			return
		begin = self.scale * self.oldLocation - self.scaleCenterBottom
		end = self.scale * location - self.scaleCenterBottom
		displayString = '%s %s' % ( self.lineIndex + 1, line )
		tagString = 'colored_line_index: %s %s' % ( len( self.skeinPane.coloredLines ), len( self.skeinPanes ) - 1 )
		coloredLine = tableau.ColoredLine( begin, '', displayString, end, tagString )
		coloredLine.z = location.z
		self.skeinPane.coloredLines.append( coloredLine )
		self.coloredThread.append( coloredLine )

	def getLayerTop( self ):
		"Get the layer top."
		if len( self.layerTops ) < 1:
			return - 9123456789123.9
		return self.layerTops[ - 1 ]

	def getLayerZoneIndex( self, z ):
		"Get the layer zone index."
		if self.layerTops[ self.oldLayerZoneIndex ] > z:
			if self.oldLayerZoneIndex == 0:
				return 0
			elif self.layerTops[ self.oldLayerZoneIndex - 1 ] < z:
				return self.oldLayerZoneIndex
		for layerTopIndex in xrange( len( self.layerTops ) ):
			layerTop = self.layerTops[ layerTopIndex ]
			if layerTop > z:
				self.oldLayerZoneIndex = layerTopIndex
				return layerTopIndex
		self.oldLayerZoneIndex = len( self.layerTops ) - 1
		return self.oldLayerZoneIndex

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

	def moveColoredThreadToSkeinPane( self ):
		'Move a colored thread to the skein pane.'
		if len( self.coloredThread ) <= 0:
			return
		layerZoneIndex = self.getLayerZoneIndex( self.coloredThread[ 0 ].z )
		if not self.extruderActive:
			self.setColoredThread( ( 190.0, 190.0, 190.0 ), self.skeinPane.travelLines ) #grey
			return
		self.skeinPane.layerZoneIndex = layerZoneIndex
		if self.isPerimeter:
			if self.isOuter:
				self.setColoredThread( ( 255.0, 0.0, 0.0 ), self.skeinPane.perimeterOutsideLines ) #red
			else:
				self.setColoredThread( ( 255.0, 165.0, 0.0 ), self.skeinPane.perimeterInsideLines ) #orange
			return
		if self.isLoop:
			self.setColoredThread( ( 255.0, 255.0, 0.0 ), self.skeinPane.loopLines ) #yellow
			return
		if not self.hasASurroundingLoopBeenReached:
			self.setColoredThread( ( 165.0, 42.0, 42.0 ), self.skeinPane.raftLines ) #brown
			return
		if layerZoneIndex < self.repository.numberOfFillBottomLayers.value:
			self.setColoredThread( ( 128.0, 128.0, 0.0 ), self.skeinPane.fillBottomLines ) #olive
			return
		if layerZoneIndex >= self.firstTopLayer:
			self.setColoredThread( ( 0.0, 0.0, 255.0 ), self.skeinPane.fillTopLines ) #blue
			return
		self.setColoredThread( ( 0.0, 255.0, 0.0 ), self.skeinPane.infillLines ) #green

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
		elif firstWord == '(<layer>':
			self.layerTopZ = float( splitLine[ 1 ] ) + self.thirdLayerThickness
		elif firstWord == '(<layerThickness>':
			self.thirdLayerThickness = 0.33333333333 * float( splitLine[ 1 ] )
		elif firstWord == '(<surroundingLoop>)':
			if self.layerTopZ > self.getLayerTop():
				self.layerTops.append( self.layerTopZ )

	def parseGcode( self, fileName, gcodeText, repository ):
		"Parse gcode text and store the vector output."
		self.repository = repository
		self.fileName = fileName
		self.gcodeText = gcodeText
		self.initializeActiveLocation()
		self.cornerHigh = Vector3( - 999999999.0, - 999999999.0, - 999999999.0 )
		self.cornerLow = Vector3( 999999999.0, 999999999.0, 999999999.0 )
		self.goAroundExtruderOffTravel = repository.goAroundExtruderOffTravel.value
		self.lines = gcodec.getTextLines( gcodeText )
		self.isThereALayerStartWord = gcodec.isThereAFirstWord( '(<layer>', self.lines, 1 )
		self.parseInitialization()
		for line in self.lines[ self.lineIndex : ]:
			self.parseCorner( line )
		if len( self.layerTops ) > 0:
			self.layerTops[ - 1 ] += 912345678.9
		if len( self.layerTops ) > 1:
			self.oneMinusBrightnessOverTopLayerIndex = ( 1.0 - repository.bottomLayerBrightness.value ) / float( len( self.layerTops ) - 1 )
		self.firstTopLayer = len( self.layerTops ) - self.repository.numberOfFillTopLayers.value
		self.centerComplex = 0.5 * ( self.cornerHigh.dropAxis( 2 ) + self.cornerLow.dropAxis( 2 ) )
		self.centerBottom = Vector3( self.centerComplex.real, self.centerComplex.imag, self.cornerLow.z )
		self.scale = repository.scale.value
		self.scaleCenterBottom = self.scale * self.centerBottom
		self.scaleCornerHigh = self.scale * self.cornerHigh.dropAxis( 2 )
		self.scaleCornerLow = self.scale * self.cornerLow.dropAxis( 2 )
		print( "The lower left corner of the behold window is at %s, %s" % ( self.cornerLow.x, self.cornerLow.y ) )
		print( "The upper right corner of the behold window is at %s, %s" % ( self.cornerHigh.x, self.cornerHigh.y ) )
		self.cornerImaginaryTotal = self.cornerHigh.y + self.cornerLow.y
		margin = complex( 5.0, 5.0 )
		self.marginCornerLow = self.scaleCornerLow - margin
		self.screenSize = margin + 2.0 * ( self.scaleCornerHigh - self.marginCornerLow )
		self.initializeActiveLocation()
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
			self.skeinPane = SkeinPane( len( self.skeinPanes ) )
			self.skeinPanes.append( self.skeinPane )
		if firstWord == 'G1':
			location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
			self.linearMove( line, location )
			self.oldLocation = location
		elif firstWord == 'M101':
			self.moveColoredThreadToSkeinPane()
			self.extruderActive = True
		elif firstWord == 'M103':
			self.moveColoredThreadToSkeinPane()
			self.extruderActive = False
			self.isLoop = False
			self.isPerimeter = False
		elif firstWord == '(<loop>':
			self.isLoop = True
		elif firstWord == '(</loop>)':
			self.moveColoredThreadToSkeinPane()
			self.isLoop = False
		elif firstWord == '(<perimeter>':
			self.isPerimeter = True
			self.isOuter = ( splitLine[ 1 ] == 'outer' )
		elif firstWord == '(</perimeter>)':
			self.moveColoredThreadToSkeinPane()
			self.isPerimeter = False
		elif firstWord == '(<surroundingLoop>)':
			self.hasASurroundingLoopBeenReached = True
		if firstWord == 'G2' or firstWord == 'G3':
			relativeLocation = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
			relativeLocation.z = 0.0
			location = self.oldLocation + relativeLocation
			self.linearMove( line, location )
			self.oldLocation = location

	def setColoredLineColor( self, coloredLine, colorTuple ):
		'Set the color and stipple of the colored line.'
		layerZoneIndex = self.getLayerZoneIndex( coloredLine.z )
		multiplier = self.repository.bottomLayerBrightness.value
		if len( self.layerTops ) > 1:
			multiplier += self.oneMinusBrightnessOverTopLayerIndex * float( layerZoneIndex )
		bandIndex = layerZoneIndex / self.repository.bandHeight.value
		if self.repository.fromTheTop.value:
			brightZoneIndex = len( self.layerTops ) - 1 - layerZoneIndex
			bandIndex = brightZoneIndex / self.repository.bandHeight.value + 1
		if bandIndex % 2 == 0:
			multiplier *= self.repository.bottomBandBrightness.value
		red = settings.getWidthHex( int( colorTuple[ 0 ] * multiplier ), 2 )
		green = settings.getWidthHex( int( colorTuple[ 1 ] * multiplier ), 2 )
		blue = settings.getWidthHex( int( colorTuple[ 2 ] * multiplier ), 2 )
		coloredLine.colorName = '#%s%s%s' % ( red, green, blue )

	def setColoredThread( self, colorTuple, lineList ):
		'Set the colored thread, then move it to the line list and stipple of the colored line.'
		for coloredLine in self.coloredThread:
			self.setColoredLineColor( coloredLine, colorTuple )
		lineList += self.coloredThread
		self.coloredThread = []


class SkeinPane:
	"A class to hold the colored lines for a layer."
	def __init__( self, sequenceIndex ):
		"Create empty line lists."
		self.coloredLines = []
		self.fillBottomLines = []
		self.fillTopLines = []
		self.index = 0
		self.infillLines = []
		self.layerZoneIndex = 0
		self.loopLines = []
		self.perimeterInsideLines = []
		self.perimeterOutsideLines = []
		self.raftLines = []
		self.sequenceIndex = sequenceIndex
		self.travelLines = []


class SkeinWindow( tableau.TableauWindow ):
	def __init__( self, repository, skein ):
		"Initialize the skein window."
		self.arrowshape = ( 24, 30, 9 )
		self.addCanvasMenuRootScrollSkein( repository, skein, '_behold', 'Behold Viewer' )
		self.center = 0.5 * self.screenSize
		self.motionStippleName = 'gray75'
		halfCenter = 0.5 * self.center.real
		roundedHalfCenter = euclidean.getThreeSignificantFigures( halfCenter / skein.scale )
		self.xAxisLine = tableau.ColoredLine( Vector3(), 'darkorange', None, Vector3( halfCenter ), 'X Axis: Origin -> %s,0,0' % roundedHalfCenter )
		self.yAxisLine = tableau.ColoredLine( Vector3(), 'gold', None, Vector3( 0.0, halfCenter ), 'Y Axis: Origin -> 0,%s,0' % roundedHalfCenter )
		self.zAxisLine = tableau.ColoredLine( Vector3(), 'skyblue', None, Vector3( 0.0, 0.0, halfCenter ), 'Z Axis: Origin -> 0,0,%s' % roundedHalfCenter )
		self.repository.bandHeight.setUpdateFunction( self.setWindowToDisplaySavePhoenixUpdate )
		self.repository.bottomBandBrightness.setUpdateFunction( self.setWindowToDisplaySavePhoenixUpdate )
		self.repository.bottomLayerBrightness.setUpdateFunction( self.setWindowToDisplaySavePhoenixUpdate )
		self.repository.drawArrows.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.fromTheBottom.setUpdateFunction( self.setWindowToDisplaySavePhoenixUpdate )
		self.repository.fromTheTop.setUpdateFunction( self.setWindowToDisplaySavePhoenixUpdate )
		self.repository.goAroundExtruderOffTravel.setUpdateFunction( self.setWindowToDisplaySavePhoenixUpdate )
		self.repository.layersFrom.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.layersTo.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.setWindowNewMouseTool( display_line.getNewMouseTool, self.repository.displayLine )
		self.setWindowNewMouseTool( view_move.getNewMouseTool, self.repository.viewMove )
		self.setWindowNewMouseTool( view_rotate.getNewMouseTool, self.repository.viewRotate )
		self.repository.numberOfFillBottomLayers.setUpdateFunction( self.setWindowToDisplaySavePhoenixUpdate )
		self.repository.numberOfFillTopLayers.setUpdateFunction( self.setWindowToDisplaySavePhoenixUpdate )
		self.repository.viewpointLatitude.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.viewpointLongitude.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfFillBottomThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfFillTopThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfInfillThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfLoopThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfPerimeterInsideThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfPerimeterOutsideThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfRaftThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfSelectionThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfTravelThread.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfXAxis.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfYAxis.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.repository.widthOfZAxis.setUpdateFunction( self.setWindowToDisplaySaveUpdate )
		self.addMouseToolsBind()

	def drawSkeinPane( self, skeinPane, viewVectors ):
		"Draw colored lines."
		self.getDrawnColoredLines( skeinPane.raftLines, viewVectors, self.repository.widthOfRaftThread.value )
		self.getDrawnColoredLines( skeinPane.travelLines, viewVectors, self.repository.widthOfTravelThread.value )
		self.getDrawnColoredLines( skeinPane.fillBottomLines, viewVectors, self.repository.widthOfFillBottomThread.value )
		self.getDrawnColoredLines( skeinPane.fillTopLines, viewVectors, self.repository.widthOfFillTopThread.value )
		self.getDrawnColoredLines( skeinPane.infillLines, viewVectors, self.repository.widthOfInfillThread.value )
		self.getDrawnColoredLines( skeinPane.loopLines, viewVectors, self.repository.widthOfLoopThread.value )
		self.getDrawnColoredLines( skeinPane.perimeterInsideLines, viewVectors, self.repository.widthOfPerimeterInsideThread.value )
		self.getDrawnColoredLines( skeinPane.perimeterOutsideLines, viewVectors, self.repository.widthOfPerimeterOutsideThread.value )

	def drawXYAxisLines( self, viewVectors ):
		"Draw the x and y axis lines."
		if self.repository.widthOfXAxis.value > 0:
			self.getDrawnColoredLine( 'last', self.xAxisLine, self.xAxisLine.tagString, viewVectors, self.repository.widthOfXAxis.value )
		if self.repository.widthOfYAxis.value > 0:
			self.getDrawnColoredLine( 'last', self.yAxisLine, self.yAxisLine.tagString, viewVectors, self.repository.widthOfYAxis.value )

	def drawZAxisLine( self, viewVectors ):
		"Draw the z axis line."
		if self.repository.widthOfZAxis.value > 0:
			self.getDrawnColoredLine( 'last', self.zAxisLine, self.zAxisLine.tagString, viewVectors, self.repository.widthOfZAxis.value )

	def getCentered( self, coordinate ):
		"Get the centered coordinate."
		relativeToCenter = complex( coordinate.real - self.center.real, self.center.imag - coordinate.imag )
		if abs( relativeToCenter ) < 1.0:
			relativeToCenter = complex( 0.0, 1.0 )
		return relativeToCenter

	def getCanvasRadius( self ):
		"Get half of the minimum of the canvas height and width."
		return 0.5 * min( float( self.canvasHeight ), float( self.canvasWidth ) )

	def getCenteredScreened( self, coordinate ):
		"Get the normalized centered coordinate."
		return self.getCentered( coordinate ) / self.getCanvasRadius()

	def getColoredLines( self ):
		"Get the colored lines from the skein pane."
		return self.skeinPanes[ self.repository.layer.value ].coloredLines

	def getCopy( self ):
		"Get a copy of this window."
		return SkeinWindow( self.repository, self.skein )

	def getCopyWithNewSkein( self ):
		"Get a copy of this window with a new skein."
		return getWindowGivenTextRepository( self.skein.fileName, self.skein.gcodeText, self.repository )

	def getDrawnColoredLine( self, arrowType, coloredLine, tags, viewVectors, width ):
		"Draw colored line."
		viewBegin = self.getViewComplex( coloredLine.begin, viewVectors )
		viewEnd = self.getViewComplex( coloredLine.end, viewVectors )
		return self.canvas.create_line(
			viewBegin.real,
			viewBegin.imag,
			viewEnd.real,
			viewEnd.imag,
			fill = coloredLine.colorName,
			arrow = arrowType,
			tags = tags,
			width = width )

	def getDrawnColoredLineMotion( self, coloredLine, viewVectors, width ):
		"Draw colored line with motion stipple and tag."
		viewBegin = self.getViewComplex( coloredLine.begin, viewVectors )
		viewEnd = self.getViewComplex( coloredLine.end, viewVectors )
		return self.canvas.create_line(
			viewBegin.real,
			viewBegin.imag,
			viewEnd.real,
			viewEnd.imag,
			fill = coloredLine.colorName,
			arrow = 'last',
			arrowshape = self.arrowshape,
			stipple = self.motionStippleName,
			tags = 'mouse_item',
			width = width + 4 )

	def getDrawnColoredLines( self, coloredLines, viewVectors, width ):
		"Draw colored lines."
		if width <= 0:
			return
		drawnColoredLines = []
		for coloredLine in coloredLines:
			drawnColoredLines.append( self.getDrawnColoredLine( self.arrowType, coloredLine, coloredLine.tagString, viewVectors, width ) )
		return drawnColoredLines

	def getDrawnSelectedColoredLine( self, coloredLine ):
		"Get the drawn selected colored line."
		viewVectors = view_rotate.ViewVectors( self.repository.viewpointLatitude.value, self.repository.viewpointLongitude.value )
		return self.getDrawnColoredLine( self.arrowType, coloredLine, 'mouse_item', viewVectors, self.repository.widthOfSelectionThread.value )

	def getLayersAround( self, layers ):
		"Get the layers wrappers around the number of skein panes."
		if layers < 0:
			return max( 0, len( self.skeinPanes ) + layers )
		return min( layers, len( self.skeinPanes ) - 1 )

	def getScreenComplex( self, pointComplex ):
		"Get the point in screen perspective."
		return complex( pointComplex.real, - pointComplex.imag ) + self.center

	def getViewComplex( self, point, viewVectors ):
		"Get the point in view perspective."
		screenComplexX = point.dot( viewVectors.viewXVector3 )
		screenComplexY = point.dot( viewVectors.viewYVector3 )
		return self.getScreenComplex( complex( screenComplexX, screenComplexY ) )

	def printHexadecimalColorName( self, name ):
		"Print the color name in hexadecimal."
		colorTuple = self.canvas.winfo_rgb( name )
		print( '#%s%s%s' % ( settings.getWidthHex( colorTuple[ 0 ], 2 ), settings.getWidthHex( colorTuple[ 1 ], 2 ), settings.getWidthHex( colorTuple[ 2 ], 2 ) ) )

	def update( self ):
		"Update the screen."
		if len( self.skeinPanes ) < 1:
			return
		self.limitIndexSetArrowMouseDeleteCanvas()
		self.repository.viewpointLatitude.value = view_rotate.getBoundedLatitude( self.repository.viewpointLatitude.value )
		self.repository.viewpointLongitude.value = round( self.repository.viewpointLongitude.value, 1 )
		viewVectors = view_rotate.ViewVectors( self.repository.viewpointLatitude.value, self.repository.viewpointLongitude.value )
		indexBegin = min( self.repository.layer.value, self.getLayersAround( self.repository.layersFrom.value ) )
		indexEnd = max( self.repository.layer.value + 1, self.getLayersAround( self.repository.layersTo.value ) + 1 )
		skeinPanesCopy = self.skeinPanes[ indexBegin : indexEnd ]
		skeinPanesCopy.sort( compareLayerSequence )
		if viewVectors.viewpointLatitudeRatio.real > 0.0:
			self.drawXYAxisLines( viewVectors )
		else:
			skeinPanesCopy.reverse()
			self.drawZAxisLine( viewVectors )
		for skeinPane in skeinPanesCopy:
			self.drawSkeinPane( skeinPane, viewVectors )
		if viewVectors.viewpointLatitudeRatio.real > 0.0:
			self.drawZAxisLine( viewVectors )
		else:
			self.drawXYAxisLines( viewVectors )
		self.setDisplayLayerIndex()


def main():
	"Display the behold dialog."
	if len( sys.argv ) > 1:
		analyzeFile( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
