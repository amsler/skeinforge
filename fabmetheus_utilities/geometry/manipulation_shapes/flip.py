"""
Add material to support overhang or remove material at the overhang angle.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation import solid
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.geometry.manipulation_evaluator import matrix
from fabmetheus_utilities.vector3 import Vector3


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = 'GPL 3.0'


globalExecutionOrder = 200


# http://www.opengl.org/discussion_boards/ubbthreads.php?ubb=showflat&Number=269576
# http://www.opengl.org/resources/code/samples/sig99/advanced99/notes/node159.html
#	m.a00 = -2 * norm.x * norm.x + 1;
#	m.a10 = -2 * norm.y * norm.x;
#	m.a20 = -2 * norm.z * norm.x;
#	m.a30 = 0;

#	m.a01 = -2 * norm.x * norm.y;
#	m.a11 = -2 * norm.y * norm.y + 1;
#	m.a21 = -2 * norm.z * norm.y;
#	m.a31 = 0;

#	m.a02 =	-2 * norm.x * norm.z;
#	m.a12 = -2 * norm.y * norm.z;
#	m.a22 = -2 * norm.z * norm.z + 1;
#	m.a32 = 0;

#	m.a03 = -2 * norm.x * d;
#	m.a13 = -2 * norm.y * d;
#	m.a23 = -2 * norm.z * d;
#	m.a33 = 1;

# normal = unit_vector(normal[:3])
# M = numpy.identity(4)
# M[:3, :3] -= 2.0 * numpy.outer(normal, normal)
# M[:3, 3] = (2.0 * numpy.dot(point[:3], normal)) * normal
# return M
def flipPoints(points, prefix, xmlElement):
	"Flip the points."
	origin = evaluate.getVector3ByPrefix(prefix + 'origin', Vector3(), xmlElement)
	axis = evaluate.getVector3ByPrefix(prefix + 'axis', Vector3(1.0, 0.0, 0.0), xmlElement).getNormalized()
	for point in points:
		point.setToVector3(point - 2.0 * axis.dot(point - origin) * axis)

def getShouldReverse(xmlElement):
	"Determine if the loop should be reversed."
	return evaluate.getEvaluatedBooleanDefault(True, 'reverse', xmlElement)

def getManipulatedPaths(close, loop, prefix, sideLength, xmlElement):
	"Get flipped loop."
	flipPoints(loop, prefix, xmlElement)
	if getShouldReverse(xmlElement):
		loop.reverse()
	return [loop]

def getManipulatedGeometryOutput(geometryOutput, xmlElement):
	"Get equated geometryOutput."
	flipPoints(matrix.getConnectionVertexes(geometryOutput), prefix, xmlElement)
	return geometryOutput

def manipulateXMLElement(target, xmlElement):
	"Manipulate the xml element."
	if target.object == None:
		return
	for path in target.object.getPaths():
		flipPoints(path, '', xmlElement)
	flipPoints(target.object.getVertexes(), '', xmlElement)
	if getShouldReverse(xmlElement):
		for path in target.object.getPaths():
			path.reverse()
		for triangleMesh in target.object.getTriangleMeshes():
			for face in triangleMesh.faces:
				face.edgeIndexes = []
				face.vertexIndexes.reverse()
			triangleMesh.edges = []
			triangleMesh.setEdgesForAllFaces()
#	for connectionAxisKey in ['connectionStart', 'connectionEnd', 'xAxis']:
#		connectionAxisValue = evaluate.getVector3ByPrefix(connectionAxisKey, Vector3(), target)
#		if not connectionAxisValue.getIsDefault():
#			flipPoints([connectionAxisValue], '', xmlElement)
#			target.attributeDictionary[connectionAxisKey] = str(connectionAxisValue)


def processXMLElement(xmlElement):
	"Process the xml element."
	solid.processXMLElementByFunction(manipulateXMLElement, xmlElement)
