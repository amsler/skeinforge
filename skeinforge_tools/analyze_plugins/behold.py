"""
Behold is an analysis script to display a gcode file in an isometric view.

The default 'Activate Behold' checkbox is on.  When it is on, the functions described below will work when called from the skeinforge toolchain, when it is off, the functions will not be called from the toolchain.  The functions will still be called, whether or not the 'Activate Behold' checkbox is on, when behold is run directly.  Behold can not separate the layers when it reads gcode without comments.

The viewer is simple, the viewpoint can only be moved in a sphere around the center of the model by changing the viewpoint latitude and longitude.  Different regions of the model can be hidden by setting the width of the thread to zero.  The alternating bands act as contour bands and their brightness and width can be changed.  The layers will be displayed starting at the "Layer From" index up until the "Layer To" index.  All of the preferences can be set in the initial "Behold Preferences" window and some can be changed after the viewer is running in the "Behold Dynamic Preferences" window.  In the viewer, dragging the mouse will change the viewpoint.

The "Band Height" is height of the band in layers, with the default of five, a pair of bands is ten layers high.  The "Bottom Band Brightness" is the ratio of the brightness of the bottom band over the brightness of the top band, the default is 0.7.  The "Bottom Layer Brightness" is the ratio of the brightness of the bottom layer over the brightness of the top layer, the default is 1.0.  With a low bottom layer brightness ratio the bottom of the model will be darker than the top of the model, as if it was being illuminated by a light just above the top.  The "Bright Band Start" button group determines where the bright band starts from.  If the "From the Bottom" choice is selected, the bright bands will start from the bottom.  If the default "From the Top" choice is selected, the bright bands will start from the top.

If "Draw Arrows" is selected, arrows will be drawn at the end of each line segment, the default is on.  If "Go Around Extruder Off Travel" is selected, the display will include the travel when the extruder is off, which means it will include the nozzle wipe path if any.

When the submenu in the export menu item in the file menu is clicked, an export canvas dialog will be displayed, which can export the canvas to a file.

The mouse tool can be changed from the 'Mouse Mode' menu button or picture button.  The 'Display Line' tool will display the line index of the line clicked, counting from one, and the line itself.  The 'Viewpoint Move' tool will move the viewpoint in the xy plane when the mouse is clicked and dragged on the canvas.  The 'Viewpoint Rotate' tool will rotate the viewpoint around the origin, when the mouse is clicked and dragged on the canvas, or the arrow keys have been used and <Return> is pressed.  The mouse tools listen to the arrow keys when the canvas has the focus.  Clicking in the canvas gives the canvas the focus, and when the canvas has the focus a thick black border is drawn around the canvas.

On the display window, the Up button increases the 'Layer Index' by one, and the Down button decreases the layer index by one.  When the index displayed in the index field is changed then <return> is hit, the layer index shown will be set to the index field, to a mimimum of zero and to a maximum of the highest index layer.  The layer index can also be changed from the Preferences menu or the behold dialog.  The Soar button increases the layer index at the 'Slide Show Rate', and the Dive button decreases the layer index at the slide show rate.  The layers displayed will start from the minimum of the "Layer From" setting and the layer index.  The layers displayed will go until the maximum of the 'Layer To' setting and the layer index.  If the layer to setting is a huge number like the default 999999999, the display will go to the top of the model.

The zoom in mouse tool will zoom in the display at the point where the mouse was clicked, increasing the scale by a factor of two.  The zoom out tool will zoom out the display at the point where the mouse was clicked, decreasing the scale by a factor of two.

The "Number of Fill Bottom Layers" is the number of layers at the bottom which will be colored olive.  The "Number of Fill Bottom Layers" is the number of layers at the top which will be colored blue.

The scale setting is the scale of the image in pizels per millimeter, the higher the number, the greater the size of the display.  The "Screen Horizontal Inset" determines how much the display will be inset in the horizontal direction from the edge of screen, the higher the number the more it will be inset and the smaller it will be, the default is one hundred.  The "Screen Vertical Inset" determines how much the display will be inset in the vertical direction from the edge of screen, the default is fifty.

The "Viewpoint Latitude" is the latitude of the viewpoint, the default is 15 degrees.  The "Viewpoint Longitude" is the longitude of the viewpoint, the default is 210 degrees.  The viewpoint can also be moved by dragging the mouse.  The viewpoint latitude will be increased when the mouse is dragged from the center towards the edge.  The viewpoint longitude will be changed by the amount around the center the mouse is dragged.  This is not very intuitive, but I don't know how to do this the intuitive way and I have other stuff to develop.  If the shift key is pressed; if the latitude is changed more than the longitude, only the latitude will be changed, if the longitude is changed more only the longitude will be changed.

The "Width of Infill Thread" sets the width of the green extrusion threads, those threads which are not loops and not part of the raft.  The default is one, if the width is zero the extrusion threads will be invisible.  The "Width of Fill Bottom Thread" sets the width of the olive extrusion threads at the bottom of the model, the default is three.  The "Width of Fill Top Thread" sets the width of the blue extrusion threads at the top of the model, the default is three.  The "Width of Loop Thread" sets the width of the yellow loop threads, which are not perimeters, the default is three.  The "Width of Perimeter Inside Thread" sets the width of the orange inside perimeter threads, the default is three.  The "Width of Perimeter Outside Thread" sets the width of the red outside perimeter threads, the default is three.  The "Width of Raft Thread" sets the width of the brown raft threads, the default is one.  The "Width of Selection Thread" sets the width of the selected line, the default is six.  The "Width of Travel Thread" sets the width of the grey extruder off travel threads, the default is zero.

The "Width of X Axis" preference sets the width of the dark orange X Axis, the default is five pixels.  The "Width of Y Axis" sets the width of the gold Y Axis, the default is five.  The "Width of Z Axis" sets the width of the sky blue Z Axis, the default is five.

The dive, soar and zoom icons are from Mark James' soarSilk icon set 1.3 at:
http://www.famfamfam.com/lab/icons/silk/

To run behold, in a shell in the folder which behold is in type:
> python behold.py

An explanation of the gcodes is at:
http://reprap.org/bin/view/Main/Arduino_GCode_Interpreter

and at:
http://reprap.org/bin/view/Main/MCodeReference

A gode example is at:
http://forums.reprap.org/file.php?12,file=565

This example lets the viewer behold the gcode file Screw Holder.gcode.  This example is run in a terminal in the folder which contains Screw Holder.gcode and behold.py.


> python behold.py
This brings up the behold dialog.


> python behold.py Screw Holder.gcode
This brings up the behold dialog to view the gcode file.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import behold
>>> behold.main()
This brings up the behold dialog.


>>> behold.beholdFile()
This brings up the behold window to view the gcode file.

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
from skeinforge_tools.skeinforge_utilities import preferences
from skeinforge_tools.meta_plugins import polyfile
import math
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


#bring up the preferences window, maybe make dragging more intuitive
def beholdFile( fileName = '' ):
	"Behold a gcode file.  If no fileName is specified, behold the first gcode file in this folder that is not modified."
	gcodeText = gcodec.getFileText( fileName )
	displayFileGivenText( fileName, gcodeText )

def compareLayerSequence( first, second ):
	"Get comparison in order to sort skein panes in ascending order of layer zone index then sequence index."
	if first.layerZoneIndex < second.layerZoneIndex:
		return - 1
	if first.layerZoneIndex > second.layerZoneIndex:
		return 1
	if first.sequenceIndex < second.sequenceIndex:
		return - 1
	return int( first.sequenceIndex > second.sequenceIndex )

def displayFileGivenText( fileName, gcodeText, beholdRepository = None ):
	"Display a beholded gcode file for a gcode file."
	if gcodeText == '':
		return ''
	if beholdRepository == None:
		beholdRepository = BeholdRepository()
		preferences.getReadRepository( beholdRepository )
	skeinWindow = getWindowGivenTextRepository( fileName, gcodeText, beholdRepository )
	skeinWindow.updateDeiconify()

def getPolygonComplexFromColoredLines( coloredLines ):
	"Get a complex polygon from the colored lines."
	polygonComplex = []
	for coloredLine in coloredLines:
		polygonComplex.append( coloredLine.begin.dropAxis( 2 ) )
	return polygonComplex

def getNewRepository():
	"Get the repository constructor."
	return BeholdRepository()

def getWindowGivenTextRepository( fileName, gcodeText, beholdRepository ):
	"Display the gcode text in a behold viewer."
	skein = BeholdSkein()
	skein.parseGcode( fileName, gcodeText, beholdRepository )
	return SkeinWindow( beholdRepository, skein )

def writeOutput( fileName, gcodeText = '' ):
	"Write a beholded gcode file for a skeinforge gcode file, if 'Activate Behold' is selected."
	beholdRepository = BeholdRepository()
	preferences.getReadRepository( beholdRepository )
	if beholdRepository.activateBehold.value:
		gcodeText = gcodec.getTextIfEmpty( fileName, gcodeText )
		displayFileGivenText( fileName, gcodeText, beholdRepository )


class BeholdRepository( tableau.TableauRepository ):
	"A class to handle the behold preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		preferences.addListsToRepository( 'skeinforge_tools.analyze_plugins.behold.html', '', self )
		self.initializeUpdateFunctionsToNone()
		self.fileNameInput = preferences.FileNameInput().getFromFileName( [ ( 'Gcode text files', '*.gcode' ) ], 'Open File to Behold', self, '' )
		self.activateBehold = preferences.BooleanPreference().getFromValue( 'Activate Behold', self, True )
		self.addAnimation()
		self.bandHeight = preferences.IntSpinUpdate().getFromValue( 0, 'Band Height (layers):', self, 10, 5 )
		self.bandHeight.setUpdateFunction( self.setToDisplaySaveResizeUpdate )
		self.bottomBandBrightness = preferences.FloatSpinUpdate().getFromValue( 0.0, 'Bottom Band Brightness (ratio):', self, 1.0, 0.7 )
		self.bottomBandBrightness.setUpdateFunction( self.setToDisplaySaveResizeUpdate )
		self.bottomLayerBrightness = preferences.FloatSpinUpdate().getFromValue( 0.0, 'Bottom Layer Brightness (ratio):', self, 1.0, 1.0 )
		self.bottomLayerBrightness.setUpdateFunction( self.setToDisplaySaveResizeUpdate )
		self.brightBandStart = preferences.MenuButtonDisplay().getFromName( 'Bright Band Start:', self )
		self.fromTheBottom = preferences.MenuRadio().getFromMenuButtonDisplay( self.brightBandStart, 'From the Bottom', self, False )
		self.fromTheBottom.setUpdateFunction( self.setToDisplaySaveResizeUpdate )
		self.fromTheTop = preferences.MenuRadio().getFromMenuButtonDisplay( self.brightBandStart, 'From the Top', self, True )
		self.fromTheTop.setUpdateFunction( self.setToDisplaySaveResizeUpdate )
		self.drawArrows = preferences.BooleanPreference().getFromValue( 'Draw Arrows', self, False )
		self.drawArrows.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.goAroundExtruderOffTravel = preferences.BooleanPreference().getFromValue( 'Go Around Extruder Off Travel', self, False )
		self.goAroundExtruderOffTravel.setUpdateFunction( self.setToDisplaySavePhoenixUpdate )
		self.layer = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Layer (index):', self, 912345678, 0 )
		self.layer.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.layersFrom = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Layers From (index):', self, 912345678, 0 )
		self.layersFrom.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.layersTo = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Layers To (index):', self, 912345678, 0 )
		self.layersTo.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.line = preferences.IntSpinUpdate().getSingleIncrementFromValue( 0, 'Line (index):', self, 912345678, 0 )
		self.line.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.mouseMode = preferences.MenuButtonDisplay().getFromName( 'Mouse Mode:', self )
		self.displayLine = preferences.MenuRadio().getFromMenuButtonDisplay( self.mouseMode, 'Display Line', self, True )
		self.setNewMouseToolUpdate( display_line.getNewMouseTool, self.displayLine )
		self.viewMove = preferences.MenuRadio().getFromMenuButtonDisplay( self.mouseMode, 'View Move', self, False )
		self.setNewMouseToolUpdate( view_move.getNewMouseTool, self.viewMove )
		self.viewRotate = preferences.MenuRadio().getFromMenuButtonDisplay( self.mouseMode, 'View Rotate', self, False )
		self.setNewMouseToolUpdate( view_rotate.getNewMouseTool, self.viewRotate )
		self.numberOfFillBottomLayers = preferences.IntSpinUpdate().getFromValue( 0, 'Number of Fill Bottom Layers (integer):', self, 5, 1 )
		self.numberOfFillBottomLayers.setUpdateFunction( self.setToDisplaySaveResizeUpdate )
		self.numberOfFillTopLayers = preferences.IntSpinUpdate().getFromValue( 0, 'Number of Fill Top Layers (integer):', self, 5, 1 )
		self.numberOfFillTopLayers.setUpdateFunction( self.setToDisplaySaveResizeUpdate )
		self.addScaleScreenSlide()
		self.viewpointLatitude = preferences.FloatSpin().getFromValue( 0.0, 'Viewpoint Latitude (degrees):', self, 180.0, 15.0 )
		self.viewpointLatitude.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.viewpointLongitude = preferences.FloatSpin().getFromValue( 0.0, 'Viewpoint Longitude (degrees):', self, 360.0, 210.0 )
		self.viewpointLongitude.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfFillBottomThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Fill Bottom Thread (pixels):', self, 5, 2 )
		self.widthOfFillBottomThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfFillTopThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Fill Top Thread (pixels):', self, 5, 2 )
		self.widthOfFillTopThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfInfillThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Infill Thread (pixels):', self, 5, 1 )
		self.widthOfInfillThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfLoopThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Loop Thread (pixels):', self, 5, 2 )
		self.widthOfLoopThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfPerimeterInsideThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Perimeter Inside Thread (pixels):', self, 5, 4 )
		self.widthOfPerimeterInsideThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfPerimeterOutsideThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Perimeter Outside Thread (pixels):', self, 5, 4 )
		self.widthOfPerimeterOutsideThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfRaftThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Raft Thread (pixels):', self, 5, 1 )
		self.widthOfRaftThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfSelectionThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Selection Thread (pixels):', self, 10, 6 )
		self.widthOfSelectionThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfTravelThread = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Travel Thread (pixels):', self, 5, 0 )
		self.widthOfTravelThread.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfXAxis = preferences.IntSpinUpdate().getFromValue( 0, 'Width of X Axis (pixels):', self, 10, 5 )
		self.widthOfXAxis.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfYAxis = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Y Axis (pixels):', self, 10, 5 )
		self.widthOfYAxis.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.widthOfZAxis = preferences.IntSpinUpdate().getFromValue( 0, 'Width of Z Axis (pixels):', self, 10, 5 )
		self.widthOfZAxis.setUpdateFunction( self.setToDisplaySaveUpdate )
		self.executeTitle = 'Behold'

	def execute( self ):
		"Write button has been clicked."
		fileNames = polyfile.getFileOrGcodeDirectory( self.fileNameInput.value, self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			beholdFile( fileName )


class BeholdSkein:
	"A class to write a get a scalable vector graphics text for a gcode skein."
	def __init__( self ):
		self.coloredThread = []
		self.feedRateMinute = 960.1
		self.hasASurroundingLoopBeenReached = False
		self.isLoop = False
		self.isPerimeter = False
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
			perimeterComplex = getPolygonComplexFromColoredLines( self.coloredThread )
			if euclidean.isWiddershins( perimeterComplex ):
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
		if layerZoneIndex < self.beholdRepository.numberOfFillBottomLayers.value:
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

	def parseGcode( self, fileName, gcodeText, beholdRepository ):
		"Parse gcode text and store the vector output."
		self.beholdRepository = beholdRepository
		self.fileName = fileName
		self.gcodeText = gcodeText
		self.initializeActiveLocation()
		self.cornerHigh = Vector3( - 999999999.0, - 999999999.0, - 999999999.0 )
		self.cornerLow = Vector3( 999999999.0, 999999999.0, 999999999.0 )
		self.goAroundExtruderOffTravel = beholdRepository.goAroundExtruderOffTravel.value
		self.lines = gcodec.getTextLines( gcodeText )
		self.isThereALayerStartWord = gcodec.isThereAFirstWord( '(<layer>', self.lines, 1 )
		self.parseInitialization()
		for line in self.lines[ self.lineIndex : ]:
			self.parseCorner( line )
		if len( self.layerTops ) > 0:
			self.layerTops[ - 1 ] += 912345678.9
		if len( self.layerTops ) > 1:
			self.oneMinusBrightnessOverTopLayerIndex = ( 1.0 - beholdRepository.bottomLayerBrightness.value ) / float( len( self.layerTops ) - 1 )
		self.firstTopLayer = len( self.layerTops ) - self.beholdRepository.numberOfFillTopLayers.value
		self.centerComplex = 0.5 * ( self.cornerHigh.dropAxis( 2 ) + self.cornerLow.dropAxis( 2 ) )
		self.centerBottom = Vector3( self.centerComplex.real, self.centerComplex.imag, self.cornerLow.z )
		self.scale = beholdRepository.scale.value
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
		elif firstWord == '(<loop>)':
			self.isLoop = True
		elif firstWord == '(<perimeter>)':
			self.isPerimeter = True
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
		multiplier = self.beholdRepository.bottomLayerBrightness.value
		if len( self.layerTops ) > 1:
			multiplier += self.oneMinusBrightnessOverTopLayerIndex * float( layerZoneIndex )
		bandIndex = layerZoneIndex / self.beholdRepository.bandHeight.value
		if self.beholdRepository.fromTheTop.value:
			brightZoneIndex = len( self.layerTops ) - 1 - layerZoneIndex
			bandIndex = brightZoneIndex / self.beholdRepository.bandHeight.value + 1
		if bandIndex % 2 == 0:
			multiplier *= self.beholdRepository.bottomBandBrightness.value
		red = preferences.getWidthHex( int( colorTuple[ 0 ] * multiplier ), 2 )
		green = preferences.getWidthHex( int( colorTuple[ 1 ] * multiplier ), 2 )
		blue = preferences.getWidthHex( int( colorTuple[ 2 ] * multiplier ), 2 )
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
			self.getDrawnColoredLine( 'last', self.xAxisLine, viewVectors, self.repository.widthOfXAxis.value )
		if self.repository.widthOfYAxis.value > 0:
			self.getDrawnColoredLine( 'last', self.yAxisLine, viewVectors, self.repository.widthOfYAxis.value )

	def drawZAxisLine( self, viewVectors ):
		"Draw the z axis line."
		if self.repository.widthOfZAxis.value > 0:
			self.getDrawnColoredLine( 'last', self.zAxisLine, viewVectors, self.repository.widthOfZAxis.value )

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

	def getDrawnColoredLine( self, arrowType, coloredLine, viewVectors, width ):
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
			tags = coloredLine.tagString,
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
			tags = 'view_rotate_item',
			width = width + 4 )

	def getDrawnColoredLines( self, coloredLines, viewVectors, width ):
		"Draw colored lines."
		if width <= 0:
			return
		drawnColoredLines = []
		for coloredLine in coloredLines:
			drawnColoredLines.append( self.getDrawnColoredLine( self.arrowType, coloredLine, viewVectors, width ) )
		return drawnColoredLines

	def getLayersAround( self, layers ):
		"Get the layers wrappers around the number of skein panes."
		if layers < 0:
			return layers % len( self.skeinPanes )
		return layers % len( self.skeinPanes )

	def getScreenComplex( self, pointComplex ):
		"Get the point in screen perspective."
		return complex( pointComplex.real, - pointComplex.imag ) + self.center

	def getSelectedDrawnColoredLines( self, coloredLines ):
		"Get the selected drawn colored lines."
		viewVectors = view_rotate.ViewVectors( self.repository.viewpointLatitude.value, self.repository.viewpointLongitude.value )
		return self.getDrawnColoredLines( coloredLines, viewVectors, self.repository.widthOfSelectionThread.value )

	def getViewComplex( self, point, viewVectors ):
		"Get the point in view perspective."
		screenComplexX = point.dot( viewVectors.viewXVector3 )
		screenComplexY = point.dot( viewVectors.viewYVector3 )
		return self.getScreenComplex( complex( screenComplexX, screenComplexY ) )

	def printHexadecimalColorName( self, name ):
		"Print the color name in hexadecimal."
		colorTuple = self.canvas.winfo_rgb( name )
		print( '#%s%s%s' % ( preferences.getWidthHex( colorTuple[ 0 ], 2 ), preferences.getWidthHex( colorTuple[ 1 ], 2 ), preferences.getWidthHex( colorTuple[ 2 ], 2 ) ) )

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
		beholdFile( ' '.join( sys.argv[ 1 : ] ) )
	else:
		preferences.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
