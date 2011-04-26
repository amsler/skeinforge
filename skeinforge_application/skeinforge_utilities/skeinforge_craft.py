"""
Craft is a script to access the plugins which craft a gcode file.

The plugin buttons which are commonly used are bolded and the ones which are rarely used have normal font weight.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_analyze
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
from skeinforge_application.skeinforge_utilities import skeinforge_profile
import os
import time


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getChainText( fileName, procedure ):
	"Get a crafted shape file."
	text = gcodec.getFileText( fileName )
	procedures = getProcedures( procedure, text )
	return getChainTextFromProcedures( fileName, procedures, text )

def getChainTextFromProcedures( fileName, procedures, text ):
	"Get a crafted shape file from a list of procedures."
	lastProcedureTime = time.time()
	for procedure in procedures:
		craftModule = getCraftModule( procedure )
		if craftModule != None:
			text = craftModule.getCraftedText( fileName, text )
			if gcodec.isProcedureDone( text, procedure ):
				print('%s procedure took %s.' % ( procedure.capitalize(), euclidean.getDurationString( time.time() - lastProcedureTime ) ) )
				lastProcedureTime = time.time()
	return text

def getCraftModule( fileName ):
	"Get craft module."
	return gcodec.getModuleWithDirectoryPath( getPluginsDirectoryPath(), fileName )

def getLastModule():
	"Get the last tool."
	craftSequence = getReadCraftSequence()
	if len( craftSequence ) < 1:
		return None
	return getCraftModule( craftSequence[ - 1 ] )

def getNewRepository():
	"Get the repository constructor."
	return CraftRepository()

def getPluginsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( os.path.dirname( __file__ ), os.path.join('skeinforge_plugins', 'craft_plugins') )

def getPluginFileNames():
	"Get craft plugin fileNames."
	craftSequence = getReadCraftSequence()
	craftSequence.sort()
	return craftSequence

def getProcedures( procedure, text ):
	"Get the procedures up to and including the given procedure."
	craftSequence = getReadCraftSequence()
	sequenceIndexPlusOneFromText = getSequenceIndexPlusOneFromText( text )
	sequenceIndexFromProcedure = getSequenceIndexFromProcedure( procedure )
	return craftSequence[ sequenceIndexPlusOneFromText : sequenceIndexFromProcedure + 1 ]

def getReadCraftSequence():
	"Get profile sequence."
	return skeinforge_profile.getCraftTypePluginModule().getCraftSequence()

def getSequenceIndexFromProcedure( procedure ):
	"Get the profile sequence index of the procedure.  Return None if the procedure is not in the sequence"
	craftSequence = getReadCraftSequence()
	if procedure not in craftSequence:
		return 0
	return craftSequence.index( procedure )

def getSequenceIndexPlusOneFromText( fileText ):
	"Get the profile sequence index of the file plus one.  Return zero if the procedure is not in the file"
	craftSequence = getReadCraftSequence()
	for craftSequenceIndex in xrange( len( craftSequence ) - 1, - 1, - 1 ):
		procedure = craftSequence[ craftSequenceIndex ]
		if gcodec.isProcedureDone( fileText, procedure ):
			return craftSequenceIndex + 1
	return 0

def writeChainTextWithNounMessage( fileName, procedure ):
	"Get and write a crafted shape file."
	print('')
	print('The %s tool is parsing the file:' % procedure )
	print( os.path.basename( fileName ) )
	print('')
	startTime = time.time()
	fileNameSuffix = fileName[ : fileName.rfind('.') ] + '_' + procedure + '.gcode'
	craftText = getChainText( fileName, procedure )
	if craftText == '':
		return
	gcodec.writeFileText( fileNameSuffix, craftText )
	print('')
	print('The %s tool has created the file:' % procedure )
	print( fileNameSuffix )
	print('')
	print('It took %s to craft the file.' % euclidean.getDurationString( time.time() - startTime ) )
	skeinforge_analyze.writeOutput( fileName, fileNameSuffix, craftText )

def writeOutput( fileName ):
	"Craft a gcode file with the last module."
	pluginModule = getLastModule()
	if pluginModule != None:
		pluginModule.writeOutput( fileName )


class CraftRadioButtonsSaveListener:
	"A class to update the craft radio buttons."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		euclidean.addElementToListTableIfNotThere( self, self.repository.repositoryDialog, settings.globalProfileSaveListenerListTable )
		self.gridPosition = gridPosition.getCopy()
		self.gridPosition.row = gridPosition.rowStart
		self.gridPosition.increment()
		self.setRadioButtons()

	def getFromRadioPlugins( self, radioPlugins, repository ):
		"Initialize."
		self.name = 'CraftRadioButtonsSaveListener'
		self.radioPlugins = radioPlugins
		self.repository = repository
		repository.displayEntities.append( self )
		return self

	def save( self ):
		"Profile has been saved and craft radio plugins should be updated."
		self.setRadioButtons()

	def setRadioButtons( self ):
		"Profile has been saved and craft radio plugins should be updated."
		craftSequence = skeinforge_profile.getCraftTypePluginModule().getCraftSequence()
		gridPosition = self.gridPosition.getCopy()
		maximumValue = False
		activeRadioPlugins = []
		for radioPlugin in self.radioPlugins:
			if radioPlugin.name in craftSequence:
				activeRadioPlugins.append( radioPlugin )
				radioPlugin.incrementGridPosition( gridPosition )
				maximumValue = max( radioPlugin.value, maximumValue )
			else:
				radioPlugin.radiobutton.grid_remove()
		if not maximumValue:
			selectedRadioPlugin = settings.getSelectedRadioPlugin( self.repository.importantFileNames + [ activeRadioPlugins[0].name ], activeRadioPlugins ).setSelect()
		self.repository.pluginFrame.update()


class CraftRepository:
	"A class to handle the craft settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository('skeinforge_application.skeinforge_utilities.skeinforge_craft.html', '', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Craft', self, '')
		self.importantFileNames = ['carve', 'chop', 'feed', 'flow', 'lift', 'raft', 'speed']
		allCraftNames = gcodec.getPluginFileNamesFromDirectoryPath( getPluginsDirectoryPath() )
		radioPlugins = settings.getRadioPluginsAddPluginFrame( getPluginsDirectoryPath(), self.importantFileNames, allCraftNames, self )
		CraftRadioButtonsSaveListener().getFromRadioPlugins( radioPlugins, self )
		self.executeTitle = 'Craft'

	def execute( self ):
		"Craft button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, [], self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )
