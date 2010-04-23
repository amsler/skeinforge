"""
Boolean geometry group of solids.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities.solids import group
from fabmetheus_utilities.solids.solid_utilities import geomancer
from fabmetheus_utilities.xml_simple_parser import XMLSimpleParser
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
import cStringIO
import os


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getXMLFromCarvingFileName( fileName ):
	"Get xml text from xml text."
	carving = fabmetheus_interpret.getCarving( fileName )
	if carving == None:
		return ''
	output = cStringIO.StringIO()
	carving.addXML( 0, output )
	return output.getvalue()

def getXMLFromFileName( fileName ):
	"Get xml text from xml text."
	if gcodec.getHasSuffix( fileName, '.xml' ):
		return getXMLFromXMLFileName( fileName )
	return getXMLFromCarvingFileName( fileName )

def getXMLFromXMLFileName( fileName ):
	"Get xml text from xml text."
	xmlText = gcodec.getFileText( fileName )
	xmlText = str( BooleanGeometryParser( xmlText ) )
	if xmlText != '':
		return xmlText
	return getXMLFromCarvingFileName( fileName )

def processXMLElement( xmlElement ):
	"Process the xml element."
	fileName = geomancer.getEvaluatedValue( 'file', xmlElement )
	if fileName == None:
		return
	parserFileName = xmlElement.getRootElement().parser.fileName
	absoluteFileName = gcodec.getAbsoluteFolderPath( parserFileName, fileName )
	xmlText = getXMLFromFileName( absoluteFileName )
	if xmlText == '':
		print( 'The file %s could not be found in the folder which the xml boolean geometry file is in.' % fileName )
		return
	XMLSimpleParser( xmlElement.getRootElement().parser.fileName, xmlElement, xmlText )
	group.processShape( group.Group, xmlElement )
	baseNameUntilDot = gcodec.getUntilDot( os.path.basename( absoluteFileName ) )
	xmlElement.addIDIfUndefined( baseNameUntilDot )


class BooleanGeometryParser:
	"A simple xml parser."
	def __init__( self, xmlText ):
		"Add empty lists."
		self.isInBooleanGeometry = False
		self.lines = gcodec.getTextLines( xmlText )
		self.output = cStringIO.StringIO()
		for line in self.lines:
			self.parseLine( line )
	
	def __repr__( self ):
		"Get the string representation of this parser."
		return self.output.getvalue()

	def parseLine( self, line ):
		"Parse a gcode line and add it to the inset skein."
		line = line.lstrip()
		if len( line ) < 1:
			return
		if line[ : len( '</' ) ] == '</':
			lineAfterEndTagSymbol = line[ len( '</' ) : ].lstrip()
			if lineAfterEndTagSymbol[ : len( 'booleangeometry' ) ] == 'booleangeometry':
				self.isInBooleanGeometry = False
				return
		if line[ : len( '<' ) ] == '<':
			lineAfterBeginTagSymbol = line[ len( '<' ) : ].lstrip()
			if lineAfterBeginTagSymbol[ : len( 'booleangeometry' ) ] == 'booleangeometry':
				self.isInBooleanGeometry = True
				return
		if self.isInBooleanGeometry:
			self.output.write( line + '\n' )
