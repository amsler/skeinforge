"""
Boolean geometry utilities.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.solids.solid_tools import matrix4x4
from fabmetheus_utilities import gcodec


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def evaluateKeyValue( key, xmlElement ):
	"Evaluate the key value."
	value = getEvaluatedValue( key, xmlElement )
	if value == '':
		print( 'Warning, %s does not evaluate.' % xmlElement.attributeDictionary[ key ] )
		del xmlElement.attributeDictionary[ key ]
		return
	xmlElement.attributeDictionary[ key ] = value

def getArchivableObject( archivableClass, xmlElement ):
	"Get the archivable object."
	archivableObject = archivableClass()
	archivableObject.xmlElement = xmlElement
	xmlElement.object = archivableObject
	archivableObject.setToObjectAttributeDictionary()
	xmlElement.parent.object.archivableObjects.append( archivableObject )
	return archivableObject

def getEvaluatedDictionary( xmlElement ):
	"Get the evaluated dictionary."
	for key in xmlElement.attributeDictionary.keys():
		evaluateKeyValue( key, xmlElement )
	return xmlElement.attributeDictionary

def getEvaluatedIDValue( key, xmlElement, value ):
	"Evaluate the id value."
	strippedValue = value[ len( 'id.' ) : ]
	dotIndex = strippedValue.find( '.' )
	if dotIndex < 0:
		return ''
	idString = strippedValue[ : dotIndex ]
	if idString not in xmlElement.getRootElement().idDictionary:
		return ''
	idElement = xmlElement.getRootElement().idDictionary[ idString ]
	idKey = strippedValue[ dotIndex + 1 : ]
	if idKey not in idElement.attributeDictionary:
		return ''
	return str( idElement.attributeDictionary[ idKey ] ).lstrip()

def getEvaluatedParentValue( key, xmlElement, value ):
	"Evaluate the parent value."
	parent = xmlElement
	while gcodec.getHasPrefix( value, 'parent.' ):
		parent = parent.parent
		if parent == None:
			return ''
		value = value[ len( 'parent.' ) : ]
	if value not in parent.attributeDictionary:
		return ''
	return str( parent.attributeDictionary[ value ] ).lstrip()

def getEvaluatedRootValue( key, xmlElement, value ):
	"Evaluate the parent value."
	value = value[ len( 'root.' ) : ]
	if value not in xmlElement.getRootElement().attributeDictionary:
		return ''
	return str( xmlElement.getRootElement().attributeDictionary[ value ] ).lstrip()

def getEvaluatedValue( key, xmlElement ):
	"Get the evaluated dictionary."
	value = str( xmlElement.attributeDictionary[ key ] ).lstrip()
	if key == 'id':
		return value
	if gcodec.getHasPrefix( value, 'id.' ):
		return getEvaluatedIDValue( key, xmlElement, value )
	if gcodec.getHasPrefix( value, 'parent.' ):
		return getEvaluatedParentValue( key, xmlElement, value )
	if gcodec.getHasPrefix( value, 'root.' ):
		return getEvaluatedRootValue( key, xmlElement, value )
	return value

def getVisibleObjects( archivableObjects ):
	"Get the visible objects."
	visibleObjects = []
	for archivableObject in archivableObjects:
		if archivableObject.getVisible():
			visibleObjects.append( archivableObject )
	return visibleObjects

def processArchivable( archivableClass, xmlElement ):
	"Get any new elements and process the archivable."
	if xmlElement == None:
		return
	getArchivableObject( archivableClass, xmlElement )
	xmlElement.getRootElement().xmlProcessor.processChildren( xmlElement )

def processShape( shapeClass, xmlElement ):
	"Get any new elements and process the shape."
	if xmlElement == None:
		return
	archivableObject = getArchivableObject( shapeClass, xmlElement )
	matrix4x4.setXMLElementMatrixToMatrixAttributeDictionary( xmlElement.attributeDictionary, xmlElement.object.matrix4X4, xmlElement )
	xmlElement.getRootElement().xmlProcessor.processChildren( xmlElement )
