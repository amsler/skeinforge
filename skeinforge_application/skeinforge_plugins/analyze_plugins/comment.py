"""
This page is in the table of contents.
Comment is a script to comment a gcode file.

The comment manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Comment

==Operation==
The default 'Activate Comment' checkbox is on.  When it is on, the functions described below will work when called from the skeinforge toolchain, when it is off, the functions will not be called from the toolchain.  The functions will still be called, whether or not the 'Activate Comment' checkbox is on, when comment is run directly.

==Gcodes==

An explanation of the gcodes is at:
http://reprap.org/bin/view/Main/Arduino_GCode_Interpreter

and at:
http://reprap.org/bin/view/Main/MCodeReference

A gode example is at:
http://forums.reprap.org/file.php?12,file=565

==Examples==

Below are examples of comment being used.  These examples are run in a terminal in the folder which contains Screw_Holder_penultimate.gcode and comment.py.

> python comment.py
This brings up the comment dialog.


> python comment.py Screw Holder_penultimate.gcode
The comment file is saved as Screw_Holder_penultimate_comment.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import comment
>>> comment.main()
This brings up the comment dialog.


>>> comment.getWindowAnalyzeFile('Screw Holder_penultimate.gcode')
The commente file is saved as Screw_Holder_penultimate_comment.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
import cStringIO
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getNewRepository():
	"Get the repository constructor."
	return CommentRepository()

def getWindowAnalyzeFile( fileName ):
	"Comment a gcode file."
	gcodeText = gcodec.getFileText( fileName )
	return getWindowAnalyzeFileGivenText( fileName, gcodeText )

def getWindowAnalyzeFileGivenText( fileName, gcodeText ):
	"Write a commented gcode file for a gcode file."
	skein = CommentSkein()
	skein.parseGcode(gcodeText)
	gcodec.writeFileMessageEnd('_comment.gcode', fileName, skein.output.getvalue(), 'The commented file is saved as ')

def writeOutput( fileName, fileNameSuffix, gcodeText = ''):
	"Write a commented gcode file for a skeinforge gcode file, if 'Write Commented File for Skeinforge Chain' is selected."
	repository = settings.getReadRepository( CommentRepository() )
	if gcodeText == '':
		gcodeText = gcodec.getFileText( fileNameSuffix )
	if repository.activateComment.value:
		getWindowAnalyzeFileGivenText( fileNameSuffix, gcodeText )


class CommentRepository:
	"A class to handle the comment settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository('skeinforge_application.skeinforge_plugins.analyze_plugins.comment.html', '', self )
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute('http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Comment')
		self.activateComment = settings.BooleanSetting().getFromValue('Activate Comment', self, False )
		self.fileNameInput = settings.FileNameInput().getFromFileName( [ ('Gcode text files', '*.gcode') ], 'Open File to Write Comments for', self, '')
		#Create the archive, title of the execute button, title of the dialog & settings fileName.
		self.executeTitle = 'Write Comments'

	def execute(self):
		"Write button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrGcodeDirectory( self.fileNameInput.value, self.fileNameInput.wasCancelled, ['_comment'] )
		for fileName in fileNames:
			getWindowAnalyzeFile( fileName )


class CommentSkein:
	"A class to comment a gcode skein."
	def __init__(self):
		self.oldLocation = None
		self.output = cStringIO.StringIO()

	def addComment( self, comment ):
		"Add a gcode comment and a newline to the output."
		self.output.write( "( " + comment + " )\n" )

	def linearMove( self, splitLine ):
		"Comment a linear move."
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		self.addComment( "Linear move to " + str( location ) + "." );
		self.oldLocation = location

	def parseGcode( self, gcodeText ):
		"Parse gcode text and store the commented gcode."
		lines = gcodec.getTextLines(gcodeText)
		for line in lines:
			self.parseLine(line)

	def parseLine( self, line ):
		"Parse a gcode line and add it to the commented gcode."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[0]
		if firstWord == 'G1':
			self.linearMove( splitLine )
		elif firstWord == 'G2':
			self.setHelicalMoveEndpoint( splitLine )
			self.addComment( "Helical clockwise move to " + str( self.oldLocation ) + "." )
		elif firstWord == 'G3':
			self.setHelicalMoveEndpoint( splitLine )
			self.addComment( "Helical counterclockwise move to " + str( self.oldLocation ) + "." )
		elif firstWord == 'G21':
			self.addComment( "Set units to mm." )
		elif firstWord == 'G28':
			self.addComment( "Start at home." )
		elif firstWord == 'G90':
			self.addComment( "Set positioning to absolute." )
		elif firstWord == 'M101':
			self.addComment( "Extruder on, forward." );
		elif firstWord == 'M102':
			self.addComment( "Extruder on, reverse." );
		elif firstWord == 'M103':
			self.addComment( "Extruder off." )
		elif firstWord == 'M104':
			self.addComment( "Set temperature to " + str( gcodec.getDoubleAfterFirstLetter( splitLine[1] ) ) + " C." )
		elif firstWord == 'M105':
			self.addComment( "Custom code for temperature reading." )
		elif firstWord == 'M106':
			self.addComment( "Turn fan on." )
		elif firstWord == 'M107':
			self.addComment( "Turn fan off." )
		elif firstWord == 'M108':
			self.addComment( "Set extruder speed to " + str( gcodec.getDoubleAfterFirstLetter( splitLine[1] ) ) + "." )
		self.output.write( line + "\n" )

	def setHelicalMoveEndpoint( self, splitLine ):
		"Get the endpoint of a helical move."
		if self.oldLocation == None:
			print( "A helical move is relative and therefore must not be the first move of a gcode file." )
			return
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		location += self.oldLocation
		self.oldLocation = location


def main():
	"Display the comment dialog."
	if len( sys.argv ) > 1:
		getWindowAnalyzeFile(' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()

