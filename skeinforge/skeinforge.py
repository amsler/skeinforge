#!/usr/bin/python
"""
This page is in the table of contents.
==Overview==
===Introduction===
Skeinforge is a GPL tool chain to forge a gcode skein for a model.

The tool chain starts with carve, which carves the model into layers, then the layers are modified by other tools in turn like fill, comb, tower, raft, stretch, hop, wipe, fillet & export.  Each tool automatically gets the gcode from the previous tool.  So if you want a carved & filled gcode, call the fill tool and it will call carve, then it will fill and output the gcode.  If you want to use all the tools, call export and it will call in turn all the other tools down the chain to produce the gcode file.

If you do not want a tool after preface to modify the output, deselect the Activate checkbox for that tool.  When the Activate checkbox is off, the tool will just hand off the gcode to the next tool without modifying it.

The skeinforge module provides a single place to call up all the setting dialogs.  When the 'Skeinforge' button is clicked, skeinforge calls export, since that is the end of the chain.

The plugin buttons which are commonly used are bolded and the ones which are rarely used have normal font weight.

There are also tools which handle settings for the chain, like material & polyfile.

The analyze tool calls plugins in the analyze_plugins folder, which will analyze the gcode in some way when it is generated if their Activate checkbox is selected.

The interpret tool accesses and displays the import plugins.

The default settings are similar to those on Nophead's machine.  A setting which is often different is the 'Layer Thickness' in carve.

===Alternative===
Another way to make gcode for a model is to use the Java RepRap host program, described at:
http://dev.www.reprap.org/bin/view/Main/DriverSoftware#Creating_GCode_files_from_STL_fi

===Contribute===
You can contribute by helping develop the manual at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge

There is also a forum thread about how to contribute to skeinforge development at:
http://dev.forums.reprap.org/read.php?12,27562

===Documentation===
There is a manual at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge

There is also documentation is in the documentation folder, in the doc strings for each module and it can be called from the '?' button or the menu or by clicking F1 in each setting dialog.

A list of other tutorials is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge#Tutorials

===Fabrication===
To fabricate a model with gcode and the Arduino you can use the send.py in the fabricate folder.  The documentation for it is in the folder as send.html and at:
http://reprap.org/bin/view/Main/ArduinoSend

Another way is to use an EMC2 or similar computer controlled milling machine, as described in the "ECM2 based repstrap" forum thread at:
http://forums.reprap.org/read.php?1,12143

using the M-Apps package, which is at:
http://forums.reprap.org/file.php?1,file=772

Another way is to use Zach's ReplicatorG at:
http://replicat.org/

There is also an older Processing script at:
http://reprap.svn.sourceforge.net/viewvc/reprap/trunk/users/hoeken/arduino/GCode_Host/

Yet another way is to use the reprap host, written in Java, to load and print gcode:
http://dev.www.reprap.org/bin/view/Main/DriverSoftware#Load_GCode

For jogging, the Metalab group wrote their own exerciser, also in Processing:
http://reprap.svn.sourceforge.net/viewvc/reprap/trunk/users/metalab/processing/GCode_Exerciser/

The Metalab group has descriptions of skeinforge in action and their adventures are described at:
http://reprap.soup.io/

There is a board about printing issues at:
http://www.bitsfrombytes.com/fora/user/index.php?board=5.0

You can buy the Rapman (an improved Darwin) from Bits from Bytes at:
http://www.bitsfrombytes.com/

You can buy the Makerbot from Makerbot Industries at:
http://www.makerbot.com/

===File Formats===
An explanation of the gcodes is at:
http://reprap.org/bin/view/Main/Arduino_GCode_Interpreter

and at:
http://reprap.org/bin/view/Main/MCodeReference

A gode example is at:
http://forums.reprap.org/file.php?12,file=565

The settings are saved as tab separated .csv files in the .skeinforge folder in your home directory.  The settings can be set in the tool dialogs.  The .csv files can also be edited with a text editor or a spreadsheet program set to separate tabs.

The Scalable Vector Graphics file produced by vectorwrite can be opened by an SVG viewer or an SVG capable browser like Mozilla:
http://www.mozilla.com/firefox/

A good triangle surface format is the GNU Triangulated Surface format, which is supported by Mesh Viewer and described at:
http://gts.sourceforge.net/reference/gts-surfaces.html#GTS-SURFACE-WRITE

You can export GTS files from Art of Illusion with the Export GNU Triangulated Surface.bsh script in the Art of Illusion Scripts folder.

STL is an inferior triangle surface format, described at:
http://en.wikipedia.org/wiki/STL_(file_format)

If you're using an STL file and you can't even carve it, try converting it to a GNU Triangulated Surface file in Art of Illusion.  If it still doesn't carve, then follow the advice in the troubleshooting section.

===Getting Skeinforge===
The latest version is at:
http://members.axion.net/~enrique/reprap_python_beanshell.zip

a sometimes out of date version is in the last reprap_python_beanshell.zip attachment in the last post of the Fabmetheus blog at:
http://fabmetheus.blogspot.com/

another sometimes out of date version is at:
https://reprap.svn.sourceforge.net/svnroot/reprap/trunk/reprap/miscellaneous/python-beanshell-scripts/

===Getting Started===
For skeinforge to run, install python 2.x on your machine, which is available from:
http://www.python.org/download/

To use the settings dialog you'll also need Tkinter, which probably came with the python installation.  If it did not, look for it at:
http://www.tcl.tk/software/tcltk/

If you want python and Tkinter together on MacOS, you can try:
http://www.astro.washington.edu/owen/PythonOnMacOSX.html

If you want python and Tkinter together on all platforms and don't mind filling out forms, you can try the ActivePython package from Active State at:
http://www.activestate.com/Products/activepython/feature_list.mhtml

The computation intensive python modules will use psyco if it is available and run about twice as fast.  Psyco is described at:
http://psyco.sourceforge.net/index.html

The psyco download page is:
http://psyco.sourceforge.net/download.html

Skeinforge imports Stereolithography (.stl) files or GNU Triangulated Surface (.gts) files.  If importing an STL file directly doesn't work, an indirect way to import an STL file is by turning it into a GTS file is by using the Export GNU Triangulated Surface script at:
http://members.axion.net/~enrique/Export%20GNU%20Triangulated%20Surface.bsh

The Export GNU Triangulated Surface script is also in the Art of Illusion folder, which is in the same folder as skeinforge.py.  To bring the script into Art of Illusion, drop it into the folder ArtOfIllusion/Scripts/Tools/.  Then import the STL file using the STL import plugin in the import submenu of the Art of Illusion file menu.  Then from the Scripts submenu in the Tools menu, choose 'Export GNU Triangulated Surface' and select the imported STL shape.  Click the 'Export Selected' checkbox and click OK. Once you've created the GTS file, you can turn it into gcode by typing in a shell in the same folder as skeinforge:
> python skeinforge.py

When the skeinforge dialog pops up, click 'Skeinforge', choose the file which you exported in 'Export GNU Triangulated Surface' and the gcode file will be saved with the suffix '_export.gcode'.

Or you can turn files into gcode by adding the file name, for example:
> python skeinforge.py Screw Holder Bottom.stl

===Motto===
I may be slow, but I get there in the end.

===Troubleshooting===
If there's a bug, try downloading the very latest version because skeinforge is often updated without an announcement.

If there is still a bug, then first prepare the following files:

1. stl file
2. pictures explaining the problem
3. your settings (pack the whole .skeinforge directory with all your settings) 

Then zip all the files.

Second, write a description of the error, send the description and the archive to the developer, enrique ( perez_enrique AT yahoo.com.removethispart ). After a bug fix is released, test the new version and report the results to enrique, whether the fix was successful or not.

If the dialog window is too big for the screen, on most Linux window managers you can move a window by holding down the Alt key and then drag the window with the left mouse button to get to the off screen widgets.

If you can't use the graphical interface, you can change the settings for skeinforge by using a text editor or spreadsheet to change the settings in the profiles folder in the .skeinforge folder in your home directory.

Comments and suggestions are welcome, however, I usually won't reply because developing takes all my time and as of the time of this writing I have at least one year of features to implement.

I will only answer your questions if you contribute to skeinforge in some way.  Some ways of contributing to skeinforge are in the contributions thread at:
http://dev.forums.reprap.org/read.php?12,27562

I reserve the right to make any correspondence public.  Do not send me any correspondence marked confidential.  If you do I will delete it.


==Examples==
The following examples forge the STL file Screw Holder.stl.  The examples are run in a terminal in the folder which contains Screw Holder.gts and skeinforge.py.

> python skeinforge.py
This brings up the dialog, after clicking 'Skeinforge', the following is printed:
The exported file is saved as Screw Holder_export.gcode


> python skeinforge.py Screw Holder.stl
The exported file is saved as Screw Holder_export.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import skeinforge
>>> skeinforge.writeOutput( 'Screw Holder.stl' )
The exported file is saved as Screw Holder_export.gcode


>>> skeinforge.main()
This brings up the skeinforge dialog.


To run only fill for example, type in the skeinforge_tools folder which fill is in:
> python fill.py

"""

from __future__ import absolute_import
import __init__

from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
from skeinforge.skeinforge_utilities import skeinforge_craft
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from skeinforge.skeinforge_utilities import skeinforge_polyfile
from skeinforge.skeinforge_utilities import skeinforge_profile
import os
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = """
Adrian Bowyer <http://forums.reprap.org/profile.php?12,13>
Brendan Erwin <http://forums.reprap.org/profile.php?12,217>
Greenarrow <http://forums.reprap.org/profile.php?12,81>
Ian England <http://forums.reprap.org/profile.php?12,192>
John Gilmore <http://forums.reprap.org/profile.php?12,364>
Jonwise <http://forums.reprap.org/profile.php?12,716>
Kyle Corbitt <http://forums.reprap.org/profile.php?12,90>
Michael Duffin <http://forums.reprap.org/profile.php?12,930>
Marius Kintel <http://reprap.soup.io/>
Nophead <http://www.blogger.com/profile/12801535866788103677>
PJR <http://forums.reprap.org/profile.php?12,757>
Reece.Arnott <http://forums.reprap.org/profile.php?12,152>
Wade <http://forums.reprap.org/profile.php?12,489>
Xsainnz <http://forums.reprap.org/profile.php?12,563>
Zach Hoeken <http://blog.zachhoeken.com/>

Organizations:
Art of Illusion <http://www.artofillusion.org/>"""
__date__ = "$Date: 2008/21/11 $"
__license__ = "GPL 3.0"


def addToProfileMenu( profileSelection, profileType, repository ):
	"Add a profile menu."
	pluginFileNames = skeinforge_profile.getPluginFileNames()
	craftTypeName = skeinforge_profile.getCraftTypeName()
	pluginModule = skeinforge_profile.getCraftTypePluginModule()
	profilePluginSettings = settings.getReadRepository( pluginModule.getNewRepository() )
	for pluginFileName in pluginFileNames:
		skeinforge_profile.ProfileTypeMenuRadio().getFromMenuButtonDisplay( profileType, pluginFileName, repository, craftTypeName == pluginFileName )
	for profileName in profilePluginSettings.profileList.value:
		skeinforge_profile.ProfileSelectionMenuRadio().getFromMenuButtonDisplay( profileSelection, profileName, repository, profileName == profilePluginSettings.profileListbox.value )

def getPluginsDirectoryPath():
	"Get the plugins directory path."
	return gcodec.getAbsoluteFolderPath( __file__, 'skeinforge_tools' )

def getPluginFileNames():
	"Get analyze plugin fileNames."
	return gcodec.getPluginFileNamesFromDirectoryPath( getPluginsDirectoryPath() )

def getNewRepository():
	"Get the repository constructor."
	return SkeinforgeRepository()

def getRadioPluginsAddPluginGroupFrame( directoryPath, importantFileNames, names, repository ):
	"Get the radio plugins and add the plugin frame."
	repository.pluginGroupFrame = settings.PluginGroupFrame()
	radioPlugins = []
	for name in names:
		radioPlugin = settings.RadioPlugin().getFromRadio( name in importantFileNames, repository.pluginGroupFrame.latentStringVar, name, repository, name == importantFileNames[ 0 ] )
		radioPlugin.updateFunction = repository.pluginGroupFrame.update
		radioPlugins.append( radioPlugin )
	defaultRadioButton = settings.getSelectedRadioPlugin( importantFileNames + [ radioPlugins[ 0 ].name ], radioPlugins )
	repository.pluginGroupFrame.getFromPath( defaultRadioButton, directoryPath, repository )
	return radioPlugins

def writeOutput( fileName ):
	"Craft a gcode file."
	skeinforge_craft.writeOutput( fileName )


class SkeinforgeRepository:
	"A class to handle the skeinforge settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		settings.addListsToRepository( 'skeinforge.html', '', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Skeinforge', self, '' )
		versionText = gcodec.getFileText( gcodec.getVersionFileName() )
		self.createdOnLabel = settings.LabelDisplay().getFromName( 'Created On: ' + versionText, self )
		self.profileType = settings.MenuButtonDisplay().getFromName( 'Profile Type: ', self )
		self.profileSelection = settings.MenuButtonDisplay().getFromName( 'Profile Selection: ', self )
		addToProfileMenu( self.profileSelection, self.profileType, self )
		settings.LabelDisplay().getFromName( 'Search:', self )
		reprapSearch = settings.HelpPage().getFromNameAfterHTTP( 'members.axion.net/~enrique/search_reprap.html', 'Reprap', self )
		skeinforgeSearch = settings.HelpPage().getFromNameAfterHTTP( 'members.axion.net/~enrique/search_skeinforge.html', 'Skeinforge', self )
		skeinforgeSearch.column += 2
		webSearch = settings.HelpPage().getFromNameAfterHTTP( 'members.axion.net/~enrique/search_web.html', 'Web', self )
		webSearch.column += 4
		settings.LabelDisplay().getFromName( '', self )
		importantFileNames = [ 'craft', 'profile' ]
		getRadioPluginsAddPluginGroupFrame( getPluginsDirectoryPath(), importantFileNames, getPluginFileNames(), self )
		self.executeTitle = 'Skeinforge'

	def execute( self ):
		"Skeinforge button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )

	def save( self ):
		"Profile has been saved and profile menu should be updated."
		self.profileType.removeMenus()
		self.profileSelection.removeMenus()
		addToProfileMenu( self.profileSelection, self.profileType, self )
		self.profileType.addRadiosToDialog( self.repositoryDialog )
		self.profileSelection.addRadiosToDialog( self.repositoryDialog )


def main():
	"Display the skeinforge dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
