"""
Help is a script to display help page links.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import preferences
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addToMenu( master, menu, repository, window ):
	"Add a tool plugin menu."
	path = preferences.getPathFromFileNameHelp( repository.fileNameHelp )
	openDocumentationCommand = preferences.HelpPage().getOpenFromDocumentationSubName( repository.fileNameHelp )
	preferences.addAcceleratorCommand( '<F1>', openDocumentationCommand, master, menu, os.path.basename( path ).capitalize() )
	menu.add_separator()
	helpRepository = HelpRepository()
	preferences.addMenuEntitiesToMenu( menu, helpRepository.menuEntities )

def getRepositoryConstructor():
	"Get the repository constructor."
	return HelpRepository()


class HelpRepository:
	"A class to handle the help preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		#Set the default preferences.
		preferences.addListsToRepository( self )
		preferences.LabelDisplay().getFromName( 'Index of Local Documentation: ', self )
		preferences.HelpPage().getFromNameSubName( 'Index', self )
		preferences.LabelDisplay().getFromName( 'Manual, Wiki with Pictures & Charts: ', self )
		preferences.HelpPage().getFromNameAfterWWW( 'bitsfrombytes.com/wiki/index.php?title=Skeinforge', 'Manual', self )
		preferences.LabelDisplay().getFromName( 'Overview of Skeinforge: ', self )
		preferences.HelpPage().getFromNameSubName( 'Overview', self, 'skeinforge.html' )
		preferences.LabelSeparator().getFromRepository( self )
		preferences.LabelDisplay().getFromName( 'Forums:', self )
		preferences.LabelDisplay().getFromName( 'Bits from Bytes Printing Board:', self )
		preferences.HelpPage().getFromNameAfterWWW( 'bitsfrombytes.com/fora/user/index.php?board=5.0', 'Bits from Bytes Printing Board', self )
		preferences.LabelDisplay().getFromName( 'Bits from Bytes Software Board:', self )
		preferences.HelpPage().getFromNameAfterWWW( 'bitsfrombytes.com/fora/user/index.php?board=4.0', 'Bits from Bytes Software Board', self )
		preferences.LabelDisplay().getFromName( 'Skeinforge Contributions Thread:', self )
		preferences.HelpPage().getFromNameAfterHTTP( 'dev.forums.reprap.org/read.php?12,27562', 'Skeinforge Contributions Thread', self )
		preferences.LabelDisplay().getFromName( 'Skeinforge Powwow Thread:', self )
		preferences.HelpPage().getFromNameAfterHTTP( 'dev.forums.reprap.org/read.php?12,20013', 'Skeinforge Powwow Thread', self )
		preferences.LabelDisplay().getFromName( 'Skeinforge Settings Thread:', self )
		preferences.HelpPage().getFromNameAfterHTTP( 'dev.forums.reprap.org/read.php?12,27434', 'Skeinforge Settings Thread', self )
		#Create the archive, title of the execute button, title of the dialog & preferences fileName.
		self.executeTitle = None
		preferences.setHelpPreferencesFileNameTitleWindowPosition( self, 'skeinforge_tools.help.html' )


def main():
	"Display the help dialog."
	preferences.startMainLoopFromConstructor( getRepositoryConstructor() )

if __name__ == "__main__":
	main()
