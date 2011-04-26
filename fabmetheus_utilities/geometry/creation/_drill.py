"""
Drill negative solid.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation import extrude
from fabmetheus_utilities.geometry.creation import lineation
from fabmetheus_utilities.geometry.creation import solid
from fabmetheus_utilities.geometry.creation import teardrop
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import euclidean
import math


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = 'GPL 3.0'


def getGeometryOutput(derivation, xmlElement):
	"Get vector3 vertexes from attribute dictionary."
	if derivation == None:
		derivation = DrillDerivation(xmlElement)
	extrudeDerivation = extrude.ExtrudeDerivation()
	negatives = []
	teardrop.addNegativesByDerivation(derivation.end, extrudeDerivation, negatives, derivation.radius, derivation.start, xmlElement)
	return extrude.getGeometryOutputByNegativesPositives(extrudeDerivation, [], negatives, xmlElement)

def getGeometryOutputByArguments(arguments, xmlElement):
	"Get vector3 vertexes from attribute dictionary by arguments."
	evaluate.setAttributeDictionaryByArguments(['radius', 'start', 'end'], arguments, xmlElement)
	return getGeometryOutput(None, xmlElement)

def processXMLElement(xmlElement):
	"Process the xml element."
	solid.processXMLElementByGeometry(getGeometryOutput(None, xmlElement), xmlElement)


class DrillDerivation:
	"Class to hold drill variables."
	def __init__(self, xmlElement):
		'Set defaults.'
		self.end = evaluate.getVector3ByPrefix(Vector3(0.0, 0.0, 1.0), 'end', xmlElement)
		self.start = evaluate.getVector3ByPrefix(Vector3(), 'start', xmlElement)
		self.radius = lineation.getFloatByPrefixBeginEnd('radius', 'diameter', 1.0, xmlElement)
		size = evaluate.getEvaluatedFloatDefault(None, 'size', xmlElement)
		if size != None:
			self.radius = 0.5 * size
		self.xmlElement = xmlElement

	def __repr__(self):
		"Get the string representation of this DrillDerivation."
		return str(self.__dict__)
