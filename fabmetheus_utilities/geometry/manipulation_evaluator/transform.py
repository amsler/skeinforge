"""
Boolean geometry transform.

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


globalExecutionOrder = 320


def getManipulatedPaths(close, loop, prefix, sideLength, xmlElement):
	'Get equated paths.'
	transformPoints(loop, prefix, xmlElement)
	return [loop]

def getManipulatedGeometryOutput(geometryOutput, xmlElement):
	'Get equated geometryOutput.'
	transformPoints(matrix.getConnectionVertexes(geometryOutput), 'transform.', xmlElement)
	return geometryOutput

def manipulateXMLElement(target, xmlElement):
	'Manipulate the xml element.'
	transformTetragrid = matrix.getTransformTetragrid('', xmlElement)
	if transformTetragrid == None:
		print('Warning, transformTetragrid was None in transform so nothing will be done for:')
		print(xmlElement)
		return
	matrix.setAttributeDictionaryToMultipliedTetragrid(transformTetragrid, target)

def processXMLElement(xmlElement):
	'Process the xml element.'
	solid.processXMLElementByFunction(manipulateXMLElement, xmlElement)

def transformPoints(points, prefix, xmlElement):
	'Transform the points.'
	transformTetragrid = matrix.getTransformTetragrid(prefix, xmlElement)
	if transformTetragrid == None:
		print('Warning, transformTetragrid was None in transform so nothing will be done for:')
		print(xmlElement)
		return
	for point in points:
		matrix.transformVector3ByMatrix(transformTetragrid, point)
