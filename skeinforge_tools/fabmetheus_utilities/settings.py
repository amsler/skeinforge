"""
Settings is a collection of utilities to display, read & write the settings and position widgets.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.fabmetheus_utilities import euclidean
from skeinforge_tools.fabmetheus_utilities import gcodec
import cStringIO
import os
import shutil
import webbrowser
try:
	import Tkinter
except:
	print( 'You do not have Tkinter, which is needed for the graphical interface, you will only be able to use the command line.' )
	print( 'Information on how to download Tkinter is at:\nwww.tcl.tk/software/tcltk/' )


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/23/04 $"
__license__ = "GPL 3.0"

globalRepositoryDialogListTable = {}
globalProfileSaveListenerListTable = {}
globalCloseListTables = [ globalRepositoryDialogListTable, globalProfileSaveListenerListTable ]
globalSpreadsheetSeparator = '\t'


def addAcceleratorCommand( acceleratorBinding, commandFunction, master, menu, text ):
	"Add accelerator command."
	acceleratorText = acceleratorBinding[ 1 : - 1 ]
	lastIndexOfMinus = acceleratorText.rfind( '-' )
	if lastIndexOfMinus > - 1:
		acceleratorText = acceleratorText[ : lastIndexOfMinus + 1 ] + acceleratorText[ lastIndexOfMinus + 1 : ].capitalize()
	acceleratorText = acceleratorText.replace( 'KeyPress-', '' )
	acceleratorText = acceleratorText.replace( '-', '+' )
	acceleratorText = acceleratorText.replace( 'Control', 'Ctrl' )
	acceleratorBinding = acceleratorBinding.replace( 'KeyPress', '' )
	menu.add_command( accelerator = acceleratorText, label = text, underline = 0, command = commandFunction )
	master.bind( acceleratorBinding, commandFunction )

def addEmptyRow( gridPosition ):
	"Add an empty row."
	gridPosition.increment()
	Tkinter.Label( gridPosition.master ).grid( row = gridPosition.row, column = gridPosition.column )

def addListsToRepository( fileNameHelp, profileDirectory, repository ):
	"Add the value to the lists."
	repository.archive = []
	repository.displayEntities = []
	repository.executeTitle = None
	repository.fileNameHelp = fileNameHelp
	repository.fileNameInput = None
	repository.lowerName = fileNameHelp.split( '.' )[ - 2 ]
	repository.baseName = repository.lowerName + '.csv'
	repository.capitalizedName = getEachWordCapitalized( repository.lowerName )
	repository.openLocalHelpPage = HelpPage().getOpenFromDocumentationSubName( repository.fileNameHelp )
	repository.openWikiManualHelpPage = None
	repository.profileDirectory = profileDirectory
	repository.repositoryDialog = None
	repository.saveListenerTable = {}
	repository.title = repository.capitalizedName + ' Settings'
	repository.menuEntities = []
	repository.saveCloseTitle = 'Save and Close'
	repository.windowPosition = WindowPosition().getFromValue( repository, '0+0' )
	WindowVisibilities().getFromRepository( repository )
	for setting in repository.archive:
		setting.repository = repository

def addMenuEntitiesToMenu( menu, menuEntities ):
	"Add the menu entities to the menu."
	for menuEntity in menuEntities:
		menuEntity.addToMenu( menu )

def addMenuEntitiesToMenuFrameable( menu, menuEntities ):
	"Add the menu entities to the menu."
	for menuEntity in menuEntities:
		menuEntity.addToMenuFrameable( menu )

def addPluginsParentToMenu( directoryPath, menu, parentPath, pluginFileNames ):
	"Add plugins and the parent to the menu."
	ToolDialog().addPluginToMenu( menu, parentPath[ : parentPath.rfind( '.' ) ] )
	menu.add_separator()
	addPluginsToMenu( directoryPath, menu, pluginFileNames )

def addPluginsToMenu( directoryPath, menu, pluginFileNames ):
	"Add plugins to the menu."
	for pluginFileName in pluginFileNames:
		ToolDialog().addPluginToMenu( menu, os.path.join( directoryPath, pluginFileName ) )

def cancelRepository( repository ):
	"Read the repository then set all the entities to the read archive values."
	getReadRepository( repository )
	for setting in repository.displayEntities:
		if setting in repository.archive:
			setting.setStateToValue()

def deleteDirectory( directory, subfolderName ):
	"Delete the directory if it exists."
	subDirectory = os.path.join( directory, subfolderName )
	if os.path.isdir( subDirectory ):
		shutil.rmtree( subDirectory )

def deleteMenuItems( menu ):
	"Delete the menu items."
	try:
		lastMenuIndex = menu.index( Tkinter.END )
		if lastMenuIndex != None:
			menu.delete( 0, lastMenuIndex )
	except:
		print( 'this should never happen, the lastMenuIndex in deleteMenuItems in settings could not be determined.' ) 

def getAlongWayHexadecimalColor( beginBrightness, colorWidth, difference, endColorTuple, wayLength ):
	"Get a color along the way from begin brightness to the end color."
	alongWay = 1.0
	if wayLength != 0.0:
		alongWay = min( 1.0, float( difference ) / float( wayLength ) )
	hexadecimalColor = '#'
	oneMinusAlongWay = 1.0 - alongWay
	for primaryIndex in xrange( 3 ):
		hexadecimalColor += getAlongWayHexadecimalPrimary( beginBrightness, oneMinusAlongWay, colorWidth, endColorTuple[ primaryIndex ], alongWay )
	return hexadecimalColor

def getAlongWayHexadecimalPrimary( beginBrightness, beginRatio, colorWidth, endBrightness, endRatio ):
	"Get a primary color along the way from grey to the end color."
	brightness = beginRatio * float( beginBrightness ) + endRatio * float( endBrightness )
	return getWidthHex( int( round( brightness ) ), colorWidth )

def getArchiveText( repository ):
	"Get the text representation of the archive."
	archiveWriter = cStringIO.StringIO()
	archiveWriter.write( 'Format is tab separated %s.\n' % repository.title.lower() )
	archiveWriter.write( 'Name                          %sValue\n' % globalSpreadsheetSeparator )
	for setting in repository.archive:
		setting.writeToArchiveWriter( archiveWriter )
	return archiveWriter.getvalue()

def getDirectoryInAboveDirectory( directory ):
	"Get the directory in the above directory."
	aboveDirectory = os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )
	return os.path.join( aboveDirectory, directory )

def getDisplayedDialogFromConstructor( repository ):
	"Display the repository dialog."
	getReadRepository( repository )
	return RepositoryDialog( repository, Tkinter.Tk() )
	try:
		getReadRepository( repository )
		return RepositoryDialog( repository, Tkinter.Tk() )
	except:
		print( 'this should never happen, getDisplayedDialogFromConstructor in settings could not open' )
		print( repository )
		return None

def getDisplayedDialogFromPath( path ):
	"Display the repository dialog."
	pluginModule = gcodec.getModuleWithPath( path )
	if pluginModule == None:
		return None
	return getDisplayedDialogFromConstructor( pluginModule.getNewRepository() )

def getDisplayToolButtonsRepository( directoryPath, importantFileNames, names, repository ):
	"Get the display tool buttons."
	displayToolButtons = []
	for name in names:
		displayToolButton = DisplayToolButton().getFromPath( name in importantFileNames, name, os.path.join( directoryPath, name ), repository )
		displayToolButtons.append( displayToolButton )
	return displayToolButtons

def getDocumentationPath( subName = '' ):
	"Get the documentation file path."
	numberOfLevelsDeepInPackageHierarchy = 2
	packageFilePath = os.path.abspath( __file__ )
	for level in xrange( numberOfLevelsDeepInPackageHierarchy + 1 ):
		packageFilePath = os.path.dirname( packageFilePath )
	documentationIndexPath = os.path.join( packageFilePath, 'documentation' )
	return os.path.join( documentationIndexPath, subName )

def getEachWordCapitalized( name ):
	"Get the capitalized name."
	withSpaces = name.lower().replace( '_', ' ' )
	words = withSpaces.split( ' ' )
	capitalizedStrings = []
	for word in words:
		capitalizedStrings.append( word.capitalize() )
	return ' '.join( capitalizedStrings )

def getFileInAlterationsOrGivenDirectory( directory, fileName ):
	"Get the file from the fileName or the lowercase fileName in the alterations directories, if there is no file look in the given directory."
	settingsAlterationsDirectory = getSettingsDirectoryPath( 'alterations' )
	makeDirectory( settingsAlterationsDirectory )
	fileInSettingsAlterationsDirectory = getFileInGivenDirectory( settingsAlterationsDirectory, fileName )
	if fileInSettingsAlterationsDirectory != '':
		return fileInSettingsAlterationsDirectory
	alterationsDirectory = getDirectoryInAboveDirectory( 'alterations' )
	fileInAlterationsDirectory = getFileInGivenDirectory( alterationsDirectory, fileName )
	if fileInAlterationsDirectory != '':
		return fileInAlterationsDirectory
	if directory == '':
		directory = os.getcwd()
	return getFileInGivenDirectory( directory, fileName )

def getFileInGivenDirectory( directory, fileName ):
	"Get the file from the fileName or the lowercase fileName in the given directory."
	directoryListing = os.listdir( directory )
	lowerFileName = fileName.lower()
	for directoryFile in directoryListing:
		if directoryFile.lower() == lowerFileName:
			return getFileTextGivenDirectoryFileName( directory, directoryFile )
	return ''

def getFileTextGivenDirectoryFileName( directory, fileName ):
	"Get the entire text of a file with the given file name in the given directory."
	absoluteFilePath = os.path.join( directory, fileName )
	return gcodec.getFileText( absoluteFilePath )

def getFolders( directory ):
	"Get the folder list in a directory."
	makeDirectory( directory )
	directoryListing = []
	try:
		directoryListing = os.listdir( directory )
	except OSError:
		print( 'Skeinforge can not list the directory:' )
		print( directory )
		print( 'so give it read/write permission for that directory.' )
	folders = []
	for fileName in directoryListing:
		if os.path.isdir( os.path.join( directory, fileName ) ):
			folders.append( fileName )
	return folders

def getGlobalRepositoryDialogValues():
	"Get the global repository dialog values."
	global globalRepositoryDialogListTable
	return euclidean.getListTableElements( globalRepositoryDialogListTable )

def getPathFromFileNameHelp( fileNameHelp ):
	"Get the directory path from file name help."
	skeinforgePath = getSkeinforgeDirectoryPath()
	splitFileNameHelps = fileNameHelp.split( '.' )
	splitFileNameDirectoryNames = splitFileNameHelps[ : - 1 ]
	for splitFileNameDirectoryName in splitFileNameDirectoryNames:
		skeinforgePath = os.path.join( skeinforgePath, splitFileNameDirectoryName )
	return skeinforgePath

def getProfileBaseName( repository ):
	"Get the profile base file name."
	if repository.profileDirectory == '':
		return repository.baseName
	return os.path.join( repository.profileDirectory(), repository.baseName )

def getProfilesDirectoryPath( subfolder = '' ):
	"Get the profiles directory path, which is the settings directory joined with profiles."
	profilesDirectory = getSettingsDirectoryPath( 'profiles' )
	if subfolder == '':
		return profilesDirectory
	return os.path.join( profilesDirectory, subfolder )

def getProfilesDirectoryInAboveDirectory( subName = '' ):
	"Get the profiles directory path in the above directory."
	aboveProfilesDirectory = getDirectoryInAboveDirectory( 'profiles' )
	if subName == '':
		return aboveProfilesDirectory
	return os.path.join( aboveProfilesDirectory, subName )

def getRadioPluginsAddPluginFrame( directoryPath, importantFileNames, names, repository ):
	"Get the radio plugins and add the plugin frame."
	repository.pluginFrame = PluginFrame()
	radioPlugins = []
	for name in names:
		radioPlugin = RadioPlugin().getFromRadio( name in importantFileNames, repository.pluginFrame.latentStringVar, name, repository, name == importantFileNames[ 0 ] )
		radioPlugin.updateFunction = repository.pluginFrame.update
		radioPlugins.append( radioPlugin )
	defaultRadioButton = getSelectedRadioPlugin( importantFileNames + [ radioPlugins[ 0 ].name ], radioPlugins )
	repository.pluginFrame.getFromPath( defaultRadioButton, directoryPath, repository )
	return radioPlugins

def getReadRepository( repository ):
	"Read and return settings from a file."
	text = gcodec.getFileText( getProfilesDirectoryPath( getProfileBaseName( repository ) ), 'r', False )
	if text == '':
		print( 'The default %s will be written in the .skeinforge folder in the home directory.' % repository.title.lower() )
		text = gcodec.getFileText( getProfilesDirectoryInAboveDirectory( getProfileBaseName( repository ) ), 'r', False )
		if text != '':
			readSettingsFromText( repository, text )
		writeSettings( repository )
		return repository
	readSettingsFromText( repository, text )
	return repository

def getSelectedPluginModuleFromPath( filePath, plugins ):
	"Get the selected plugin module."
	for plugin in plugins:
		if plugin.value:
			return gcodec.getModuleFromPath( plugin.name, filePath )
	return None

def getSelectedPluginName( plugins ):
	"Get the selected plugin name."
	for plugin in plugins:
		if plugin.value:
			return plugin.name
	return ''

def getSelectedRadioPlugin( names, radioPlugins ):
	"Get the selected radio button if it exists, None otherwise."
	for radioPlugin in radioPlugins:
		if radioPlugin.value:
			return radioPlugin
	for name in names:
		for radioPlugin in radioPlugins:
			if radioPlugin.name == name:
				radioPlugin.value = True
				return radioPlugin
	print( 'this should never happen, no getSelectedRadioPlugin in settings' )
	print( names )
	return radioPlugin[ 0 ]

def getSettingsDirectoryPath( subfolder = '' ):
	"Get the settings directory path, which is the home directory joined with .skeinforge."
	settingsDirectory = os.path.join( os.path.expanduser( '~' ), '.skeinforge' )
	if subfolder == '':
		return settingsDirectory
	return os.path.join( settingsDirectory, subfolder )

def getSkeinforgeToolsDirectoryPath():
	"Get the skeinforge tools directory path."
	return os.path.dirname( os.path.dirname( os.path.abspath( __file__ ) ) )

def getSkeinforgeDirectoryPath():
	"Get the skeinforge directory path."
	return os.path.dirname( getSkeinforgeToolsDirectoryPath() )

def getSubfolderWithBasename( basename, directory ):
	"Get the subfolder in the directory with the basename."
	makeDirectory( directory )
	directoryListing = os.listdir( directory )
	for fileName in directoryListing:
		joinedFileName = os.path.join( directory, fileName )
		if os.path.isdir( joinedFileName ):
			if basename == fileName:
				return joinedFileName
	return None

def getTitleFromName( title ):
	"Get the title of this setting."
	if title[ - 1 ] == ':':
		title = title[ : - 1 ]
	spaceBracketIndex = title.find( ' (' )
	if spaceBracketIndex > - 1:
		return title[ : spaceBracketIndex ]
	return title

def getWidthHex( number, width ):
	"Get the first width hexadecimal digits."
	return ( '0000%s' % hex( number )[ 2 : ] )[ - width : ]

def liftRepositoryDialogs( repositoryDialogs ):
	"Lift the repository dialogs."
	for repositoryDialog in repositoryDialogs:
		repositoryDialog.root.withdraw() # the withdraw & deiconify trick is here because lift does not work properly on my linux computer
		repositoryDialog.root.lift() # probably not necessary, here in case the withdraw & deiconify trick does not work on some other computer
		repositoryDialog.root.deiconify()
		repositoryDialog.root.lift() # probably not necessary, here in case the withdraw & deiconify trick does not work on some other computer
		repositoryDialog.root.update_idletasks()

def makeDirectory( directory ):
	"Make a directory if it does not already exist."
	if os.path.isdir( directory ):
		return
	try:
		os.makedirs( directory )
	except OSError:
		print( 'Skeinforge can not make the directory %s so give it read/write permission for that directory and the containing directory.' % directory )

def openWebPage( webPagePath ):
	"Open a web page in a browser."
	if webPagePath.find( '#' ) != - 1: # to get around # encode bug
		redirectionText = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">\n<html>\n<head>\n'
		redirectionText += '<meta http-equiv="REFRESH" content="0;url=%s"></head>\n</HTML>\n' % webPagePath
		webPagePath = getDocumentationPath( 'redirect.html' )
		gcodec.writeFileText( webPagePath, redirectionText )
	webPagePath = '"%s"' % webPagePath # " to get around space in url bug
	try:
		os.startfile( webPagePath )#this is available on some python environments, but not all
		return
	except:
		pass
	webbrowserName = webbrowser.get().name
	if webbrowserName == '':
		print( 'Skeinforge was not able to open the documentation file in a web browser.  To see the documentation, open the following file in a web browser:' )
		print( webPagePath )
		return
	os.system( webbrowserName + ' ' + webPagePath )#used this instead of webbrowser.open() to workaround webbrowser open() bug

def quitWindow( root ):
	"Quit a window."
	try:
		root.destroy()
	except:
		pass

def quitWindows( event = None ):
	"Quit all windows."
	global globalRepositoryDialogListTable
	globalRepositoryDialogValues = euclidean.getListTableElements( globalRepositoryDialogListTable )
	for globalRepositoryDialogValue in globalRepositoryDialogValues:
		quitWindow( globalRepositoryDialogValue.root )

def readSettingsFromText( repository, text ):
	"Read settings from a text."
	lines = gcodec.getTextLines( text )
	settingTable = {}
	for setting in repository.archive:
		settingTable[ setting.name ] = setting
	for lineIndex in xrange( len( lines ) ):
		setArchiveToLine( lineIndex, lines, settingTable )

def saveAll():
	"Save all the dialogs."
	for globalRepositoryDialogValue in getGlobalRepositoryDialogValues():
		globalRepositoryDialogValue.save()

def saveRepository( repository ):
	"Set the entities to the dialog then write them."
	for setting in repository.archive:
		setting.setToDisplay()
	writeSettingsPrintMessage( repository )
	for saveListener in repository.saveListenerTable.values():
		saveListener()

def setArchiveToLine( lineIndex, lines, settingTable ):
	"Set an archive to a setting line."
	line = lines[ lineIndex ]
	splitLine = line.split( globalSpreadsheetSeparator )
	if len( splitLine ) < 2:
		return
	fileSettingName = splitLine[ 0 ]
	if fileSettingName in settingTable:
		settingTable[ fileSettingName ].setValueToSplitLine( lineIndex, lines, splitLine )

def setButtonFontWeightString( button, isBold ):
	"Set button font weight given isBold."
	try:
		weightString = 'normal'
		if isBold:
			weightString = 'bold'
		splitFont = button[ 'font' ].split()
		button[ 'font' ] = ( splitFont[ 0 ], splitFont[ 1 ], weightString )
	except:
		pass

def setEntryText( entry, value ):
	"Set the entry text."
	if entry == None:
		return
	entry.delete( 0, Tkinter.END )
	entry.insert( 0, str( value ) )

def setIntegerValueToString( integerSetting, valueString ):
	"Set the integer to the string."
	dotIndex = valueString.find( '.' )
	if dotIndex > - 1:
		valueString = valueString[ : dotIndex ]
	try:
		integerSetting.value = int( valueString )
		return
	except:
		print( 'Warning, can not read integer ' + integerSetting.name + ' ' + valueString )
		print( 'Will try reading as a boolean, which might be a mistake.' )
	integerSetting.value = 0
	if valueString.lower() == 'true':
		integerSetting.value = 1

def setSpinColor( setting ):
	"Set the spin box color to the value, yellow if it is lower than the default and blue if it is higher."
	if setting.entry == None:
		return
	if setting.backgroundColor == None:
		setting.backgroundColor = setting.entry[ 'background' ]
		if setting.backgroundColor[ 0 ] != '#':
			setting.backgroundColor = '#ffffff'
		setting.colorWidth = len( setting.backgroundColor ) / 3
		setting.grey = int( setting.backgroundColor[ 1 : 1 + setting.colorWidth ], 16 )
		setting.white = int( 'f' * setting.colorWidth, 16 )
	if abs( setting.value - setting.defaultValue ) < 0.02 * setting.width:
		setting.entry[ 'background' ] = setting.backgroundColor
		return
	difference = setting.value - setting.defaultValue
	if difference > 0.0:
		wayLength = setting.to - setting.defaultValue
		setting.entry[ 'background' ] = getAlongWayHexadecimalColor( setting.grey, setting.colorWidth, difference, ( 0, setting.white, setting.white ), wayLength )
		return
	wayLength = setting.from_ - setting.defaultValue
	setting.entry[ 'background' ] = getAlongWayHexadecimalColor( setting.grey, setting.colorWidth, difference, ( setting.white, setting.white, 0 ), wayLength )

def startMainLoopFromConstructor( repository ):
	"Display the repository dialog and start the main loop."
	getDisplayedDialogFromConstructor( repository ).root.mainloop()

def writeValueListToArchiveWriter( archiveWriter, setting ):
	"Write tab separated name and list to the archive writer."
	archiveWriter.write( setting.name )
	for item in setting.value:
		if item != '[]':
			archiveWriter.write( globalSpreadsheetSeparator )
			archiveWriter.write( item )
	archiveWriter.write( '\n' )

def writeSettings( repository ):
	"Write the settings to a file."
	profilesDirectoryPath = getProfilesDirectoryPath( getProfileBaseName( repository ) )
	makeDirectory( os.path.dirname( profilesDirectoryPath ) )
	gcodec.writeFileText( profilesDirectoryPath, getArchiveText( repository ) )

def writeSettingsPrintMessage( repository ):
	"Set the settings to the dialog then write them."
	writeSettings( repository )
	print( repository.title.lower().capitalize() + ' have been saved.' )


class StringSetting:
	"A class to display, read & write a string."
	def __init__( self ):
		"Set the update function to none."
		self.entry = None
		self.updateFunction = None

	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.label = Tkinter.Label( gridPosition.master, text = self.name )
		self.label.grid( row = gridPosition.row, column = 0, columnspan = 3, sticky = Tkinter.W )
		self.createEntry( gridPosition.master )
		self.setStateToValue()
		self.entry.grid( row = gridPosition.row, column = 3, columnspan = 2, sticky = Tkinter.W )
		self.bindEntry()
		LabelHelp( self.repository.fileNameHelp, gridPosition.master, self.name, self.label )

	def addToMenu( self, repositoryMenu ):
		"Do nothing because this should only be added to a frameable repository menu."
		pass

	def addToMenuFrameable( self, repositoryMenu ):
		"Add this to the frameable repository menu."
		titleFromName = getTitleFromName( self.name )
		helpWindowMenu = Tkinter.Menu( repositoryMenu, tearoff = 0 )
		repositoryMenu.add_cascade( label = titleFromName, menu = helpWindowMenu, underline = 0 )
		if self.name in self.repository.frameList.value:
			helpWindowMenu.add_command( label = 'Remove from Window', command = self.removeFromWindow )
		else:
			helpWindowMenu.add_command( label = 'Add to Window', command = self.addToWindow )
		helpWindowMenu.add_separator()
		helpWindowMenu.add_command( label = 'Help', command = HelpPage().getOpenFromDocumentationSubName( self.repository.fileNameHelp + '#' + titleFromName ) )

	def addToWindow( self ):
		"Add this to the repository frame list."
		self.repository.frameList.addToList( self.name )

	def bindEntry( self ):
		"Bind the entry to the update function."
		if self.updateFunction != None:
			self.entry.bind( '<Return>', self.updateFunction )

	def createEntry( self, root ):
		"Create the entry."
		self.entry = Tkinter.Entry( root )

	def getFromValue( self, name, repository, value ):
		"Initialize."
		return self.getFromValueOnlyAddToRepository( name, repository, value )

	def getFromValueOnly( self, name, repository, value ):
		"Initialize."
		self.defaultValue = value
		self.name = name
		self.repository = repository
		self.value = value
		return self

	def getFromValueOnlyAddToRepository( self, name, repository, value ):
		"Initialize."
		repository.archive.append( self )
		repository.displayEntities.append( self )
		repository.menuEntities.append( self )
		return self.getFromValueOnly( name, repository, value )

	def removeFromWindow( self ):
		"Remove this from the repository frame list."
		self.repository.frameList.removeFromList( self.name )

	def setStateToValue( self ):
		"Set the entry to the value."
		setEntryText( self.entry, self.value )

	def setToDisplay( self ):
		"Set the string to the entry field."
		try:
			valueString = self.entry.get()
			self.setValueToString( valueString )
		except:
			pass

	def setUpdateFunction( self, updateFunction ):
		"Set the update function."
		self.updateFunction = updateFunction

	def setValueToSplitLine( self, lineIndex, lines, splitLine ):
		"Set the value to the second word of a split line."
		self.setValueToString( splitLine[ 1 ] )

	def setValueToString( self, valueString ):
		"Set the value to the value string."
		self.value = valueString

	def writeToArchiveWriter( self, archiveWriter ):
		"Write tab separated name and value to the archive writer."
		archiveWriter.write( '%s%s%s\n' % ( self.name, globalSpreadsheetSeparator, self.value ) )


class BooleanSetting( StringSetting ):
	"A class to display, read & write a boolean."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.checkbutton = Tkinter.Checkbutton( gridPosition.master, command = self.toggleCheckbutton, text = self.name )
#toggleCheckbutton is being used instead of a Tkinter IntVar because there is a weird bug where it doesn't work properly if this setting is not on the first window.
		self.checkbutton.grid( row = gridPosition.row, columnspan = 5, sticky = Tkinter.W )
		self.setStateToValue()
		LabelHelp( self.repository.fileNameHelp, gridPosition.master, self.name, self.checkbutton )

	def addToMenu( self, repositoryMenu ):
		"Add this to the repository menu."
		self.activateToggleMenuCheckbutton = False
#activateToggleMenuCheckbutton is being used instead of setting command after because add_checkbutton does not return a checkbutton.
		repositoryMenu.add_checkbutton( label = getTitleFromName( self.name ), command = self.toggleMenuCheckbutton )
		if self.value:
			repositoryMenu.invoke( repositoryMenu.index( Tkinter.END ) )
		self.activateToggleMenuCheckbutton = True

	def addToMenuFrameable( self, repositoryMenu ):
		"Add this to the frameable repository menu."
		titleFromName = getTitleFromName( self.name )
		helpWindowMenu = Tkinter.Menu( repositoryMenu, tearoff = 0 )
		repositoryMenu.add_cascade( label = titleFromName, menu = helpWindowMenu, underline = 0 )
		self.addToMenu( helpWindowMenu )
		helpWindowMenu.add_separator()
		helpWindowMenu.add_command( label = 'Help', command = HelpPage().getOpenFromDocumentationSubName( self.repository.fileNameHelp + '#' + titleFromName ) )

	def setStateToValue( self ):
		"Set the checkbutton to the boolean."
		try:
			if self.value:
				self.checkbutton.select()
			else:
				self.checkbutton.deselect()
		except:
			pass

	def setToDisplay( self ):
		"Do nothing because toggleCheckbutton is handling the value."
		pass

	def setValueToString( self, valueString ):
		"Set the boolean to the string."
		self.value = ( valueString.lower() == 'true' )

	def toggleCheckbutton( self ):
		"Workaround for Tkinter bug, toggle the value."
		self.value = not self.value
		self.setStateToValue()
		if self.updateFunction != None:
			self.updateFunction()

	def toggleMenuCheckbutton( self ):
		"Workaround for Tkinter bug, toggle the value."
		if self.activateToggleMenuCheckbutton:
			self.value = not self.value
			if self.updateFunction != None:
				self.updateFunction()


class CloseListener:
	"A class to listen to link a window to the global repository dialog list table."
	def __init__( self, window, closeFunction = None ):
		"Add the window to the global repository dialog list table."
		self.closeFunction = closeFunction
		self.window = window
		self.shouldWasClosedBeBound = True
		global globalRepositoryDialogListTable
		euclidean.addElementToListTableIfNotThere( window, window, globalRepositoryDialogListTable )

	def listenToWidget( self, widget ):
		"Listen to the destroy message of the widget."
		if self.shouldWasClosedBeBound:
			self.shouldWasClosedBeBound = False
			widget.bind( '<Destroy>', self.wasClosed )

	def wasClosed( self, event ):
		"The dialog was closed."
		global globalCloseListTables
		for globalCloseListTable in globalCloseListTables:
			if self.window in globalCloseListTable:
				del globalCloseListTable[ self.window ]
		if self.closeFunction != None:
			self.closeFunction()


class DisplayToolButton:
	"A class to display the tool dialog button, in a two column wide table."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		self.displayButton = Tkinter.Button( gridPosition.master, activebackground = 'black', activeforeground = 'white', text = getEachWordCapitalized( self.name ), command = self.displayDialog )
		setButtonFontWeightString( self.displayButton, self.important )
		gridPosition.incrementGivenNumberOfColumns( 2 )
		self.displayButton.grid( row = gridPosition.row, column = gridPosition.column, columnspan = 2 )

	def displayDialog( self ):
		"Display function."
		ToolDialog().getFromPath( self.path ).display()

	def getFromPath( self, important, name, path, repository ):
		"Initialize."
		self.important = important
		self.name = name
		self.path = path
		self.repository = repository
		repository.displayEntities.append( self )
		return self


class FileHelpMenuBar:
	def __init__( self, root ):
		"Create a menu bar with a file and help menu."
		self.underlineLetters = []
		self.menuBar = Tkinter.Menu( root )
		self.root = root
		root.config( menu = self.menuBar )
		self.fileMenu = Tkinter.Menu( self.menuBar, tearoff = 0 )
		self.menuBar.add_cascade( label = "File", menu = self.fileMenu, underline = 0 )
		self.underlineLetters.append( 'f' )

	def addMenuToMenuBar( self, labelText, menu ):
		"Add a menu to the menu bar."
		lowerLabelText = labelText.lower()
		for underlineLetterIndex in xrange( len( lowerLabelText ) ):
			underlineLetter = lowerLabelText[ underlineLetterIndex ]
			if underlineLetter not in self.underlineLetters:
				self.underlineLetters.append( underlineLetter )
				self.menuBar.add_cascade( label = labelText, menu = menu, underline = underlineLetterIndex )
				return
		self.menuBar.add_cascade( label = labelText, menu = menu )

	def addPluginToMenuBar( self, modulePath, repository, window ):
		"Add a menu to the menu bar from a tool."
		pluginModule = gcodec.getModuleWithPath( modulePath )
		if pluginModule == None:
			print( 'this should never happen, pluginModule in addMenuToMenuBar in settings is None.' )
			return None
		repositoryMenu = Tkinter.Menu( self.menuBar, tearoff = 0 )
		labelText = getEachWordCapitalized( os.path.basename( modulePath ) )
		self.addMenuToMenuBar( labelText, repositoryMenu )
		pluginModule.addToMenu( self.root, repositoryMenu, repository, window )

	def completeMenu( self, closeFunction, repository, saveFunction, window ):
		"Complete the menu."
		self.closeFunction = closeFunction
		self.saveFunction = saveFunction
		addAcceleratorCommand( '<Control-KeyPress-s>', saveFunction, self.root, self.fileMenu, 'Save' )
		self.fileMenu.add_command( label = "Save and Close", command = self.saveClose )
		addAcceleratorCommand( '<Control-KeyPress-w>', closeFunction, self.root, self.fileMenu, 'Close' )
		self.fileMenu.add_separator()
		addAcceleratorCommand( '<Control-KeyPress-q>', quitWindows, self.root, self.fileMenu, 'Quit' )
		skeinforgeToolsDirectoryPath = getSkeinforgeToolsDirectoryPath()
		pluginFileNames = gcodec.getPluginFileNamesFromDirectoryPath( skeinforgeToolsDirectoryPath )
		for pluginFileName in pluginFileNames:
			self.addPluginToMenuBar( os.path.join( skeinforgeToolsDirectoryPath, pluginFileName ), repository, window )

	def saveClose( self ):
		"Call the save function then the close function."
		self.saveFunction()
		self.closeFunction()


class FileNameInput( StringSetting ):
	"A class to display, read & write a fileName."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		self.gridPosition = gridPosition
		gridPosition.executables.append( self )

	def execute( self ):
		"Open the file picker."
		self.wasCancelled = False
		parent = self.gridPosition.master
		try:
			import tkFileDialog
			summarized = gcodec.getSummarizedFileName( self.value )
			initialDirectory = os.path.dirname( summarized )
			if len( initialDirectory ) > 0:
				initialDirectory += os.sep
			else:
				initialDirectory = "."
			fileName = tkFileDialog.askopenfilename( filetypes = self.getFileNameFirstTypes(), initialdir = initialDirectory, initialfile = os.path.basename( summarized ), parent = parent, title = self.name )
			self.setCancelledValue( fileName )
			return
		except:
			print( 'Could not get the old directory in settings, so the file picker will be opened in the default directory.' )
		try:
			fileName = tkFileDialog.askopenfilename( filetypes = self.getFileNameFirstTypes(), initialdir = '.', initialfile = '', parent = parent, title = self.name )
			self.setCancelledValue( fileName )
		except:
			print( 'Error in execute in FileName in settings, ' + self.name )

	def getFileNameFirstTypes( self ):
		"Get the file types with the file type of the fileName moved to the front of the list."
		try:
			basename = os.path.basename( self.value )
			splitFile = basename.split( '.' )
			allFiles = [ ( 'All', '*.*' ) ]
			allReadables = []
			if len( self.fileTypes ) > 1:
				for fileType in self.fileTypes:
					allReadable = ( ( 'All Readable', fileType[ 1 ] ) )
					allReadables.append( allReadable )
			if len( splitFile ) < 1:
				return self.fileTypes + allReadables + allFiles
			baseExtension = splitFile[ - 1 ]
			for fileType in self.fileTypes:
				fileExtension = fileType[ 1 ].split( '.' )[ - 1 ]
				if fileExtension == baseExtension:
					fileNameFirstTypes = self.fileTypes[ : ]
					fileNameFirstTypes.remove( fileType )
					return [ fileType ] + fileNameFirstTypes + allReadables + allFiles
			return self.fileTypes + allReadables + allFiles
		except:
			return allFiles

	def getFromFileName( self, fileTypes, name, repository, value ):
		"Initialize."
		self.getFromValueOnly( name, repository, value )
		self.fileTypes = fileTypes
		repository.archive.append( self )
		repository.displayEntities.append( self )
		return self

	def setCancelledValue( self, fileName ):
		"Set the value to the file name and wasCancelled true if a file was not picked."
		if ( str( fileName ) == '()' or str( fileName ) == '' ):
			self.wasCancelled = True
		else:
			self.value = fileName

	def setToDisplay( self ):
		"Do nothing because the file dialog is handling the value."
		pass


class FloatSetting( StringSetting ):
	"A class to display, read & write a float."
	def setValueToString( self, valueString ):
		"Set the float to the string."
		try:
			self.value = float( valueString )
		except:
			print( 'Oops, can not read float' + self.name + ' ' + valueString )


class FloatSpin( FloatSetting ):
	"A class to display, read & write an float in a spin box."
	def addToMenuFrameable( self, repositoryMenu ):
		"Add this to the frameable repository menu."
		titleFromName = getTitleFromName( self.name )
		helpWindowMenu = Tkinter.Menu( repositoryMenu, tearoff = 0 )
		repositoryMenu.add_cascade( label = titleFromName, menu = helpWindowMenu, underline = 0 )
		if self.name in self.repository.frameList.value:
			helpWindowMenu.add_command( label = 'Remove from Window', command = self.removeFromWindow )
		else:
			helpWindowMenu.add_command( label = 'Add to Window', command = self.addToWindow )
		helpWindowMenu.add_separator()
		changeString = ' by %s' % self.increment
		helpWindowMenu.add_command( label = 'Increase' + changeString, command = self.increase )
		helpWindowMenu.add_command( label = 'Decrease' + changeString, command = self.decrease )
		helpWindowMenu.add_separator()
		helpWindowMenu.add_command( label = 'Help', command = HelpPage().getOpenFromDocumentationSubName( self.repository.fileNameHelp + '#' + titleFromName ) )

	def bindEntry( self ):
		"Bind the entry to the update function."
		self.entry.bind( '<Return>', self.entryUpdated )
		self.setColor()

	def createEntry( self, root ):
		"Create the entry."
		self.entry = Tkinter.Spinbox( root, command = self.setColorToDisplay, from_ = self.from_, increment = self.increment, to = self.to )

	def decrease( self ):
		"Decrease the value then set the state and color to the value."
		self.value -= self.increment
		self.setStateUpdateColor()

	def entryUpdated( self, event = None ):
		"Create the entry."
		self.setColorToDisplay()
		if self.updateFunction != None:
			self.updateFunction( event )

	def getFromValue( self, from_, name, repository, to, value ):
		"Initialize."
		self.backgroundColor = None
		self.from_ = from_
		self.width = to - from_
		rank = euclidean.getRank( 0.05 * self.width )
		self.increment = euclidean.getIncrementFromRank( rank )
		self.to = to
		return self.getFromValueOnlyAddToRepository( name, repository, value )

	def increase( self ):
		"Increase the value then set the state and color to the value."
		self.value += self.increment
		self.setStateUpdateColor()

	def setColor( self, event = None ):
		"Set the color to the value, yellow if it is lower than the default and blue if it is higher."
		setSpinColor( self )

	def setColorToDisplay( self, event = None ):
		"Set the color to the value, yellow if it is lower than the default and blue if it is higher."
		self.setToDisplay()
		self.setColor()

	def setStateToValue( self ):
		"Set the entry to the value."
		setEntryText( self.entry, self.value )
		self.setColor()

	def setStateUpdateColor( self ):
		"Set the state to the value, call the update function, then set the color."
		self.setStateToValue()
		if self.updateFunction != None:
			self.updateFunction()


class FloatSpinNotOnMenu( FloatSpin ):
	"A class to display, read & write an float in a spin box, which is not to be added to a menu."
	def getFromValueOnlyAddToRepository( self, name, repository, value ):
		"Initialize."
		repository.archive.append( self )
		repository.displayEntities.append( self )
		return self.getFromValueOnly( name, repository, value )


class FloatSpinUpdate( FloatSpin ):
	"A class to display, read, update & write an float in a spin box."
	def createEntry( self, root ):
		"Create the entry."
		self.entry = Tkinter.Spinbox( root, command = self.entryUpdated, from_ = self.from_, increment = self.increment, to = self.to )


class FrameList:
	"A class to list the frames."
	def addToList( self, word ):
		"Add the word to the sorted list."
		self.value.append( word )
		self.value.sort()
		self.repository.window.redisplayWindowUpdate()

	def getFromValue( self, name, repository, value ):
		"Initialize."
		repository.archive.append( self )
		self.name = name
		self.repository = repository
		self.value = value
		return self

	def removeFromList( self, word ):
		"Remove the word from the sorted list."
		self.value.remove( word )
		self.value.sort()
		self.repository.window.redisplayWindowUpdate()

	def setToDisplay( self ):
		"Do nothing because frame list does not have a display."
		pass

	def setValueToSplitLine( self, lineIndex, lines, splitLine ):
		"Set the value to the second and later words of a split line."
		self.value = splitLine[ 1 : ]

	def writeToArchiveWriter( self, archiveWriter ):
		"Write tab separated name and list to the archive writer."
		writeValueListToArchiveWriter( archiveWriter, self )


class GridHorizontal:
	"A class to place elements horizontally on a grid."
	def __init__( self, column, row ):
		"Initialize the column and row."
		self.column = column
		self.columnStart = column
		self.row = row

	def getCopy( self ):
		"Get a copy."
		copy = GridHorizontal( self.column, self.row )
		copy.columnStart = self.columnStart
		return copy

	def increment( self ):
		"Increment the position horizontally."
		self.column += 1


class GridVertical:
	"A class to place elements vertically on a grid."
	def __init__( self, column, row ):
		"Initialize the column and row."
		self.column = column
		self.columnOffset = column
		self.columnStart = column
		self.row = row
		self.rowStart = row

	def execute( self ):
		"The execute button was clicked."
		for executable in self.executables:
			executable.execute()
		saveRepository( self.repository )
		self.repository.execute()

	def getCopy( self ):
		"Get a copy."
		copy = GridVertical( self.column, self.row )
		copy.columnOffset = self.columnOffset
		copy.columnStart = self.columnStart
		copy.rowStart = self.rowStart
		return copy

	def increment( self ):
		"Increment the position vertically."
		self.column = self.columnStart
		self.columnOffset = self.columnStart
		self.row += 1

	def incrementGivenNumberOfColumns( self, numberOfColumns ):
		"Increment the position vertically and offset it horizontally by the given number of columns."
		self.column = self.columnOffset
		if self.columnOffset == self.columnStart:
			self.columnOffset = self.columnStart + 1
			self.row += 1
			return
		if self.columnOffset < self.columnStart + numberOfColumns - 1:
			self.columnOffset += 1
			return
		self.columnOffset = self.columnStart

	def setExecutablesRepository( self, repository ):
		"Set the executables to an empty list and set the repository."
		self.executables = []
		self.repository = repository


class HelpPage:
	"A class to open a help page."
	def __init__( self ):
		"Initialize column."
		self.column = 3

	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		capitalizedName = getEachWordCapitalized( self.name )
		self.displayButton = Tkinter.Button( gridPosition.master, activebackground = 'black', activeforeground = 'white', command = self.openPage, text = capitalizedName )
		if len( capitalizedName ) < 12:
			self.displayButton[ 'width' ] = 10
		self.displayButton.grid( row = gridPosition.row, column = self.column, columnspan = 2 )

	def addToMenu( self, repositoryMenu ):
		"Add this to the repository menu."
		repositoryMenu.add_command( label = getTitleFromName( self.name ), command = self.openPage )

	def addToMenuFrameable( self, repositoryMenu ):
		"Add this to the frameable repository menu."
		self.addToMenu( repositoryMenu )

	def getFromNameAfterHTTP( self, afterHTTP, name, repository ):
		"Initialize."
		self.setToNameRepository( name, repository )
		self.hypertextAddress = 'http://' + afterHTTP
		return self

	def getFromNameAfterWWW( self, afterWWW, name, repository ):
		"Initialize."
		self.setToNameRepository( name, repository )
		self.hypertextAddress = 'http://www.' + afterWWW
		return self

	def getFromNameSubName( self, name, repository, subName = '' ):
		"Initialize."
		self.setToNameRepository( name, repository )
		self.hypertextAddress = getDocumentationPath( subName )
		return self

	def getOpenFromAbsolute( self, hypertextAddress ):
		"Get the open help page function from the hypertext address."
		self.hypertextAddress = hypertextAddress
		return self.openPage

	def getOpenFromAfterHTTP( self, afterHTTP ):
		"Get the open help page function from the part of the address after the HTTP."
		self.hypertextAddress = 'http://' + afterHTTP
		return self.openPage

	def getOpenFromAfterWWW( self, afterWWW ):
		"Get the open help page function from the afterWWW of the address after the www."
		self.hypertextAddress = 'http://www.' + afterWWW
		return self.openPage

	def getOpenFromDocumentationSubName( self, subName = '' ):
		"Get the open help page function from the afterWWW of the address after the www."
		self.hypertextAddress = getDocumentationPath( subName )
		return self.openPage

	def openPage( self, event = None ):
		"Open the browser to the hypertext address."
		openWebPage( self.hypertextAddress )

	def setToNameRepository( self, name, repository ):
		"Set to the name and repository."
		self.name = name
		self.repository = repository
		repository.displayEntities.append( self )
		repository.menuEntities.append( self )


class HelpPageRepository:
	"A class to open a repository help page."
	def __init__( self, repository ):
		"Add this to the dialog."
		self.repository = repository

	def openPage( self, event = None ):
		"Open the browser to the repository help page."
		if self.repository.openWikiManualHelpPage == None:
			self.repository.openLocalHelpPage()
			return
		from skeinforge_utilities import skeinforge_help
		helpRepository = getReadRepository( skeinforge_help.HelpRepository() )
		if helpRepository.wikiManualPrimary.value:
			self.repository.openWikiManualHelpPage()
			return
		self.repository.openLocalHelpPage()


class HiddenScrollbar( Tkinter.Scrollbar ):
	"A class to hide the scrollbar if it is not needed."
	def set( self, lo, hi ):
		"Add to grid is needed, remove if not."
		if float( lo ) <= 0.0 and float( hi ) >= 1.0:
			self.tk.call( 'grid', 'remove', self )
		else:
			self.grid()
		Tkinter.Scrollbar.set( self, lo, hi )


class IntSetting( FloatSetting ):
	"A class to display, read & write an int."
	def setValueToString( self, valueString ):
		"Set the integer to the string."
		setIntegerValueToString( self, valueString )


class IntSpin( FloatSpin ):
	"A class to display, read & write an int in a spin box."
	def getFromValue( self, from_, name, repository, to, value ):
		"Initialize."
		self.backgroundColor = None
		self.from_ = from_
		self.width = to - from_
		rank = euclidean.getRank( 0.05 * self.width )
		self.increment = max( 1, int( euclidean.getIncrementFromRank( rank ) ) )
		self.to = to
		return self.getFromValueOnlyAddToRepository( name, repository, value )

	def getSingleIncrementFromValue( self, from_, name, repository, to, value ):
		"Initialize."
		self.backgroundColor = None
		self.from_ = from_
		self.width = to - from_
		self.increment = 1
		self.to = to
		return self.getFromValueOnlyAddToRepository( name, repository, value )

	def setValueToString( self, valueString ):
		"Set the integer to the string."
		setIntegerValueToString( self, valueString )



class IntSpinNotOnMenu( IntSpin ):
	"A class to display, read & write an integer in a spin box, which is not to be added to a menu."
	def getFromValueOnlyAddToRepository( self, name, repository, value ):
		"Initialize."
		repository.archive.append( self )
		repository.displayEntities.append( self )
		return self.getFromValueOnly( name, repository, value )


class IntSpinUpdate( IntSpin ):
	"A class to display, read, update & write an int in a spin box."
	def createEntry( self, root ):
		"Create the entry."
		self.entry = Tkinter.Spinbox( root, command = self.entryUpdated, from_ = self.from_, increment = self.increment, to = self.to )


class LabelDisplay:
	"A class to add a label."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.label = Tkinter.Label( gridPosition.master, text = self.name )
		self.label.grid( row = gridPosition.row, column = 0, columnspan = 3, sticky = Tkinter.W )
		LabelHelp( self.repository.fileNameHelp, gridPosition.master, self.name, self.label )

	def getFromName( self, name, repository ):
		"Initialize."
		self.name = name
		self.repository = repository
		repository.displayEntities.append( self )
		return self


class LabelHelp:
	"A class to add help to a widget."
	def __init__( self, fileNameHelp, master, name, widget ):
		"Add menu to the widget."
		if len( name ) < 1:
			return
		self.popupMenu = Tkinter.Menu( master, tearoff = 0 )
		titleFromName = getTitleFromName( name.replace( '- ', '' ).replace( ' -', '' ) )
		self.popupMenu.add_command( label = 'Help', command = HelpPage().getOpenFromDocumentationSubName( fileNameHelp + '#' + titleFromName ) )
		widget.bind( '<Button-1>', self.unpostPopupMenu )
		widget.bind( '<Button-2>', self.unpostPopupMenu )
		widget.bind( '<Button-3>', self.displayPopupMenu )

	def unpostPopupMenu( self, event = None ):
		'Unpost the popup menu.'
		self.popupMenu.unpost()

	def displayPopupMenu( self, event = None ):
		'Display the popup menu when the button is right clicked.'
		try:
			self.popupMenu.tk_popup( event.x_root + 30, event.y_root, 0 )
		finally:
			self.popupMenu.grab_release()


class LabelSeparator:
	"A class to add a label and menu separator."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.label = Tkinter.Label( gridPosition.master, text = '' )
		self.label.grid( row = gridPosition.row, column = 0, columnspan = 3, sticky = Tkinter.W )

	def addToMenu( self, repositoryMenu ):
		"Add this to the repository menu."
		repositoryMenu.add_separator()

	def addToMenuFrameable( self, repositoryMenu ):
		"Add this to the frameable repository menu."
		self.addToMenu( repositoryMenu )

	def getFromRepository( self, repository ):
		"Initialize."
		self.name = ''
		self.repository = repository
		repository.displayEntities.append( self )
		repository.menuEntities.append( self )
		return self


class LatentStringVar:
	"A class to provide a StringVar when needed."
	def __init__( self ):
		"Set the string var."
		self.stringVar = None

	def getVar( self ):
		"Get the string var."
		if self.stringVar == None:
			self.stringVar = Tkinter.StringVar()
		return self.stringVar

	def getString( self ):
		"Get the string."
		return self.getVar().get()

	def setString( self, word ):
		"Set the string."
		self.getVar().set( word )


class MenuButtonDisplay:
	"A class to add a menu button."
	def addRadiosToDialog( self, gridPosition ):
		"Add the menu radios to the dialog."
		for menuRadio in self.menuRadios:
			menuRadio.addToDialog( gridPosition )

	def addToMenu( self, repositoryMenu ):
		"Add this to the repository menu."
		if len( self.menuRadios ) < 1:
			print( 'The MenuButtonDisplay in settings should have menu items.' )
			print( self.name )
			return
		self.menu = Tkinter.Menu( repositoryMenu, tearoff = 0 )
		repositoryMenu.add_cascade( label = getTitleFromName( self.name ), menu = self.menu )
		self.setRadioVarToName( self.menuRadios[ 0 ].name )

	def addToMenuFrameable( self, repositoryMenu ):
		"Add this to the frameable repository menu."
		titleFromName = getTitleFromName( self.name )
		self.addToMenu( repositoryMenu )
		self.menu.add_command( label = 'Help', command = HelpPage().getOpenFromDocumentationSubName( self.repository.fileNameHelp + '#' + titleFromName ) )
		self.menu.add_separator()

	def getFromName( self, name, repository ):
		"Initialize."
		self.menuRadios = []
		self.name = name
		self.radioVar = None
		self.repository = repository
		repository.menuEntities.append( self )
		return self

	def removeMenus( self ):
		"Remove all menus."
		deleteMenuItems( self.menu )
		self.menuRadios = []

	def setRadioVarToName( self, name ):
		"Get the menu button."
		self.optionList = [ name ]
		self.radioVar = Tkinter.StringVar()
		self.radioVar.set( self.optionList[ 0 ] )

	def setToNameAddToDialog( self, name, gridPosition ):
		"Get the menu button."
		if self.radioVar != None:
			return
		gridPosition.increment()
		self.setRadioVarToName( name )
		self.label = Tkinter.Label( gridPosition.master, text = self.name )
		self.label.grid( row = gridPosition.row, column = 0, columnspan = 3, sticky = Tkinter.W )
		self.menuButton = Tkinter.OptionMenu( gridPosition.master, self.radioVar, self.optionList )
		self.menuButton.grid( row = gridPosition.row, column = 3, columnspan = 2, sticky = Tkinter.W )
		self.menuButton.menu = Tkinter.Menu( self.menuButton, tearoff = 0 )
		self.menu = self.menuButton.menu
		self.menuButton[ 'menu' ]  =  self.menu
		LabelHelp( self.repository.fileNameHelp, gridPosition.master, self.name, self.label )


class MenuRadio( BooleanSetting ):
	"A class to display, read & write a boolean with associated menu radio button."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		self.menuButtonDisplay.setToNameAddToDialog( self.name, gridPosition )
		self.addToSubmenu()

	def addToMenu( self, repositoryMenu ):
		"Add this to the submenu set by MenuButtonDisplay, the repository menu is ignored"
		self.addToSubmenu()

	def addToMenuFrameable( self, repositoryMenu ):
		"Add this to the frameable repository menu."
		self.addToMenu( repositoryMenu )

	def addToSubmenu( self ):
		"Add this to the submenu."
		self.activate = False
		menu = self.menuButtonDisplay.menu
		menu.add_radiobutton( label = self.name, command = self.clickRadio, value = self.name, variable = self.menuButtonDisplay.radioVar )
		self.menuLength = menu.index( Tkinter.END )
		if self.value:
			self.menuButtonDisplay.radioVar.set( self.name )
			self.invoke()
		self.activate = True

	def clickRadio( self ):
		"Workaround for Tkinter bug, invoke and set the value when clicked."
		if not self.activate:
			return
		self.menuButtonDisplay.radioVar.set( self.name )
		if self.updateFunction != None:
			self.updateFunction()

	def getFromMenuButtonDisplay( self, menuButtonDisplay, name, repository, value ):
		"Initialize."
		self.getFromValueOnlyAddToRepository( name, repository, value )
		self.menuButtonDisplay = menuButtonDisplay
		self.menuButtonDisplay.menuRadios.append( self )
		return self

	def invoke( self ):
		"Workaround for Tkinter bug, invoke to set the value when changed."
		self.menuButtonDisplay.menu.invoke( self.menuLength )

	def setStateToValue( self ):
		"Set the checkbutton to the boolean."
		try:
			if self.value:
				self.invoke()
		except:
			pass

	def setToDisplay( self ):
		"Set the boolean to the checkbutton."
		if self.menuButtonDisplay.radioVar != None:
			self.value = ( self.menuButtonDisplay.radioVar.get() == self.name )


class PluginFrame:
	"A class to display the plugins in a frame."
	def __init__( self ):
		"Initialize."
		self.gridTable = {}
		self.latentStringVar = LatentStringVar()
		self.oldLatentString = ''

	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.gridPosition = gridPosition.getCopy()
		self.gridPosition.master = gridPosition.master
		self.createFrame( gridPosition )

	def createFrame( self, gridPosition ):
		"Create the frame."
		gridVertical = GridVertical( 0, 0 )
		gridVertical.master = Tkinter.LabelFrame( gridPosition.master, borderwidth = 3, relief = 'raised' )
		gridVertical.master.grid( row = gridPosition.row, column = gridPosition.column, columnspan = 12, sticky = Tkinter.E + Tkinter.W + Tkinter.N + Tkinter.S )
		gridPosition.master.grid_rowconfigure( gridPosition.row, weight = 1 )
		gridPosition.master.grid_columnconfigure( gridPosition.column + 11, weight = 1 )
		if self.latentStringVar.getString() == '':
			self.defaultRadioButton.setSelect()
		self.gridTable[ self.latentStringVar.getString() ] = gridVertical
		path = os.path.join( self.directoryPath, self.latentStringVar.getString() )
		pluginModule = gcodec.getModuleWithPath( path )
		if pluginModule == None:
			print( 'this should never happen, pluginModule in addToDialog in PluginFrame in settings is None' )
			print( path )
			return
		gridVertical.repository = getReadRepository( pluginModule.getNewRepository() )
		gridVertical.frameGridVertical = GridVertical( 0, 0 )
		gridVertical.frameGridVertical.setExecutablesRepository( gridVertical.repository )
		executeTitle = gridVertical.repository.executeTitle
		if executeTitle != None:
			executeButton = Tkinter.Button( gridVertical.master, activebackground = 'black', activeforeground = 'blue', text = executeTitle, command = gridVertical.frameGridVertical.execute )
			executeButton.grid( row = gridVertical.row, column = gridVertical.column )
			gridVertical.column += 1
		self.helpButton = Tkinter.Button( gridVertical.master, activebackground = 'black', activeforeground = 'white', text = "?", command = HelpPageRepository( gridVertical.repository ).openPage )
		self.helpButton.grid( row = gridVertical.row, column = gridVertical.column )
		addEmptyRow( gridVertical )
		gridVertical.increment()
		gridVertical.xScrollbar = HiddenScrollbar( gridVertical.master, orient = Tkinter.HORIZONTAL )
		gridVertical.xScrollbar.grid( row = gridVertical.row + 1, column = gridVertical.column, columnspan = 11, sticky = Tkinter.E + Tkinter.W )
		gridVertical.yScrollbar = HiddenScrollbar( gridVertical.master )
		gridVertical.yScrollbar.grid( row = gridVertical.row, column = gridVertical.column + 12, sticky = Tkinter.N + Tkinter.S )
		canvasHeight = min( 1000, gridPosition.master.winfo_screenheight() - 500 ) - 6 - int( gridVertical.xScrollbar[ 'width' ] )
		canvasWidth = min( 650, gridPosition.master.winfo_screenwidth() - 100 ) - 6 - int( gridVertical.yScrollbar[ 'width' ] )
		gridVertical.canvas = Tkinter.Canvas( gridVertical.master, height = canvasHeight, highlightthickness = 0, width = canvasWidth )
		gridVertical.frameGridVertical.master = Tkinter.Frame( gridVertical.canvas )
		for setting in gridVertical.repository.displayEntities:
			setting.addToDialog( gridVertical.frameGridVertical )
		addEmptyRow( gridVertical.frameGridVertical )
		gridVertical.frameGridVertical.master.update_idletasks()
		gridVertical.xScrollbar.config( command = gridVertical.canvas.xview )
		gridVertical.canvas[ 'xscrollcommand' ] = gridVertical.xScrollbar.set
		gridVertical.yScrollbar.config( command = gridVertical.canvas.yview )
		gridVertical.canvas[ 'yscrollcommand' ] = gridVertical.yScrollbar.set
		gridVertical.canvas.create_window( 0, 0, anchor = Tkinter.NW, window = gridVertical.frameGridVertical.master )
		gridVertical.canvas[ 'scrollregion' ] = gridVertical.frameGridVertical.master.grid_bbox()
		gridVertical.canvas.grid( row = gridVertical.row, column = gridVertical.column, columnspan = 11, sticky = Tkinter.E + Tkinter.W + Tkinter.N + Tkinter.S )
		gridVertical.master.grid_rowconfigure( gridVertical.row, weight = 1 )
		gridVertical.master.grid_columnconfigure( gridVertical.column + 11, weight = 1 )
		gridVertical.frameGridVertical.master.lift()
		self.oldLatentString = self.latentStringVar.getString()

	def focusSetMaster( self, gridPosition ):
		"Set the focus to the plugin master."
		gridPosition.frameGridVertical.master.focus_set()

	def getFromPath( self, defaultRadioButton, directoryPath, repository ):
		"Initialize."
		self.defaultRadioButton = defaultRadioButton
		self.directoryPath = directoryPath
		self.name = 'PluginFrame'
		self.repository = repository
		repository.archive.append( self )
		repository.displayEntities.append( self )
		return self

	def setStateToValue( self ):
		"Set the state of all the plugins to the value."
		for gridTableValue in self.gridTable.values():
			cancelRepository( gridTableValue.repository )

	def setToDisplay( self ):
		"Set the plugins to the display."
		pass

	def update( self ):
		"Update the frame."
		if self.oldLatentString == self.latentStringVar.getString():
			return
		self.oldLatentString = self.latentStringVar.getString()
		self.repository.archive.remove( self )
		for setting in self.repository.archive:
			setting.setToDisplay()
		writeSettingsPrintMessage( self.repository )
		self.repository.archive.append( self )
		if self.latentStringVar.getString() in self.gridTable:
			gridPosition = self.gridTable[ self.latentStringVar.getString() ]
			gridPosition.master.lift()
			self.focusSetMaster( gridPosition )
			return
		self.createFrame( self.gridPosition )

	def writeToArchiveWriter( self, archiveWriter ):
		"Write tab separated name and value to the archive writer."
		gridTableKeys = self.gridTable.keys()
		gridTableKeys.sort()
		for gridTableKey in gridTableKeys:
			saveRepository( self.gridTable[ gridTableKey ].repository )


class PluginGroupFrame( PluginFrame ):
	"A class to display the plugin groups in a frame."
	def createFrame( self, gridPosition ):
		"Create the frame."
		gridVertical = GridVertical( 0, 0 )
		gridVertical.master = Tkinter.LabelFrame( gridPosition.master, borderwidth = 3, relief = 'raised' )
		gridVertical.master.grid( row = gridPosition.row, column = gridPosition.column, columnspan = 11, sticky = Tkinter.E + Tkinter.W + Tkinter.N + Tkinter.S )
		gridPosition.master.grid_rowconfigure( gridPosition.row, weight = 1 )
		gridPosition.master.grid_columnconfigure( gridPosition.column + 10, weight = 1 )
		if self.latentStringVar.getString() == '':
			self.defaultRadioButton.setSelect()
		self.gridTable[ self.latentStringVar.getString() ] = gridVertical
		path = os.path.join( self.directoryPath, self.latentStringVar.getString() )
		pluginModule = gcodec.getModuleWithPath( path )
		if pluginModule == None:
			print( 'this should never happen, pluginModule in addToDialog in PluginFrame in settings is None' )
			print( path )
			return
		gridVertical.repository = getReadRepository( pluginModule.getNewRepository() )
		gridVertical.setExecutablesRepository( gridVertical.repository )
		executeTitle = gridVertical.repository.executeTitle
		if executeTitle != None:
			executeButton = Tkinter.Button( gridVertical.master, activebackground = 'black', activeforeground = 'blue', text = executeTitle, command = gridVertical.execute )
			executeButton.grid( row = gridVertical.row, column = gridVertical.column )
			gridVertical.column += 1
		self.helpButton = Tkinter.Button( gridVertical.master, activebackground = 'black', activeforeground = 'white', text = "?", command = HelpPageRepository( gridVertical.repository ).openPage )
		self.helpButton.grid( row = gridVertical.row, column = gridVertical.column )
		addEmptyRow( gridVertical )
		gridVertical.increment()
		for setting in gridVertical.repository.displayEntities:
			setting.addToDialog( gridVertical )
		gridVertical.master.update_idletasks()
		gridVertical.master.lift()
		self.oldLatentString = self.latentStringVar.getString()

	def focusSetMaster( self, gridPosition ):
		"Set the focus to the plugin master."
		gridPosition.master.focus_set()


class Radio( BooleanSetting ):
	"A class to display, read & write a boolean with associated radio button."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.createRadioButton( gridPosition )
		self.radiobutton.grid( row = gridPosition.row, column = 0, columnspan = 3, sticky = Tkinter.W )
		self.setStateToValue()

	def clickRadio( self ):
		"Workaround for Tkinter bug, set the value."
		self.latentStringVar.setString( self.radiobutton[ 'value' ] )
		if self.updateFunction != None:
			self.updateFunction()

	def createRadioButton( self, gridPosition ):
		"Create the radio button."
		self.radiobutton = Tkinter.Radiobutton( gridPosition.master, command = self.clickRadio, text = self.name, value = self.name, variable = self.latentStringVar.getVar() )
		LabelHelp( self.repository.fileNameHelp, gridPosition.master, self.name, self.radiobutton )

	def getFromRadio( self, latentStringVar, name, repository, value ):
		"Initialize."
		self.getFromValueOnly( name, repository, value )
		self.latentStringVar = latentStringVar
		repository.archive.append( self )
		repository.displayEntities.append( self )
#when addToMenu is added to this entity, the line below should be uncommented
#		repository.menuEntities.append( self )
		return self

	def setToDisplay( self ):
		"Set the boolean to the checkbutton."
		self.value = ( self.latentStringVar.getString() == self.radiobutton[ 'value' ] )

	def setSelect( self ):
		"Set the int var and select the radio button."
		self.latentStringVar.setString( self.radiobutton[ 'value' ] )
		self.radiobutton.select()

	def setStateToValue( self ):
		"Set the checkbutton to the boolean."
		if self.value:
			self.setSelect()


class RadioCapitalized( Radio ):
	"A class to display, read & write a boolean with associated radio button."
	def createRadioButton( self, gridPosition ):
		"Create the radio button."
		capitalizedName = getEachWordCapitalized( self.name )
		self.radiobutton = Tkinter.Radiobutton( gridPosition.master, command = self.clickRadio, text = capitalizedName, value = self.name, variable = self.latentStringVar.getVar() )


class RadioCapitalizedButton( Radio ):
	"A class to display, read & write a boolean with associated radio button."
	def createRadioButton( self, gridPosition ):
		"Create the radio button."
		capitalizedName = getEachWordCapitalized( self.name )
		self.radiobutton = Tkinter.Radiobutton( gridPosition.master, command = self.clickRadio, text = capitalizedName, value = self.name, variable = self.latentStringVar.getVar() )
		self.displayButton = Tkinter.Button( gridPosition.master, activebackground = 'black', activeforeground = 'white', text = capitalizedName, command = self.displayDialog )
		self.displayButton.grid( row = gridPosition.row, column = 3, columnspan = 2 )

	def displayDialog( self ):
		"Display function."
		ToolDialog().getFromPath( self.path ).display()
		self.setSelect()

	def getFromPath( self, latentStringVar, name, path, repository, value ):
		"Initialize."
		self.getFromRadio( latentStringVar, name, repository, value )
		self.path = path
		return self


class RadioPlugin( RadioCapitalized ):
	"A class to display, read & write a boolean with associated radio button."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		self.createRadioButton( gridPosition )
		self.radiobutton[ 'activebackground' ] = 'black'
		self.radiobutton[ 'activeforeground' ] = 'white'
		self.radiobutton[ 'selectcolor' ] = 'white'
		self.radiobutton[ 'borderwidth' ] = 3
		self.radiobutton[ 'indicatoron' ] = 0
		setButtonFontWeightString( self.radiobutton, self.important )
		self.incrementGridPosition( gridPosition )
		self.setStateToValue()

	def getFromRadio( self, important, latentStringVar, name, repository, value ):
		"Initialize."
		self.important = important
		return RadioCapitalized.getFromRadio( self, latentStringVar, name, repository, value )

	def incrementGridPosition( self, gridPosition ):
		"Increment the grid position."
		gridPosition.incrementGivenNumberOfColumns( 10 )
		self.radiobutton.grid( row = gridPosition.row, column = gridPosition.column, sticky = Tkinter.W )


class TextSetting( StringSetting ):
	"A class to display, read & write a text."
	def __init__( self ):
		"Set the update function to none."
		self.tokenConversions = [
			TokenConversion(),
			TokenConversion( 'carriageReturn', '\r' ),
			TokenConversion( 'doubleQuote', '"' ),
			TokenConversion( 'newline', '\n' ),
			TokenConversion( 'semicolon', ';' ),
			TokenConversion( 'singleQuote', "'" ),
			TokenConversion( 'tab', '\t' ) ]
		self.updateFunction = None

	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.label = Tkinter.Label( gridPosition.master, text = self.name )
		self.label.grid( row = gridPosition.row, column = 0, columnspan = 3, sticky = Tkinter.W )
		gridPosition.increment()
		self.entry = Tkinter.Text( gridPosition.master )
		self.setStateToValue()
		self.entry.grid( row = gridPosition.row, column = 0, columnspan = 5, sticky = Tkinter.W )
		LabelHelp( self.repository.fileNameHelp, gridPosition.master, self.name, self.label )

	def getFromValue( self, name, repository, value ):
		"Initialize."
		self.getFromValueOnly( name, repository, value )
		repository.archive.append( self )
		repository.displayEntities.append( self )
		return self

	def setToDisplay( self ):
		"Set the string to the entry field."
		valueString = self.entry.get( 1.0, Tkinter.END )
		self.setValueToString( valueString )

	def setStateToValue( self ):
		"Set the entry to the value."
		try:
			self.entry.delete( 1.0, Tkinter.END )
			self.entry.insert( Tkinter.INSERT, self.value )
		except:
			pass

	def setValueToSplitLine( self, lineIndex, lines, splitLine ):
		"Set the value to the second word of a split line."
		replacedValue = splitLine[ 1 ]
		for tokenConversion in reversed( self.tokenConversions ):
			replacedValue = tokenConversion.getTokenizedString( replacedValue )
		self.setValueToString( replacedValue )

	def writeToArchiveWriter( self, archiveWriter ):
		"Write tab separated name and value to the archive writer."
		replacedValue = self.value
		for tokenConversion in self.tokenConversions:
			replacedValue = tokenConversion.getNamedString( replacedValue )
		archiveWriter.write( '%s%s%s\n' % ( self.name, globalSpreadsheetSeparator, replacedValue ) )


class TokenConversion:
	"A class to convert tokens in a string."
	def __init__( self, name = 'replaceToken', token = '___replaced___' ):
		"Set the name and token."
		self.replacedName = '___replaced___' + name
		self.token = token

	def getNamedString( self, text ):
		"Get a string with the tokens changed to names."
		return text.replace( self.token, self.replacedName )

	def getTokenizedString( self, text ):
		"Get a string with the names changed to tokens."
		return text.replace( self.replacedName, self.token )


class ToolDialog:
	"A class to display the tool repository dialog."
	def addPluginToMenu( self, menu, path ):
		"Add the display command to the menu."
		name = os.path.basename( path )
		self.path = path
		menu.add_command( label = getEachWordCapitalized( name ) + '...', command = self.display )

	def display( self ):
		"Display the tool repository dialog."
		global globalRepositoryDialogListTable
		for repositoryDialog in globalRepositoryDialogListTable:
			if getPathFromFileNameHelp( repositoryDialog.repository.fileNameHelp ) == self.path:
				liftRepositoryDialogs( globalRepositoryDialogListTable[ repositoryDialog ] )
				return
		self.repositoryDialog = getDisplayedDialogFromPath( self.path )

	def getFromPath( self, path ):
		"Initialize and return display function."
		self.path = path
		return self


class WindowPosition( StringSetting ):
	"A class to display, read & write a window position."
	def addToDialog( self, gridPosition ):
		"Set the root to later get the geometry."
		self.root = gridPosition.master
		self.setToDisplay()

	def getFromValue( self, repository, value ):
		"Initialize."
		self.getFromValueOnly( 'WindowPosition', repository, value )
		repository.archive.append( self )
		repository.displayEntities.append( self )
		return self

	def setToDisplay( self ):
		"Set the string to the window position."
		try:
			geometryString = self.root.geometry()
		except:
			return
		if geometryString == '1x1+0+0':
			return
		firstPlusIndexPlusOne = geometryString.find( '+' ) + 1
		self.value = geometryString[ firstPlusIndexPlusOne : ]

	def setWindowPosition( self ):
		"Set the window position."
		movedGeometryString = '%sx%s+%s' % ( self.root.winfo_reqwidth(), self.root.winfo_reqheight(), self.value )
		self.root.geometry( movedGeometryString )


class WindowVisibilities:
	"A class to read & write window visibilities and display them."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		if self.repository.repositoryDialog == None:
			self.isActive = False
			return
		self.isActive = self.repository.repositoryDialog.isFirst
		if self.isActive:
			self.repository.repositoryDialog.openDialogListeners.append( self )

	def getFromRepository( self, repository ):
		"Initialize."
		self.isActive = False
		self.name = 'WindowVisibilities'
		self.repository = repository
		repository.archive.append( self )
		repository.displayEntities.append( self )
		self.value = []
		return self

	def openDialog( self ):
		"Create the display button."
		for item in self.value:
			getDisplayedDialogFromPath( item )

	def setToDisplay( self ):
		"Set the string to the window position."
		if not self.isActive:
			return
		self.value = []
		ownPath = getPathFromFileNameHelp( self.repository.fileNameHelp )
		for repositoryDialog in globalRepositoryDialogListTable.keys():
			keyPath = getPathFromFileNameHelp( repositoryDialog.repository.fileNameHelp )
			if keyPath != ownPath:
				if keyPath not in self.value:
					self.value.append( keyPath )

	def setStateToValue( self ):
		"Do nothing because the window visibility is not to be cancelled."
		pass

	def setValueToSplitLine( self, lineIndex, lines, splitLine ):
		"Set the value to the second and later words of a split line."
		self.value = splitLine[ 1 : ]

	def writeToArchiveWriter( self, archiveWriter ):
		"Write tab separated name and list to the archive writer."
		writeValueListToArchiveWriter( archiveWriter, self )


class RepositoryDialog:
	def __init__( self, repository, root ):
		"Add entities to the dialog."
		self.isFirst = ( len( globalRepositoryDialogListTable.keys() ) == 0 )
		self.closeListener = CloseListener( self )
		self.repository = repository
		self.gridPosition = GridVertical( 0, - 1 )
		self.gridPosition.setExecutablesRepository( repository )
		self.gridPosition.master = root
		self.root = root
		self.openDialogListeners = []
		repository.repositoryDialog = self
		root.withdraw()
		title = repository.title
		if repository.fileNameInput != None:
			title = os.path.basename( repository.fileNameInput.value ) + ' - ' + title
		root.title( title )
		fileHelpMenuBar = FileHelpMenuBar( root )
		fileHelpMenuBar.completeMenu( self.close, repository, self.save, self )
		for setting in repository.displayEntities:
			setting.addToDialog( self.gridPosition )
		if self.gridPosition.row < 20:
			addEmptyRow( self.gridPosition )
		self.addButtons( repository, root )
		root.update_idletasks()
		self.setWindowPositionDeiconify()
		root.deiconify()
		for openDialogListener in self.openDialogListeners:
			openDialogListener.openDialog()

	def __repr__( self ):
		"Get the string representation of this RepositoryDialog."
		return self.repository.title

	def addButtons( self, repository, root ):
		"Add buttons to the dialog."
		columnIndex = 0
		self.gridPosition.increment()
		saveCommand = self.save
		saveText = 'Save'
		if self.isFirst:
			saveCommand = saveAll
			saveText = 'Save All'
		if repository.executeTitle != None:
			executeButton = Tkinter.Button( root, activebackground = 'black', activeforeground = 'blue', text = repository.executeTitle, command = self.gridPosition.execute )
			executeButton.grid( row = self.gridPosition.row, column = columnIndex, columnspan = 2, sticky = Tkinter.W )
			columnIndex += 2
		self.helpButton = Tkinter.Button( root, activebackground = 'black', activeforeground = 'white', text = "?", command = HelpPageRepository( self.repository ).openPage )
		self.helpButton.grid( row = self.gridPosition.row, column = columnIndex )
		self.closeListener.listenToWidget( self.helpButton )
		columnIndex += 6
		cancelButton = Tkinter.Button( root, activebackground = 'black', activeforeground = 'orange', command = self.cancel, fg = 'orange', text = 'Cancel' )
		cancelButton.grid( row = self.gridPosition.row, column = columnIndex )
		columnIndex += 1
		self.saveButton = Tkinter.Button( root, activebackground = 'black', activeforeground = 'darkgreen', command = saveCommand, fg = 'darkgreen', text = saveText )
		self.saveButton.grid( row = self.gridPosition.row, column = columnIndex )

	def cancel( self, event = None ):
		"Set all entities to their saved state."
		cancelRepository( self.repository )

	def close( self, event = None ):
		"The dialog was closed."
		try:
			self.root.destroy()
		except:
			pass

	def save( self, event = None ):
		"Set the entities to the dialog then write them."
		saveRepository( self.repository )

	def setWindowPositionDeiconify( self ):
		"Set the window position if that setting exists."
		for setting in self.repository.archive:
			if setting.name == 'WindowPosition':
				setting.setWindowPosition()
				return
