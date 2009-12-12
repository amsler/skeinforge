"""
This page is in the table of contents.
Help has buttons and menu items to open help, blog and forum pages in your primary browser.

The Fabmetheus Blog is the skeinforge announcements blog and the place to post questions, bugs and skeinforge requests.

The 'Index of Local Documentation' is a list of the pages in the documentation folder.  The Wiki Manual is the skeinforge wiki with pictures and charts.  It is the best and most readable source of skeinforge information and you are welcome to contribute.  The 'Overview of Skeinforge' is also the help page of the skeinforge tool.  It is a general description of skeinforge, has answers to frequently asked questions and has many links to skeinforge, fabrication and python pages.

In the forum section, the 'Bits from Bytes Printing Board' is about printing questions, problems and solutions.  Most of the people on that forum use the rapman, but many of the solutions apply to any reprap.  The 'Bits from Bytes Software Board' is about software, and has some skeinforge threads.  The 'Skeinforge Contributions Thread' is a thread about how to contribute to skeinforge development.  The 'Skeinforge Settings Thread' is a thread for people to post, download and discuss skeinforge settings.

The help menu has an item for each button on the help page.  Also, at the very top, it has a link to the local documentation and if there is a separate page for that tool in the wiki manual, a link to that page on the manual.  If the 'Wiki Manual Primary' checkbutton is selected and there is a separate wiki manual page, the wiki page will be the primary document page, otherwise the local page will be primary.  The help button (? symbol button) on the tool page will open the primary page, as will pressing <F1>.  For example, if you click the the help button from the chamber tool, which has a separate page in the wiki, and 'Wiki Manual Primary' is selected, the wiki manual chamber page will be opened.  Clicking F1 will also open the wiki manual chamber page.

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
	capitalizedBasename = os.path.basename( path ).capitalize()
	helpRepository = preferences.getReadRepository( HelpRepository() )
	if repository.openWikiManualHelpPage != None and helpRepository.wikiManualPrimary.value:
		menu.add_command( label = 'Local ' + capitalizedBasename, command = repository.openLocalHelpPage )
	else:
		preferences.addAcceleratorCommand( '<F1>', repository.openLocalHelpPage, master, menu, 'Local ' + capitalizedBasename )
		repository.openQuestionMarkHelpPage = repository.openLocalHelpPage
	if repository.openWikiManualHelpPage != None:
		if helpRepository.wikiManualPrimary.value:
			preferences.addAcceleratorCommand( '<F1>', repository.openWikiManualHelpPage, master, menu, 'Wiki Manual ' + capitalizedBasename )
			repository.openQuestionMarkHelpPage = repository.openWikiManualHelpPage
		else:
			menu.add_command( label = 'Local ' + capitalizedBasename, command = repository.openLocalHelpPage )
	menu.add_separator()
	helpRepository = HelpRepository()
	preferences.addMenuEntitiesToMenu( menu, helpRepository.menuEntities )

def getNewRepository():
	"Get the repository constructor."
	return HelpRepository()


class HelpRepository:
	"A class to handle the help preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		preferences.addListsToRepository( 'skeinforge_tools.help.html', '', self )
		preferences.LabelDisplay().getFromName( 'Fabmetheus Blog, Announcements & Questions:', self )
		preferences.HelpPage().getFromNameAfterHTTP( 'fabmetheus.blogspot.com/', 'Fabmetheus Blog', self )
		preferences.LabelDisplay().getFromName( 'Index of Local Documentation: ', self )
		preferences.HelpPage().getFromNameSubName( 'Index', self )
		preferences.LabelDisplay().getFromName( 'Wiki Manual with Pictures & Charts: ', self )
		preferences.HelpPage().getFromNameAfterWWW( 'bitsfrombytes.com/wiki/index.php?title=Skeinforge', 'Wiki Manual', self )
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
		preferences.LabelDisplay().getFromName( 'Skeinforge Settings Thread:', self )
		preferences.HelpPage().getFromNameAfterHTTP( 'dev.forums.reprap.org/read.php?12,27434', 'Skeinforge Settings Thread', self )
		preferences.LabelSeparator().getFromRepository( self )
		self.wikiManualPrimary = preferences.BooleanPreference().getFromValue( 'Wiki Manual Primary', self, True )
		self.wikiManualPrimary.setUpdateFunction( self.save )

	def save( self ):
		"Write the entities."
		preferences.writePreferencesPrintMessage( self )

def main():
	"Display the help dialog."
	preferences.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
