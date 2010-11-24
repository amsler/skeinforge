#! /usr/bin/env python
"""
This page is in the table of contents.
Scale scales the carving to compensate for shrinkage after the extrusion has cooled.

It is best to only change the XY Plane Scale, because that does not affect other variables.  If you choose to change the Z Axis Scale, that increases the layer thickness so you must increase the feed rate in speed by the same amount and maybe some other variables which depend on layer thickness.

==Operation==
The default 'Activate Scale' checkbox is off.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===XY Plane Scale===
Default is 1.01.

Defines the amount the xy plane of the carving will be scaled.  The xy coordinates will be scaled, but the perimeterWidth is not changed, so this can be changed without affecting other variables.

===Z Axis Scale===
Default is one.

Defines the amount the z axis of the carving will be scaled.  The default is one because changing this changes many variables related to the layer thickness.  For example, the feedRate should be multiplied by the Z Axis Scale because the layers would be farther apart..

===SVG Viewer===
Default is webbrowser.

If the 'SVG Viewer' is set to the default 'webbrowser', the scalable vector graphics file will be sent to the default browser to be opened.  If the 'SVG Viewer' is set to a program name, the scalable vector graphics file will be sent to that program to be opened.

==Examples==
The following examples scale the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and scale.py.


> python scale.py
This brings up the scale dialog.


> python scale.py Screw Holder Bottom.stl
The scale tool is parsing the file:
Screw Holder Bottom.stl
..
The scale tool has created the file:
.. Screw Holder Bottom_scale.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import scale
>>> scale.main()
This brings up the scale dialog.


>>> scale.writeOutput('Screw Holder Bottom.stl')
The scale tool is parsing the file:
Screw Holder Bottom.stl
..
The scale tool has created the file:
.. Screw Holder Bottom_scale.gcode

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from datetime import date
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities.xml_simple_reader import XMLSimpleReader
from fabmetheus_utilities import archive
from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities import settings
from fabmetheus_utilities import svg_writer
from fabmetheus_utilities import xml_simple_writer
from skeinforge_application.skeinforge_utilities import skeinforge_craft
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
from skeinforge_application.skeinforge_utilities import skeinforge_profile
import cStringIO
import os
import sys
import time


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = "$Date: 2008/28/04 $"
__license__ = 'GPL 3.0'


def getCraftedText(fileName, svgText='', repository=None):
	"Scale and convert an svg file or svgText."
	return getCraftedTextFromText(fileName, archive.getTextIfEmpty(fileName, svgText), repository)

def getCraftedTextFromText(fileName, svgText, repository=None):
	"Scale and convert an svgText."
	if gcodec.isProcedureDoneOrFileIsEmpty(svgText, 'scale'):
		return svgText
	if repository == None:
		repository = settings.getReadRepository(ScaleRepository())
	if not repository.activateScale.value:
		return svgText
	return ScaleSkein().getCraftedGcode(fileName, repository, svgText)

def getNewRepository():
	"Get the repository constructor."
	return ScaleRepository()

def setSliceXMLElementScale(decimalPlacesCarried, sliceXMLElement, sliceXMLElementIndex, xyPlaneScale, zAxisScale):
	"Set the slice element scale."
	idValue = sliceXMLElement.attributeDictionary['id'].strip()
	z = float(idValue[len('z:') :].strip())
	roundedZ = euclidean.getRoundedToPlacesString(decimalPlacesCarried, z * zAxisScale)
	idValue = 'z:%s' % roundedZ
	sliceXMLElement.attributeDictionary['id'] = idValue
	textXMLElement = sliceXMLElement.getFirstChildWithClassName('text')
	textXMLElement.text = 'Layer %s, %s' % (sliceXMLElementIndex, idValue)
	pathXMLElement = sliceXMLElement.getFirstChildWithClassName('path')
	pathDictionary = pathXMLElement.attributeDictionary
	dataAttribute = pathDictionary['d']
	dataSplitLine = dataAttribute.split()
	scaledOutput = cStringIO.StringIO()
	for dataWordIndex, dataWord in enumerate(dataSplitLine):
		if dataWordIndex != 0:
			scaledOutput.write(' ')
		if dataWord.replace('.', '0').replace('-', '0').isdigit():
			scaledOutput.write(euclidean.getRoundedToPlacesString(decimalPlacesCarried, xyPlaneScale * float(dataWord)))
		else:
			scaledOutput.write(dataWord)
	pathDictionary['d'] = scaledOutput.getvalue()

def writeOutput(fileName):
	'Scale the carving.'
	skeinforge_craft.writeSVGTextWithNounMessage(fileName, ScaleRepository())


class ScaleRepository:
	"A class to handle the scale settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository('skeinforge_application.skeinforge_plugins.craft_plugins.scale.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName(fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Scale', self, '')
		self.activateScale = settings.BooleanSetting().getFromValue('Activate Scale:', self, False)
		self.xyPlaneScale = settings.FloatSpin().getFromValue(0.99, 'XY Plane Scale (ratio):', self, 1.03, 1.01)
		self.zAxisScale = settings.FloatSpin().getFromValue(0.99, 'Z Axis Scale (ratio):', self, 1.02, 1.005)
		self.svgViewer = settings.StringSetting().getFromValue('SVG Viewer:', self, 'webbrowser')
		self.executeTitle = 'Scale'

	def execute(self):
		"Scale button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode(self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled)
		for fileName in fileNames:
			writeOutput(fileName)


class ScaleSkein:
	"A class to scale a skein of extrusions."
	def getCraftedGcode(self, fileName, repository, svgText):
		"Parse svgText and store the scale svgText."
		xmlParser = XMLSimpleReader(fileName, None, svgText)
		root = xmlParser.getRoot()
		if root == None:
			print('Warning, root was None in getCraftedGcode in ScaleSkein, so nothing will be done for:')
			print(fileName)
			return ''
		sliceXMLElements = svg_writer.getSliceXMLElements(root)
		sliceDictionary = svg_writer.getSliceDictionary(root)
		decimalPlacesCarried = int(sliceDictionary['decimalPlacesCarried'])
		xyPlaneScale = repository.xyPlaneScale.value
		zAxisScale = repository.zAxisScale.value
		scaledLayerThickness = zAxisScale * float(sliceDictionary['layerThickness'])
		sliceDictionary['layerThickness'] = euclidean.getRoundedToPlacesString(decimalPlacesCarried, scaledLayerThickness)
		procedures = sliceDictionary['procedureDone'].split(',')
		procedures.append('scale')
		sliceDictionary['procedureDone'] = ','.join(procedures)
		for sliceXMLElementIndex, sliceXMLElement in enumerate(sliceXMLElements):
			setSliceXMLElementScale(decimalPlacesCarried, sliceXMLElement, sliceXMLElementIndex, xyPlaneScale, zAxisScale)
		return xml_simple_writer.getBeforeRootOutput(xmlParser)


def main():
	"Display the scale dialog."
	if len(sys.argv) > 1:
		writeOutput(' '.join(sys.argv[1 :]))
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
