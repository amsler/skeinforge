"""
Boolean geometry rotate.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation import solid
from fabmetheus_utilities.geometry.manipulation_evaluator import matrix
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = '$Date: 2008/02/05 $'
__license__ = 'GPL 3.0'


globalExecutionOrder = 360


def getManipulatedPaths(close, loop, prefix, sideLength, xmlElement):
	'Get equated paths.'
	rotatePoints(loop, prefix, xmlElement)
	return [loop]

def getManipulatedGeometryOutput(geometryOutput, xmlElement):
	'Get equated geometryOutput.'
	rotatePoints(matrix.getConnectionVertexes(geometryOutput), 'rotate.', xmlElement)
	return geometryOutput

def manipulateXMLElement(target, xmlElement):
	'Manipulate the xml element.'
	rotateTetragrid = matrix.getRotateTetragrid('', xmlElement)
	if rotateTetragrid == None:
		print('Warning, rotateTetragrid was None in rotate so nothing will be done for:')
		print(xmlElement)
		return
	matrix.setAttributeDictionaryToMultipliedTetragrid(rotateTetragrid, target)

def processXMLElement(xmlElement):
	'Process the xml element.'
	solid.processXMLElementByFunction(manipulateXMLElement, xmlElement)

def rotatePoints(points, prefix, xmlElement):
	'Rotate the points.'
	rotateTetragrid = matrix.getRotateTetragrid(prefix, xmlElement)
	if rotateTetragrid == None:
		print('Warning, rotateTetragrid was None in rotate so nothing will be done for:')
		print(xmlElement)
		return
	for point in points:
		matrix.transformVector3ByMatrix(rotateTetragrid, point)
