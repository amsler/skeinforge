"""
Solid.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.geometry_tools import path
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.geometry.solids import group
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = "GPL 3.0"


def getGeometryOutput( xmlElement ):
	"Get geometry output from solid."
	geometryOutput = []
	paths = evaluate.getPathsByKeys( [ 'path', 'paths', 'target' ], xmlElement )
	for path in paths:
		sideLoop = SideLoop( path )
		geometryOutput += getGeometryOutputByLoop( sideLoop, xmlElement )
	return getUnpackedLoops( geometryOutput )
#
#def getGeometryOutputByLoop( sideLoop, xmlElement ):
#	"Get geometry output by side loop."
#	sideLoop.rotate( xmlElement )
#	return getUnpackedLoops( getGeometryOutputByManipulation( sideLoop, xmlElement ) )
#
#def processXMLElement( xmlElement, xmlProcessor ):
#	"Process the xml element."
#	processXMLElementByGeometry( getGeometryOutput( xmlElement ), xmlElement, xmlProcessor )

#def processXMLElementByGeometry( geometryOutput, xmlElement, xmlProcessor ):
#	"Process the xml element by geometryOutput."
#	firstElement = None
#	if len( geometryOutput ) > 0:
#		firstElement = geometryOutput[ 0 ]
#	if firstElement.__class__ == list:
#		if len( firstElement ) > 1:
#			group.convertXMLElementRenameByPaths( geometryOutput, xmlElement, xmlProcessor )
#		else:
#			path.convertXMLElementRename( firstElement, xmlElement, xmlProcessor )
#	else:
#		path.convertXMLElementRename( geometryOutput, xmlElement, xmlProcessor )
#	xmlProcessor.processXMLElement( xmlElement )

def getGeometryOutputByManipulation( geometryOutput, xmlElement ):
	"Get geometryOutput manipulated by the plugins in the manipulation shapes & solids folders."
	xmlProcessor = xmlElement.getXMLProcessor()
	matchingPlugins = evaluate.getFromCreationEvaluatorPlugins( xmlProcessor.manipulationEvaluatorDictionary, xmlElement )
	matchingPlugins += evaluate.getMatchingPlugins( xmlProcessor.manipulationShapeDictionary, xmlElement )
	matchingPlugins.sort( evaluate.compareExecutionOrderAscending )
	for matchingPlugin in matchingPlugins:
		geometryOutput = matchingPlugin.getManipulatedGeometryOutput( geometryOutput, xmlElement )
	return geometryOutput

def processXMLElementByFunction( manipulationFunction, xmlElement, xmlProcessor ):
	"Process the xml element."
	target = evaluate.getXMLElementByKey( 'target', xmlElement )
	if target == None:
		print( 'Warning, translate could not get target for:' )
		print( xmlElement )
		return
	manipulationFunction( target, xmlElement, xmlProcessor )
