"""
Tableau has a couple of base classes for analyze viewers.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.analyze_plugins.analyze_utilities import zoom_in
from skeinforge_tools.analyze_plugins.analyze_utilities import zoom_out
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import preferences
import os

__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getGridHorizontalFrame( gridPosition ):
	"Get the grid horizontal object with a frame from the grid position."
	gridHorizontal = preferences.GridHorizontal( 0, 0 )
	gridHorizontal.master = preferences.Tkinter.Frame( gridPosition.master )
	gridHorizontal.master.grid( row = gridPosition.row, column = gridPosition.column, sticky = preferences.Tkinter.E )
	return gridHorizontal

def getScrollbarCanvasPortion( scrollbar ):
	"Get the canvas portion of the scrollbar."
	scrollbarBeginEnd = scrollbar.get()
	return scrollbarBeginEnd[ 1 ] - scrollbarBeginEnd[ 0 ]

def setStateNormalDisabled( active, widget ):
	"Set the state of the widget to normal if active and disabled if inactive."
	if active:
		widget.config( state = preferences.Tkinter.NORMAL )
	else:
		widget.config( state = preferences.Tkinter.DISABLED )


class ColoredLine:
	"A colored index line."
	def __init__( self, begin, colorName, displayString, end, tagString ):
		"Set the color name and corners."
		self.begin = begin
		self.colorName = colorName
		self.displayString = displayString
		self.end = end
		self.tagString = tagString
	
	def __repr__( self ):
		"Get the string representation of this colored index line."
		return '%s, %s, %s, %s' % ( self.colorName, self.begin, self.end, self.tagString )


class ExportCanvasDialog:
	"A class to display the export canvas repository dialog."
	def addPluginToMenu( self, canvas, fileName, menu, name, suffix ):
		"Add the display command to the menu."
		self.canvas = canvas
		self.fileName = fileName
		self.name = name
		self.suffix = suffix
		menu.add_command( label = preferences.getEachWordCapitalized( self.name ), command = self.display )

	def display( self ):
		"Display the export canvas repository dialog."
		for repositoryDialog in preferences.globalRepositoryDialogListTable:
			if repositoryDialog.repository.lowerName == self.name:
				repositoryDialog.setCanvasFileNameSuffix( self.canvas, self.skein.fileName, self.suffix )
				preferences.liftRepositoryDialogs( preferences.globalRepositoryDialogListTable[ repositoryDialog ] )
				return
		exportCanvasPluginsFolderPath = gcodec.getAbsoluteFolderPath( os.path.dirname( __file__ ), 'export_canvas_plugins' )
		pluginModule = gcodec.getModuleWithDirectoryPath( exportCanvasPluginsFolderPath, self.name )
		if pluginModule == None:
			return None
		pluginRepository = pluginModule.getNewRepository()
		pluginRepository.setCanvasFileNameSuffix( self.canvas, self.fileName, self.suffix )
		preferences.getDisplayedDialogFromConstructor( pluginRepository )


class TableauRepository:
	"The viewer base repository class."
	def activateMouseModeToolUpdate( self ):
		"Call the activateMouseModeTool function."
		self.setToDisplaySave()
		if self.activateMouseModeTool != None:
			self.activateMouseModeTool()

	def addAnimation( self ):
		"Add the animation settings."
		self.animationLineQuickening = preferences.FloatSpinUpdate().getFromValue( 0.5, 'Animation Line Quickening (ratio):', self, 4.5, 1.0 )
		self.animationLineQuickening.setUpdateFunction( self.setToDisplaySave )
		self.animationSlideShowRate = preferences.FloatSpinUpdate().getFromValue( 1.0, 'Animation Slide Show Rate (layers/second):', self, 5.0, 2.0 )
		self.animationSlideShowRate.setUpdateFunction( self.setToDisplaySave )

	def addScaleScreenSlide( self ):
		"Add the scale, screen and slide show settings."
		self.scale = preferences.FloatSpinNotOnMenu().getFromValue( 10.0, 'Scale (pixels per millimeter):', self, 50.0, 15.0 )
		self.screenHorizontalInset = preferences.IntSpin().getFromValue( 80, 'Screen Horizontal Inset (pixels):', self, 1000, 100 )
		self.screenHorizontalInset.setUpdateFunction( self.setToDisplaySaveRedisplayWindowUpdate )
		self.screenVerticalInset = preferences.IntSpin().getFromValue( 120, 'Screen Vertical Inset (pixels):', self, 1000, 200 )
		self.screenVerticalInset.setUpdateFunction( self.setToDisplaySaveRedisplayWindowUpdate )

	def initializeUpdateFunctionsToNone( self ):
		"Initialize all the update functions to none."
		self.activateMouseModeTool = None
		self.frameList = preferences.FrameList().getFromValue( 'Frame List', self, [] )
		self.phoenixUpdateFunction = None
		self.updateFunction = None

	def setNewMouseToolUpdate( self, getNewMouseToolFunction, mouseTool ):
		"Set the getNewMouseTool function and the update function."
		mouseTool.getNewMouseToolFunction = getNewMouseToolFunction
		mouseTool.setUpdateFunction( self.activateMouseModeToolUpdate )

	def setToDisplaySave( self, event = None ):
		"Set the preference values to the display, save the new values."
		for menuEntity in self.menuEntities:
			if menuEntity in self.archive:
				menuEntity.setToDisplay()
		preferences.writePreferences( self )

	def setToDisplaySavePhoenixUpdate( self, event = None ):
		"Set the preference values to the display, save the new values, then call the update function."
		self.setToDisplaySave()
		if self.phoenixUpdateFunction != None:
			self.phoenixUpdateFunction()

	def setToDisplaySaveRedisplayWindowUpdate( self, event = None ):
		"Set the preference values to the display, save the new values, then call the update function."
		self.setToDisplaySave()
		if self.redisplayWindowUpdateFunction != None:
			self.redisplayWindowUpdateFunction()

	def setToDisplaySaveUpdate( self, event = None ):
		"Set the preference values to the display, save the new values, then call the update function."
		self.setToDisplaySave()
		if self.updateFunction != None:
			self.updateFunction()


class TableauWindow:
	def activateMouseModeTool( self ):
		"Activate the mouse mode tool."
		self.createMouseModeTool()
		self.mouseTool.update()

	def addCanvasMenuRootScrollSkein( self, repository, skein, suffix, title ):
		"Add the canvas, menu bar, scroll bar, skein panes, tableau repository, root and skein."
		self.imagesDirectoryPath = os.path.join( preferences.getSkeinforgeDirectoryPath(), 'images' )
		self.photoImages = {}
		self.movementTextID = None
		self.mouseInstantButtons = []
		self.repository = repository
		self.root = preferences.Tkinter.Tk()
		self.gridPosition = preferences.GridVertical( 0, 1 )
		self.gridPosition.master = self.root
		self.root.title( os.path.basename( skein.fileName ) + ' - ' + title )
		self.screenSize = skein.screenSize
		self.skein = skein
		self.skeinPanes = skein.skeinPanes
		self.suffix = suffix
		self.timerID = None
		repository.animationSlideShowRate.value = max( repository.animationSlideShowRate.value, 0.01 )
		repository.animationSlideShowRate.value = min( repository.animationSlideShowRate.value, 85.0 )
		for menuRadio in repository.mouseMode.menuRadios:
			fileName = menuRadio.name.lower()
			fileName = fileName.replace( ' ', '_' ) + '.ppm'
			menuRadio.mouseButton = self.getPhotoButtonGridIncrement( menuRadio.invoke, fileName, self.gridPosition )
		self.gridPosition = preferences.GridHorizontal( 1, 99 )
		self.gridPosition.master = self.root
		self.xScrollbar = preferences.Tkinter.Scrollbar( self.root, orient = preferences.Tkinter.HORIZONTAL )
		self.xScrollbar.grid( row = 98, column = 2, columnspan = 96, sticky = preferences.Tkinter.E + preferences.Tkinter.W )
		self.yScrollbar = preferences.Tkinter.Scrollbar( self.root )
		self.yScrollbar.grid( row = 1, rowspan = 97, column = 99, sticky = preferences.Tkinter.N + preferences.Tkinter.S )
		self.canvasHeight = min( int( skein.screenSize.imag ), self.root.winfo_screenheight() - repository.screenVerticalInset.value )
		self.canvasWidth = min( int( skein.screenSize.real ), self.root.winfo_screenwidth() - repository.screenHorizontalInset.value )
		scrollRegionBoundingBox = ( 0, 0, int( skein.screenSize.real ), int( skein.screenSize.imag ) )
		self.canvas = preferences.Tkinter.Canvas( self.root, highlightthickness = 3, width = self.canvasWidth, height = self.canvasHeight, scrollregion = scrollRegionBoundingBox )
		self.canvas.grid( row = 1, rowspan = 97, column = 2, columnspan = 96, sticky = preferences.Tkinter.E + preferences.Tkinter.W + preferences.Tkinter.N + preferences.Tkinter.S )
		self.fileHelpMenuBar = preferences.FileHelpMenuBar( self.root )
		self.exportMenu = preferences.Tkinter.Menu( self.fileHelpMenuBar.fileMenu, tearoff = 0 )
		self.fileHelpMenuBar.fileMenu.add_cascade( label = "Export", menu = self.exportMenu, underline = 0 )
		exportCanvasPluginsFolderPath = gcodec.getAbsoluteFolderPath( os.path.dirname( __file__ ), 'export_canvas_plugins' )
		exportCanvasPluginFileNames = gcodec.getPluginFileNamesFromDirectoryPath( exportCanvasPluginsFolderPath )
		for exportCanvasPluginFileName in exportCanvasPluginFileNames:
			ExportCanvasDialog().addPluginToMenu( self.canvas, skein.fileName, self.exportMenu, exportCanvasPluginFileName, suffix )
		self.fileHelpMenuBar.fileMenu.add_separator()
		self.fileHelpMenuBar.completeMenu( self.close, repository, self.save, self )

	def addLayer( self, gridPosition ):
		"Add the layer frame items."
		self.diveButton = self.getPhotoButtonGridIncrement( self.dive, 'dive.ppm', gridPosition )
		self.soarButton = self.getPhotoButtonGridIncrement( self.soar, 'soar.ppm', gridPosition )
		gridPosition.increment()
		preferences.Tkinter.Label( gridPosition.master, text = 'Layer:' ).grid( row = gridPosition.row, column = gridPosition.column, sticky = preferences.Tkinter.W )
		gridPosition.increment()
		self.limitIndex()
		self.layerEntry = preferences.Tkinter.Spinbox( gridPosition.master, command = self.layerEntryReturnPressed, from_ = 0, increment = 1, to = len( self.skeinPanes ) - 1 )
		self.layerEntry.bind( '<Return>', self.layerEntryReturnPressed )
		self.layerEntry.grid( row = gridPosition.row, column = gridPosition.column, sticky = preferences.Tkinter.W )

	def addLine( self, gridPosition ):
		"Add the line frame items."
		self.lineDiveButton = self.getPhotoButtonGridIncrement( self.lineDive, 'dive.ppm', gridPosition )
		self.lineSoarButton = self.getPhotoButtonGridIncrement( self.lineSoar, 'soar.ppm', gridPosition )
		gridPosition.increment()
		preferences.Tkinter.Label( gridPosition.master, text = 'Line:' ).grid( row = gridPosition.row, column = gridPosition.column, sticky = preferences.Tkinter.W )
		gridPosition.increment()
		self.lineEntry = preferences.Tkinter.Spinbox( gridPosition.master, command = self.lineEntryReturnPressed, from_ = 0, increment = 1, to = len( self.getColoredLines() ) - 1 )
		self.lineEntry.bind( '<Return>', self.lineEntryReturnPressed )
		self.lineEntry.grid( row = gridPosition.row, column = gridPosition.column, sticky = preferences.Tkinter.W )

	def addMouseInstantTool( self, fileName, gridPosition, mouseInstantTool ):
		"Add the mouse instant tool and derived photo button."
		mouseInstantTool.getReset( self )
		photoButton = self.getPhotoButtonGridIncrement( mouseInstantTool.click, fileName, gridPosition )
		mouseInstantTool.mouseButton = photoButton
		self.mouseInstantButtons.append( photoButton )

	def addMouseToolsBind( self ):
		"Add the mouse tool and bind button one clicked, button one released and motion."
		self.xScrollbar.config( command = self.relayXview )
		self.yScrollbar.config( command = self.relayYview )
		self.canvas[ 'xscrollcommand' ] = self.xScrollbar.set
		self.canvas[ 'yscrollcommand' ] = self.yScrollbar.set
		preferences.CloseListener( self, self.destroyAllDialogWindows ).listenToWidget( self.canvas )
		self.canvasScreenCenter = 0.5 * complex( float( self.canvasWidth ) / float( self.screenSize.real ), float( self.canvasHeight ) / float( self.screenSize.imag ) )
		self.addPhotoImage( 'stop.ppm', self.gridPosition )
		self.gridPosition.increment()
		self.addLayer( getGridHorizontalFrame( self.gridPosition ) )
		self.gridPosition.increment()
		self.addLine( getGridHorizontalFrame( self.gridPosition ) )
		self.gridPosition.increment()
		self.addScale( getGridHorizontalFrame( self.gridPosition ) )
		self.gridPosition = preferences.GridVertical( self.gridPosition.columnStart + 1, self.gridPosition.row )
		self.gridPosition.master = self.root
		for name in self.repository.frameList.value:
			entity = self.getEntityFromName( name )
			if entity != None:
				self.gridPosition.incrementForThreeColumn()
				entity.addToDialog( getGridHorizontalFrame( self.gridPosition ) )
		for menuRadio in self.repository.mouseMode.menuRadios:
			menuRadio.mouseTool = menuRadio.getNewMouseToolFunction().getReset( self )
			self.mouseTool = menuRadio.mouseTool
		self.createMouseModeTool()
		self.canvas.bind( '<Button-1>', self.button1 )
		self.canvas.bind( '<ButtonRelease-1>', self.buttonRelease1 )
		self.canvas.bind( '<KeyPress-Down>', self.keyPressDown )
		self.canvas.bind( '<KeyPress-Left>', self.keyPressLeft )
		self.canvas.bind( '<KeyPress-Right>', self.keyPressRight )
		self.canvas.bind( '<KeyPress-Up>', self.keyPressUp )
		self.canvas.bind( '<Motion>', self.motion )
		self.canvas.bind( '<Return>', self.keyPressReturn )
		self.canvas.bind( '<Shift-ButtonRelease-1>', self.shiftButtonRelease1 )
		self.canvas.bind( '<Shift-Motion>', self.shiftMotion )
		self.layerEntry.bind( '<Destroy>', self.cancelTimer )
		self.root.grid_columnconfigure( 44, weight = 1 )
		self.root.grid_rowconfigure( 44, weight = 1 )
		self.resetPeriodicButtonsText()
		self.canvas.focus_set()

	def addPhotoImage( self, fileName, gridPosition ):
		"Get a PhotoImage button, grid the button and increment the grid position."
		photoImage = None
		try:
			photoImage = preferences.Tkinter.PhotoImage( file = os.path.join( self.imagesDirectoryPath, fileName ), master = gridPosition.master )
		except:
			print( 'Image %s was not found in the images directory, so a text button will be substituted.' % fileName )
		untilDotFileName = gcodec.getUntilDot( fileName )
		self.photoImages[ untilDotFileName ] = photoImage
		return untilDotFileName

	def addScale( self, gridPosition ):
		"Add the line frame items."
		self.addMouseInstantTool( 'zoom_out.ppm', gridPosition, zoom_out.getNewMouseTool() )
		self.addMouseInstantTool( 'zoom_in.ppm', gridPosition, zoom_in.getNewMouseTool() )
		gridPosition.increment()
		preferences.Tkinter.Label( gridPosition.master, text = 'Scale:' ).grid( row = gridPosition.row, column = gridPosition.column, sticky = preferences.Tkinter.W )
		gridPosition.increment()
		self.scaleEntry = preferences.Tkinter.Spinbox( gridPosition.master, command = self.scaleEntryReturnPressed, from_ = 10.0, increment = 5.0, to = 100.0 )
		self.scaleEntry.bind( '<Return>', self.scaleEntryReturnPressed )
		self.scaleEntry.grid( row = gridPosition.row, column = gridPosition.column, sticky = preferences.Tkinter.W )

	def addSettingsMenuSetWindowGeometry( self, center ):
		"Add the settings menu, center the scroll region, update, and set the window geometry."
		self.preferencesMenu = preferences.Tkinter.Menu( self.fileHelpMenuBar.menuBar, tearoff = 0 )
		self.fileHelpMenuBar.addMenuToMenuBar( "Settings", self.preferencesMenu )
		preferences.addMenuEntitiesToMenuFrameable( self.preferencesMenu, self.repository.menuEntities )
		self.relayXview( preferences.Tkinter.MOVETO, center.real - self.canvasScreenCenter.real )
		self.relayYview( preferences.Tkinter.MOVETO, center.imag - self.canvasScreenCenter.imag )
		self.root.withdraw()
		self.root.update_idletasks()
		movedGeometryString = '%sx%s+%s' % ( self.root.winfo_reqwidth(), self.root.winfo_reqheight(), '0+0' )
		self.root.geometry( movedGeometryString )
		self.repository.activateMouseModeTool = self.activateMouseModeTool
		self.repository.phoenixUpdateFunction = self.phoenixUpdate
		self.repository.redisplayWindowUpdateFunction = self.redisplayWindowUpdate
		self.repository.updateFunction = self.update

	def button1( self, event ):
		"The button was clicked."
		self.mouseTool.button1( event )

	def buttonRelease1( self, event ):
		"The button was released."
		self.mouseTool.buttonRelease1( event )

	def cancelTimer( self, event = None ):
		"Cancel the timer and set it to none."
		if self.timerID != None:
			self.canvas.after_cancel ( self.timerID )
			self.timerID = None

	def cancelTimerResetButtons( self ):
		"Cancel the timer and set it to none."
		self.cancelTimer()
		self.resetPeriodicButtonsText()

	def close( self, event = None ):
		"The dialog was closed."
		try:
			self.root.after( 1, self.root.destroy ) # to get around 'Font Helvetica -12 still in cache.' segmentation bug, instead of simply calling self.root.destroy()
		except:
			pass

	def createMouseModeTool( self ):
		"Create the mouse mode tool."
		self.destroyMouseToolRaiseMouseButtons()
		for menuRadio in self.repository.mouseMode.menuRadios:
			if menuRadio.value:
				self.mouseTool = menuRadio.mouseTool
				menuRadio.mouseButton[ 'relief' ] = preferences.Tkinter.SUNKEN

	def destroyAllDialogWindows( self ):
		"Destroy all the dialog windows."
		preferences.writePreferences( self.repository )
		return
		for menuEntity in self.repository.menuEntities:
			lowerName = menuEntity.name.lower()
			if lowerName in preferences.globalRepositoryDialogListTable:
				globalRepositoryDialogValues = preferences.globalRepositoryDialogListTable[ lowerName ]
				for globalRepositoryDialogValue in globalRepositoryDialogValues:
					preferences.quitWindow( globalRepositoryDialogValue.root )

	def destroyMouseToolRaiseMouseButtons( self ):
		"Destroy the mouse tool and raise the mouse buttons."
		self.mouseTool.destroyEverything()
		for menuRadio in self.repository.mouseMode.menuRadios:
			menuRadio.mouseButton[ 'relief' ] = preferences.Tkinter.RAISED
		for mouseInstantButton in self.mouseInstantButtons:
			mouseInstantButton[ 'relief' ] = preferences.Tkinter.RAISED

	def dive( self ):
		"Dive, go down periodically."
		oldDiveButtonText = self.diveButton[ 'text' ]
		self.cancelTimerResetButtons()
		if oldDiveButtonText == 'stop':
			return
		self.diveCycle()

	def diveCycle( self ):
		"Start the dive cycle."
		self.cancelTimer()
		self.repository.layer.value -= 1
		self.update()
		if self.repository.layer.value < 1:
			self.resetPeriodicButtonsText()
			return
		self.setButtonImageText( self.diveButton, 'stop' )
		self.timerID = self.canvas.after( self.getSlideShowDelay(), self.diveCycle )

	def getAnimationLineDelay( self, coloredLine ):
		"Get the animation line delay in milliseconds."
#		maybe later, add animation along line
#		nextLayerIndex = self.repository.layer.value
#		nextLineIndex = self.repository.line.value + 1
#		coloredLinesLength = len( self.getColoredLines() )
#		self.skein.feedRateMinute
#		if nextLineIndex >= coloredLinesLength:
#			if nextLayerIndex + 1 < len( self.skeinPanes ):
#				nextLayerIndex += 1
#				nextLineIndex = 0
#			else:
#				nextLineIndex = self.repository.line.value
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( coloredLine.displayString )
		self.skein.feedRateMinute = gcodec.getFeedRateMinute( self.skein.feedRateMinute, splitLine )
		feedRateSecond = self.skein.feedRateMinute / 60.0
		coloredLineLength = abs( coloredLine.end - coloredLine.begin ) / self.repository.scale.value
		duration = coloredLineLength / feedRateSecond
		animationLineDelay = int( round( 1000.0 * duration / self.repository.animationLineQuickening.value ) )
		return max( animationLineDelay, 1 )

	def getDrawnLineText( self, location, tags, text ):
		"Get the line text drawn on the canvas."
		anchorTowardCenter = preferences.Tkinter.N
		if location.imag > float( self.canvasHeight ) * 0.1:
			anchorTowardCenter = preferences.Tkinter.S
		if location.real > float( self.canvasWidth ) * 0.7:
			anchorTowardCenter += preferences.Tkinter.E
		else:
			anchorTowardCenter += preferences.Tkinter.W
		return self.canvas.create_text( int( location.real ), int( location.imag ), anchor = anchorTowardCenter, tags = tags, text = text )

	def getEntityFromName( self, name ):
		"Get the entity of the given name."
		for entity in self.repository.displayEntities:
			if entity.name == name:
				return entity
		return None

	def getPhotoButtonGridIncrement( self, commandFunction, fileName, gridPosition ):
		"Get a PhotoImage button, grid the button and increment the grid position."
		gridPosition.increment()
		untilDotFileName = self.addPhotoImage( fileName, gridPosition )
		photoImage = self.photoImages[ untilDotFileName ]
		photoButton = preferences.Tkinter.Button( gridPosition.master, activebackground = 'black', activeforeground = 'white', command = commandFunction, text = untilDotFileName )
		if photoImage != None:
			photoButton[ 'image' ] = photoImage
		photoButton.grid( row = gridPosition.row, column = gridPosition.column, sticky = preferences.Tkinter.W )
		return photoButton

	def getScrollPaneCenter( self ):
		"Get the center of the scroll pane."
		return self.getScrollPaneFraction() + self.canvasScreenCenter

	def getScrollPaneFraction( self ):
		"Get the center of the scroll pane."
		return complex( self.xScrollbar.get()[ 0 ], self.yScrollbar.get()[ 0 ] )

	def getSlideShowDelay( self ):
		"Get the slide show delay in milliseconds."
		slideShowDelay = int( round( 1000.0 / self.repository.animationSlideShowRate.value ) )
		return max( slideShowDelay, 1 )

	def isLineBelowZeroSetLayer( self ):
		"Determine if the line index is below zero, and if so set the layer index."
		if self.repository.line.value < 0:
			self.repository.line.value = 0
			self.setLayerIndex( self.repository.layer.value - 1 )
			return True
		return False

	def isLineBeyondListSetLayer( self ):
		"Determine if the line index is beyond the end of the list, and if so set the layer index."
		coloredLinesLength = len( self.getColoredLines() )
		if self.repository.line.value >= coloredLinesLength:
			self.repository.line.value = coloredLinesLength - 1
			self.setLayerIndex( self.repository.layer.value + 1 )
			return True
		return False

	def keyPressDown( self, event ):
		"The down arrow was pressed."
		self.mouseTool.keyPressDown( event )

	def keyPressLeft( self, event ):
		"The left arrow was pressed."
		self.mouseTool.keyPressLeft( event )

	def keyPressReturn( self, event ):
		"The return key was pressed."
		self.mouseTool.keyPressReturn( event )

	def keyPressRight( self, event ):
		"The right arrow was pressed."
		self.mouseTool.keyPressRight( event )

	def keyPressUp( self, event ):
		"The up arrow was pressed."
		self.mouseTool.keyPressUp( event )

	def layerEntryReturnPressed( self, event = None ):
		"The layer index entry return was pressed."
		self.setLayerIndex( int( self.layerEntry.get() ) )

	def limitIndex( self ):
		"Limit the index so it is not below zero or above the top."
		self.repository.layer.value = max( 0, self.repository.layer.value )
		self.repository.layer.value = min( len( self.skeinPanes ) - 1, self.repository.layer.value )

	def limitIndexSetArrowMouseDeleteCanvas( self ):
		"Limit the index, set the arrow type, and delete all the canvas items."
		self.limitIndex()
		self.arrowType = None
		if self.repository.drawArrows.value:
			self.arrowType = 'last'
		self.canvas.delete( preferences.Tkinter.ALL )

	def lineEntryReturnPressed( self, event = None ):
		"The line index entry return was pressed."
		self.repository.line.value = int( self.lineEntry.get() )
		if self.isLineBelowZeroSetLayer():
			return
		if self.isLineBeyondListSetLayer():
			return
		self.cancelTimerResetButtons()
		self.updateMouseToolIfSelection()
		self.setLineButtonsState()

	def lineDive( self ):
		"Line dive, go down periodically."
		oldLineDiveButtonText = self.lineDiveButton[ 'text' ]
		self.cancelTimerResetButtons()
		if oldLineDiveButtonText == 'stop':
			return
		self.lineDiveCycle()

	def lineDiveCycle( self ):
		"Start the line dive cycle."
		self.cancelTimer()
		self.repository.line.value -= 1
		if self.repository.line.value < 0:
			self.repository.line.value = 0
			if self.repository.layer.value == 0:
				self.resetPeriodicButtonsText()
				self.setLineButtonsState()
				return
			self.setLayerIndex( self.repository.layer.value - 1 )
		else:
			self.updateMouseToolIfSelection()
		self.setLineButtonsState()
		self.setButtonImageText( self.lineDiveButton, 'stop' )
		coloredLine = self.getColoredLines()[ self.repository.line.value ]
		self.timerID = self.canvas.after( self.getAnimationLineDelay( coloredLine ), self.lineDiveCycle )

	def lineSoar( self ):
		"Line soar, go up periodically."
		oldLineSoarButtonText = self.lineSoarButton[ 'text' ]
		self.cancelTimerResetButtons()
		if oldLineSoarButtonText == 'stop':
			return
		self.lineSoarCycle()

	def lineSoarCycle( self ):
		"Start the line soar cycle."
		self.cancelTimer()
		self.repository.line.value += 1
		coloredLinesLength = len( self.getColoredLines() )
		if self.repository.line.value >= coloredLinesLength:
			self.repository.line.value = coloredLinesLength - 1
			if self.repository.layer.value > len( self.skeinPanes ) - 2:
				self.resetPeriodicButtonsText()
				self.setLineButtonsState()
				return
			self.setLayerIndex( self.repository.layer.value + 1 )
		else:
			self.updateMouseToolIfSelection()
		self.setLineButtonsState()
		self.setButtonImageText( self.lineSoarButton, 'stop' )
		coloredLine = self.getColoredLines()[ self.repository.line.value ]
		self.timerID = self.canvas.after( self.getAnimationLineDelay( coloredLine ), self.lineSoarCycle )

	def motion( self, event ):
		"The mouse moved."
		self.mouseTool.motion( event )

	def phoenixUpdate( self ):
		"Update the skein, and deiconify a new window and destroy the old."
		self.updateNewDestroyOld( self.getScrollPaneCenter() )

	def relayXview( self, *args ):
		"Relay xview changes."
		self.canvas.xview( *args )

	def relayYview( self, *args ):
		"Relay yview changes."
		self.canvas.yview( *args )

	def resetPeriodicButtonsText( self ):
		"Reset the text of the periodic buttons."
		self.setButtonImageText( self.diveButton, 'dive' )
		self.setButtonImageText( self.soarButton, 'soar' )
		self.setButtonImageText( self.lineDiveButton, 'dive' )
		self.setButtonImageText( self.lineSoarButton, 'soar' )

	def redisplayWindowUpdate( self ):
		"Deiconify a new window and destroy the old."
		self.getCopy().updateDeiconify( self.getScrollPaneCenter() )
		self.root.after( 1, self.root.destroy ) # to get around 'Font Helvetica -12 still in cache.' segmentation bug, instead of simply calling self.root.destroy()

	def save( self ):
		"Set the preference values to the display, save the new values."
		for menuEntity in self.repository.menuEntities:
			if menuEntity in self.repository.archive:
				menuEntity.setToDisplay()
		self.setInsetToDisplay()
		preferences.writePreferences( self.repository )

	def scaleEntryReturnPressed( self, event = None ):
		"The scale entry return was pressed."
		self.repository.scale.value = float( self.scaleEntry.get() )
		self.phoenixUpdate()

	def setButtonImageText( self, button, text ):
		"Set the text of the e periodic buttons."
		photoImage = self.photoImages[ text ]
		if photoImage != None:
			button[ 'image' ] = photoImage
		button[ 'text' ] = text

	def setDisplayLayerIndex( self ):
		"Set the display of the layer index entry field and buttons."
		coloredLines = self.getColoredLines()
		isAboveFloor = self.repository.layer.value > 0
		isBelowCeiling = self.repository.layer.value < len( self.skeinPanes ) - 1
		setStateNormalDisabled( isAboveFloor, self.diveButton )
		setStateNormalDisabled( isBelowCeiling, self.soarButton )
		self.setLineButtonsState()
		preferences.setEntryText( self.layerEntry, self.repository.layer.value )
		preferences.setEntryText( self.lineEntry, self.repository.line.value )
		preferences.setEntryText( self.scaleEntry, self.repository.scale.value )
		self.mouseTool.update()
		self.setInsetToDisplay()

	def setInsetToDisplay( self ):
		"Set the archive to the display."
		if self.root.state() != 'normal':
			return
		xScrollbarCanvasPortion = getScrollbarCanvasPortion( self.xScrollbar )
#		if xScrollbarCanvasPortion < .99:
		width = int( round( ( xScrollbarCanvasPortion ) * float( int( self.skein.screenSize.real ) ) ) )
		newScreenHorizontalInset = self.root.winfo_screenwidth() - width
		if abs( newScreenHorizontalInset - self.repository.screenHorizontalInset.value ) > 1:
			self.repository.screenHorizontalInset.value = min( self.repository.screenHorizontalInset.value, newScreenHorizontalInset )
		yScrollbarCanvasPortion = getScrollbarCanvasPortion( self.yScrollbar )
#		if yScrollbarCanvasPortion < .99:
		height = int( round( ( yScrollbarCanvasPortion ) * float( int( self.skein.screenSize.imag ) ) ) )
		newScreenVerticalInset = self.root.winfo_screenheight() - height
		if abs( newScreenVerticalInset - self.repository.screenVerticalInset.value ) > 1:
			self.repository.screenVerticalInset.value = min( self.repository.screenVerticalInset.value, newScreenVerticalInset )

	def setLayerIndex( self, layerIndex ):
		"Set the layer index."
		self.cancelTimerResetButtons()
		oldLayerIndex = self.repository.layer.value
		self.repository.layer.value = layerIndex
		self.limitIndex()
		coloredLines = self.getColoredLines()
		if self.repository.layer.value < oldLayerIndex:
			self.repository.line.value = len( coloredLines ) - 1
			self.lineEntry[ 'to' ] = len( coloredLines ) - 1
		if self.repository.layer.value > oldLayerIndex:
			self.repository.line.value = 0
			self.lineEntry[ 'to' ] = len( coloredLines ) - 1
		self.update()

	def setLineButtonsState( self ):
		"Set the state of the line buttons."
		coloredLines = self.getColoredLines()
		isAboveFloor = self.repository.layer.value > 0
		isBelowCeiling = self.repository.layer.value < len( self.skeinPanes ) - 1
		setStateNormalDisabled( isAboveFloor or self.repository.line.value > 0, self.lineDiveButton )
		setStateNormalDisabled( isBelowCeiling or self.repository.line.value < len( coloredLines ) - 1, self.lineSoarButton )

	def shiftButtonRelease1( self, event ):
		"The button was released while the shift key was pressed."
		self.mouseTool.buttonRelease1( event, True )

	def shiftMotion( self, event ):
		"The mouse moved."
		self.mouseTool.motion( event, True )

	def soar( self ):
		"Soar, go up periodically."
		oldSoarButtonText = self.soarButton[ 'text' ]
		self.cancelTimerResetButtons()
		if oldSoarButtonText == 'stop':
			return
		self.soarCycle()

	def soarCycle( self ):
		"Start the soar cycle."
		self.cancelTimer()
		self.repository.layer.value += 1
		self.update()
		if self.repository.layer.value > len( self.skeinPanes ) - 2:
			self.resetPeriodicButtonsText()
			return
		self.setButtonImageText( self.soarButton, 'stop' )
		self.timerID = self.canvas.after( self.getSlideShowDelay(), self.soarCycle )

	def updateDeiconify( self, center = complex( 0.5, 0.5 ) ):
		"Update and deiconify the window."
		self.addSettingsMenuSetWindowGeometry( center )
		self.update()
		self.root.deiconify()

	def updateMouseToolIfSelection( self ):
		"Update the mouse tool if it is a selection tool."
		if self.mouseTool == None:
			return
		if self.mouseTool.isSelectionTool():
			self.mouseTool.update()

	def updateNewDestroyOld( self, scrollPaneCenter ):
		"Update and deiconify a window and destroy the old."
		self.getCopyWithNewSkein().updateDeiconify( scrollPaneCenter )
		self.root.after( 1, self.root.destroy ) # to get around 'Font Helvetica -12 still in cache.' segmentation bug, instead of simply calling self.root.destroy()
