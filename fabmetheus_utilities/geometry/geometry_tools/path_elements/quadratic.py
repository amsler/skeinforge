"""
Quadratic vertexes.

From:
http://www.w3.org/TR/SVG/paths.html#PathDataQuadraticBezierCommands

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities.geometry.creation import lineation
from fabmetheus_utilities.geometry.geometry_utilities import evaluate
from fabmetheus_utilities.vector3 import Vector3
from fabmetheus_utilities import svg_reader


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__credits__ = 'Art of Illusion <http://www.artofillusion.org/>'
__date__ = "$Date: 2008/02/05 $"
__license__ = 'GPL 3.0'


def getQuadraticPath(xmlElement):
	"Get the quadratic path."
	end = evaluate.getVector3FromXMLElement(xmlElement)
	previousXMLElement = xmlElement.getPreviousXMLElement()
	if previousXMLElement == None:
		print('Warning, can not get previousXMLElement in getQuadraticPath in quadratic for:')
		print(xmlElement)
		return [end]
	begin = xmlElement.getPreviousVertex(Vector3())
	controlPoint = evaluate.getVector3ByPrefix(None, 'controlPoint', xmlElement)
	if controlPoint == None:
		oldControlPoint = evaluate.getVector3ByPrefixes(['controlPoint','controlPoint1'], None, previousXMLElement)
		if oldControlPoint == None:
			oldControlPoint = end
		controlPoint = begin + begin - oldControlPoint
		evaluate.addVector3ToXMLElement('controlPoint', controlPoint, xmlElement)
	return svg_reader.getQuadraticPoints(begin, controlPoint, end, lineation.getNumberOfBezierPoints(begin, end, xmlElement))

def processXMLElement(xmlElement):
	"Process the xml element."
	xmlElement.parent.object.vertexes += getQuadraticPath(xmlElement)
