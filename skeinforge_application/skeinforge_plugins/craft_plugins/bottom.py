#! /usr/bin/env python
"""
This page is in the table of contents.
Bottom sets the bottom of the carving to the defined altitude.

==Operation==
The default 'Activate Bottom' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Altitude===
Default is zero.

Defines the altitude of the bottom of the model.  The bottom slice have a z of the altitude plus half the layer thickness.

===SVG Viewer===
Default is webbrowser.

If the 'SVG Viewer' is set to the default 'webbrowser', the scalable vector graphics file will be sent to the default browser to be opened.  If the 'SVG Viewer' is set to a program name, the scalable vector graphics file will be sent to that program to be opened.

==Examples==
The following examples bottom the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and bottom.py.


> python bottom.py
This brings up the bottom dialog.


> python bottom.py Screw Holder Bottom.stl
The bottom tool is parsing the file:
Screw Holder Bottom.stl
..
The bottom tool has created the file:
.. Screw Holder Bottom_bottom.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import bottom
>>> bottom.main()
This brings up the bottom dialog.


>>> bottom.writeOutput('Screw Holder Bottom.stl')
The bottom tool is parsing the file:
Screw Holder Bottom.stl
..
The bottom tool has created the file:
.. Screw Holder Bottom_bottom.gcode

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
	"Bottom and convert an svg file or svgText."
	return getCraftedTextFromText(fileName, archive.getTextIfEmpty(fileName, svgText), repository)

def getCraftedTextFromText(fileName, svgText, repository=None):
	"Bottom and convert an svgText."
	if gcodec.isProcedureDoneOrFileIsEmpty(svgText, 'bottom'):
		return svgText
	if repository == None:
		repository = settings.getReadRepository(BottomRepository())
	if not repository.activateBottom.value:
		return svgText
	return BottomSkein().getCraftedGcode(fileName, repository, svgText)

def getNewRepository():
	"Get the repository constructor."
	return BottomRepository()

def getSliceXMLElementZ(sliceXMLElement):
	"Get the slice element z."
	idValue = sliceXMLElement.attributeDictionary['id'].strip()
	return float(idValue[len('z:') :].strip())

def setSliceXMLElementZ(decimalPlacesCarried, sliceXMLElement, sliceXMLElementIndex, z):
	"Set the slice element z."
	roundedZ = euclidean.getRoundedToPlacesString(decimalPlacesCarried, z)
	idValue = 'z:%s' % roundedZ
	sliceXMLElement.attributeDictionary['id'] = idValue
	textXMLElement = sliceXMLElement.getFirstChildWithClassName('text')
	textXMLElement.text = 'Layer %s, %s' % (sliceXMLElementIndex, idValue)

def writeOutput(fileName):
	'Bottom the carving.'
	skeinforge_craft.writeSVGTextWithNounMessage(fileName, BottomRepository())


class BottomRepository:
	"A class to handle the bottom settings."
	def __init__(self):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository('skeinforge_application.skeinforge_plugins.craft_plugins.bottom.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName(fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Bottom', self, '')
		self.activateBottom = settings.BooleanSetting().getFromValue('Activate Bottom:', self, True )
		self.altitude = settings.FloatSpin().getFromValue(-1.0, 'Altitude (mm):', self, 1.0, 0.0)
		self.svgViewer = settings.StringSetting().getFromValue('SVG Viewer:', self, 'webbrowser')
		self.executeTitle = 'Bottom'

	def execute(self):
		"Bottom button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode(self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled)
		for fileName in fileNames:
			writeOutput(fileName)


class BottomSkein:
	"A class to bottom a skein of extrusions."
	def getCraftedGcode(self, fileName, repository, svgText):
		"Parse svgText and store the bottom svgText."
		xmlParser = XMLSimpleReader(fileName, None, svgText)
		root = xmlParser.getRoot()
		if root == None:
			print('Warning, root was None in getCraftedGcode in BottomSkein, so nothing will be done for:')
			print(fileName)
			return ''
		sliceXMLElements = svg_writer.getSliceXMLElements(root)
		sliceDictionary = svg_writer.getSliceDictionary(root)
		decimalPlacesCarried = int(sliceDictionary['decimalPlacesCarried'])
		layerThickness = float(sliceDictionary['layerThickness'])
		procedures = sliceDictionary['procedureDone'].split(',')
		procedures.append('bottom')
		sliceDictionary['procedureDone'] = ','.join(procedures)
		zMinimum = 987654321.0
		for sliceXMLElement in sliceXMLElements:
			zMinimum = min(getSliceXMLElementZ(sliceXMLElement), zMinimum)
		deltaZ = repository.altitude.value + 0.5 * layerThickness - zMinimum
		for sliceXMLElementIndex, sliceXMLElement in enumerate(sliceXMLElements):
			z = getSliceXMLElementZ(sliceXMLElement) + deltaZ
			setSliceXMLElementZ(decimalPlacesCarried, sliceXMLElement, sliceXMLElementIndex, z)
		return xml_simple_writer.getBeforeRootOutput(xmlParser)


def main():
	"Display the bottom dialog."
	if len(sys.argv) > 1:
		writeOutput(' '.join(sys.argv[1 :]))
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
