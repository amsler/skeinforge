"""
XML tag writer utilities.

"""


from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

import cStringIO


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Nophead <http://hydraraptor.blogspot.com/>\nArt of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def addBeginXMLTag( attributeDictionary, depth, name, output ):
	"Add the begin xml tag."
	depthStart = '\t' * depth
	output.write( '%s<%s%s>\n' % ( depthStart, name, getAttributeDictionaryString( attributeDictionary ) ) )

def addClosedXMLTag( attributeDictionary, depth, name, output ):
	"Add the closed xml tag."
	depthStart = '\t' * depth
	output.write( '%s<%s%s />\n' % ( depthStart, name, getAttributeDictionaryString( attributeDictionary ) ) )

def addEndXMLTag( depth, name, output ):
	"Add the end xml tag."
	depthStart = '\t' * depth
	output.write( '%s</%s>\n' % ( depthStart, name ) )

def addXMLFromLoopComplexZ( attributeDictionary, depth, loop, output, z ):
	"Add xml from loop."
	addBeginXMLTag( attributeDictionary, depth, 'path', output )
	for pointComplexIndex in xrange( len( loop ) ):
		pointComplex = loop[ pointComplexIndex ]
		addXMLFromXYZ( depth + 1, pointComplexIndex, output, pointComplex.real, pointComplex.imag, z )
	addEndXMLTag( depth, 'path', output )

def addXMLFromObjects( depth, objects, output ):
	"Add xml from objects."
	for object in objects:
		object.addXML( depth, output )

def addXMLFromVertices( depth, output, vertices ):
	"Add xml from loop."
	for vertexIndex in xrange( len( vertices ) ):
		vertex = vertices[ vertexIndex ]
		addXMLFromXYZ( depth + 1, vertexIndex, output, vertex.x, vertex.y, vertex.z )

def addXMLFromXYZ( depth, index, output, x, y, z ):
	"Add xml from x, y & z."
	attributeDictionary = { 'index' : str( index ) }
	if x != 0.0:
		attributeDictionary[ 'x' ] = str( x )
	if y != 0.0:
		attributeDictionary[ 'y' ] = str( y )
	if z != 0.0:
		attributeDictionary[ 'z' ] = str( z )
	addClosedXMLTag( attributeDictionary, depth, 'vertex', output )

def compareAttributeKeyAscending( key, otherKey ):
	"Get comparison in order to sort attribute keys in ascending order, with the id key first."
	if key == 'id':
		return - 1
	if otherKey == 'id':
		return 1
	if key < otherKey:
		return - 1
	return int( key > otherKey )

def getAttributeDictionaryString( attributeDictionary ):
	"Add the closed xml tag."
	attributeDictionaryString = ''
	attributeDictionaryKeys = attributeDictionary.keys()
	attributeDictionaryKeys.sort( compareAttributeKeyAscending )
	for attributeDictionaryKey in attributeDictionaryKeys:
		value = attributeDictionary[ attributeDictionaryKey ]
		if value != '':
			attributeDictionaryString += ' %s="%s"' % ( attributeDictionaryKey, value )
	return attributeDictionaryString

def getBeginGeometryXMLOutput( xmlElement ):
	"Get the beginning of the string representation of this boolean geometry object info."
	output = getBeginXMLOutput()
	attributeDictionary = {}
	if xmlElement != None:
		root = xmlElement.getRoot()
		attributeDictionary = root.attributeDictionary
	attributeDictionary[ 'version' ] = '2010-03-29'
	addBeginXMLTag( attributeDictionary, 0, 'fabmetheus', output )
	return output

def getBeginXMLOutput():
	"Get the beginning of the string representation of this object info."
	output = cStringIO.StringIO()
	output.write( "<?xml version='1.0' ?>\n" )
	return output

def getDictionaryWithoutList( dictionary, withoutList ):
	"Get the dictionary without the keys in the list."
	dictionaryWithoutList = {}
	for key in dictionary:
		if key not in withoutList:
			dictionaryWithoutList[ key ] = dictionary[ key ]
	return dictionaryWithoutList

def getEndGeometryXMLString( output ):
	"Get the string representation of this object info."
	addEndXMLTag( 0, 'fabmetheus', output )
	return output.getvalue()
