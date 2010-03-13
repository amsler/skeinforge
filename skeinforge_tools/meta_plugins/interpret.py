"""
This page is in the table of contents.
Interpret is a script to access the plugins which interpret a gcode file.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.fabmetheus_utilities import settings
from skeinforge_utilities import skeinforge_interpret
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getNewRepository():
	"Get the repository constructor."
	return skeinforge_interpret.InterpretRepository()

def writeOutput( fileName ):
	"Write file interpretation, if activate interpret is selected."
	skeinforge_interpret.interpretFile( fileName )


def main():
	"Display the interpret dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
