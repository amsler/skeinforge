"""
This page is in the table of contents.
Raft is a script to create a raft, elevate the nozzle and set the temperature.

Allan Ecker aka The Masked Retriever's has written two quicktips for raft which follow below.
"Skeinforge Quicktip: The Raft, Part 1" at:
http://blog.thingiverse.com/2009/07/14/skeinforge-quicktip-the-raft-part-1/
"Skeinforge Quicktip: The Raft, Part II" at:
http://blog.thingiverse.com/2009/08/04/skeinforge-quicktip-the-raft-part-ii/

The default 'Activate Raft' checkbox is on.  When it is on, the functions described below will work, when it is off, the functions will not be called.  The raft script sets the temperature.  If the "Activate Raft, Elevate Nozzle, Orbit and Set Altitude" checkbox is checked, the script will also create a raft, elevate the nozzle, orbit and set the altitude of the bottom of the raft.

Raft is based on the Nophead's reusable raft, which has a base layer running one way, and a couple of perpendicular layers above.  Each set of layers can be set to a different temperature.  There is the option of having the extruder orbit the raft for a while, so the heater barrel has time to reach a different temperature, without ooze accumulating around the nozzle.

The important values for the raft preferences are the temperatures of the raft, the first layer and the next layers.  These will be different for each material.  The default preferences for ABS, HDPE, PCL & PLA are extrapolated from Nophead's experiments.

This brings up the profile preferences dialog.  In that dialog you can add or delete a profile on the listbox and you change the selected profile.  After you can change the selected profile, run raft again.  If there are preferences for the new profile, those will be in the raft dialog.  If there are no preferences for the new profile, the preferences will be set to defaults and you will have to set new preferences for the new profile.

The "Base Infill Density" preference is the infill density ratio of the base of the raft, the default ratio is half.  The "Base Layer Height over Layer Thickness" preference is the ratio of the height & width of the base layer compared to the height and width of the shape infill, the default is two.  The feed rate will be slower for raft layers which have thicker extrusions than the shape infill.  The "Base Layers" preference is the number of base layers, the default is one.  The "Base Nozzle Lift over Base Layer Thickness" is the amount the nozzle is above the center of the extrusion divided by the base layer thickness.

The interface of the raft has equivalent preferences called "Interface Infill Density", "Interface Layer Thickness over Extrusion Height", "Interface Layers" and "Interface Nozzle Lift over Base Layer Thickness".  The shape has the equivalent preference of called "Operating Nozzle Lift over Layer Thickness".

The altitude that the bottom of the raft will be set to the "Bottom Altitude" preference.

The raft fills a rectangle whose base size is the rectangle around the bottom layer of the shape expanded on each side by the 'Raft Margin' plus the 'Raft Additional Margin over Length (%)' percentage times the length of the side.  The default 'Raft Margin' is 3 millimeters and the default 'Raft Additional Margin over Length (%)' is 1 percent.  The rectangle size is then reduced by the 'Infill Overhang' ratio times the width of the extrusion of the raft.

In the "Support Material Choice" radio button group, if "No Support Material" is selected then raft will not add support material, this is the default because the raft takes time to generate.  If "Support Material Everywhere" is selected, support material will be added wherever there are overhangs, even inside the object; because support material inside objects is hard or impossible to remove, this option should only be chosen if the shape has a cavity that needs support and there is some way to extract the support material.  If "Support Material on Exterior Only" is selected, support material will be added only the exterior of the object; this is the best option for most objects which require support material.  The "Support Minimum Angle" preference is the minimum angle that a surface overhangs before support material is added, the default is sixty degrees. The "Support Flow Rate over Operating Flow Rate" is the ratio of the flow rate when the support is extruded over the operating flow rate.  With a number less than one, the support flow rate will be smaller so the support will be thinner and easier to remove, the default is 0.9.  The "Support Gap over Perimeter Extrusion Width" is the gap between the support material and the object over the perimeter extrusion width, the default is 0.5.

If support material is generated, then if there is a file support_start.gcode, it will add that to the start of the support gcode. After it has added the support gcode, it will add the file support_end.gcode if it exists.  Raft does not care if the text file names are capitalized, but some file systems do not handle file name cases properly, so to be on the safe side you should give them lower case names.  Raft looks for those files in the alterations folder in the .skeinforge folder in the home directory. If it doesn't find the file it then looks in the alterations folder in the skeinforge_tools folder. If it doesn't find anything there it looks in the skeinforge_tools folder.

The extruder will orbit for at least "Temperature Change Time Before Raft" seconds before extruding the raft.  It will orbit for at least "Temperature Change Time Before First Layer Outline" seconds before extruding the outline of the first layer of the shape.  It will orbit for at least "Temperature Change Time Before Next Threads" seconds before extruding within the outline of the first layer of the shape and before extruding the next layers of the shape.  It will orbit for at least "Temperature Change Time Before Support Layers" seconds before extruding the support layers.  It will orbit for at least "Temperature Change Time Before Supported Layers" seconds before extruding the layer of the shape above the support layer.  If a time is zero, it will not orbit.

The "Temperature of Raft" preference sets the temperature of the raft.  The "Temperature of Shape First Layer Outline" preference sets the temperature of the outline of the first layer of the shape.  The "Temperature of Shape First Layer Within" preference sets the temperature within the outline of the first layer of the shape.  The "Temperature of Shape Next Layers" preference sets the temperature of the next layers of the shape.  The "Temperature of Support Layers" preference sets the temperature of the support layer.  The "Temperature of Supported Layers" preference sets the temperature of the layer of the shape above the support layer.

The following examples raft the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and raft.py.  Pictures of rafting in action are available from the Metalab blog at:
http://reprap.soup.io/?search=rafting


> python raft.py
This brings up the raft dialog.


> python raft.py Screw Holder Bottom.stl
The raft tool is parsing the file:
Screw Holder Bottom.stl
..
The raft tool has created the file:
Screw Holder Bottom_raft.gcode


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import raft
>>> raft.main()
This brings up the raft dialog.


>>> raft.writeOutput( 'Screw Holder Bottom.stl' )
Screw Holder Bottom.stl
The raft tool is parsing the file:
Screw Holder Bottom.stl
..
The raft tool has created the file:
Screw Holder Bottom_raft.gcode


"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.meta_plugins import polyfile
from skeinforge_tools.skeinforge_utilities import consecution
from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import intercircle
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools.skeinforge_utilities import preferences
from skeinforge_tools.skeinforge_utilities.vector3 import Vector3
import math
import os
import sys


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


#maybe later wide support
#raft outline temperature http://hydraraptor.blogspot.com/2008/09/screw-top-pot.html
def getCraftedText( fileName, text = '', raftRepository = None ):
	"Raft the file or text."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, text ), raftRepository )

def getCraftedTextFromText( gcodeText, raftRepository = None ):
	"Raft a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'raft' ):
		return gcodeText
	if raftRepository == None:
		raftRepository = preferences.getReadRepository( RaftRepository() )
	if not raftRepository.activateRaft.value:
		return gcodeText
	return RaftSkein().getCraftedGcode( gcodeText, raftRepository )

def getCrossHatchPointLine( crossHatchPointLineTable, y ):
	"Get the cross hatch point line."
	if not crossHatchPointLineTable.has_key( y ):
		crossHatchPointLineTable[ y ] = {}
	return crossHatchPointLineTable[ y ]

def getEndpointsFromYIntersections( x, yIntersections ):
	"Get endpoints from the y intersections."
	endpoints = []
	for yIntersectionIndex in xrange( 0, len( yIntersections ), 2 ):
		firstY = yIntersections[ yIntersectionIndex ]
		secondY = yIntersections[ yIntersectionIndex + 1 ]
		if firstY != secondY:
			firstComplex = complex( x, firstY )
			secondComplex = complex( x, secondY )
			endpointFirst = euclidean.Endpoint()
			endpointSecond = euclidean.Endpoint().getFromOtherPoint( endpointFirst, secondComplex )
			endpointFirst.getFromOtherPoint( endpointSecond, firstComplex )
			endpoints.append( endpointFirst )
			endpoints.append( endpointSecond )
	return endpoints

def getExtendedLineSegment( extensionDistance, lineSegment, loopXIntersections ):
	"Get extended line segment."
	pointBegin = lineSegment[ 0 ].point
	pointEnd = lineSegment[ 1 ].point
	segment = pointEnd - pointBegin
	segmentLength = abs( segment )
	if segmentLength <= 0.0:
		print( "This should never happen in getExtendedLineSegment in raft, the segment should have a length greater than zero." )
		print( lineSegment )
		return None
	segmentExtend = segment * extensionDistance / segmentLength
	lineSegment[ 0 ].point = pointBegin - segmentExtend
	lineSegment[ 1 ].point = pointEnd + segmentExtend
	for loopXIntersection in loopXIntersections:
		setExtendedPoint( lineSegment[ 0 ], pointBegin, loopXIntersection )
		setExtendedPoint( lineSegment[ 1 ], pointEnd, loopXIntersection )
	return lineSegment

def getNewRepository():
	"Get the repository constructor."
	return RaftRepository()

def setExtendedPoint( lineSegmentEnd, pointOriginal, x ):
	"Set the point in the extended line segment."
	if x > min( lineSegmentEnd.point.real, pointOriginal.real ) and x < max( lineSegmentEnd.point.real, pointOriginal.real ):
		lineSegmentEnd.point = complex( x, pointOriginal.imag)

def writeOutput( fileName = '' ):
	"Raft a gcode linear move file."
	fileName = interpret.getFirstTranslatorFileNameUnmodified( fileName )
	if fileName == '':
		return
	consecution.writeChainTextWithNounMessage( fileName, 'raft' )


class RaftRepository:
	"A class to handle the raft preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		preferences.addListsToCraftTypeRepository( 'skeinforge_tools.craft_plugins.raft.html', self )
		self.fileNameInput = preferences.FileNameInput().getFromFileName( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File to be Rafted', self, '' )
		self.activateRaft = preferences.BooleanPreference().getFromValue( 'Activate Raft', self, True )
		self.addRaftElevateNozzleOrbitSetAltitude = preferences.BooleanPreference().getFromValue( 'Add Raft, Elevate Nozzle, Orbit and Set Altitude:', self, True )
		self.baseInfillDensity = preferences.FloatSpin().getFromValue( 0.3, 'Base Infill Density (ratio):', self, 0.9, 0.5 )
		self.baseLayerThicknessOverLayerThickness = preferences.FloatSpin().getFromValue( 1.0, 'Base Layer Thickness over Layer Thickness:', self, 3.0, 2.0 )
		self.baseLayers = preferences.IntSpin().getFromValue( 0, 'Base Layers (integer):', self, 3, 1 )
		self.baseNozzleLiftOverBaseLayerThickness = preferences.FloatSpin().getFromValue( 0.2, 'Base Nozzle Lift over Base Layer Thickness (ratio):', self, 0.8, 0.4 )
		self.bottomAltitude = preferences.FloatSpin().getFromValue( 0.0, 'Bottom Altitude:', self, 10.0, 0.0 )
		self.infillOverhang = preferences.FloatSpin().getFromValue( 0.0, 'Infill Overhang (ratio):', self, 0.5, 0.1 )
		self.interfaceInfillDensity = preferences.FloatSpin().getFromValue( 0.3, 'Interface Infill Density (ratio):', self, 0.9, 0.5 )
		self.interfaceLayerThicknessOverLayerThickness = preferences.FloatSpin().getFromValue( 1.0, 'Interface Layer Thickness over Layer Thickness:', self, 3.0, 1.0 )
		self.interfaceLayers = preferences.IntSpin().getFromValue( 0, 'Interface Layers (integer):', self, 3, 2 )
		self.interfaceNozzleLiftOverInterfaceLayerThickness = preferences.FloatSpin().getFromValue( 0.25, 'Interface Nozzle Lift over Interface Layer Thickness (ratio):', self, 0.85, 0.45 )
		self.operatingNozzleLiftOverLayerThickness = preferences.FloatSpin().getFromValue( 0.3, 'Operating Nozzle Lift over Layer Thickness (ratio):', self, 0.7, 0.5 )
		self.raftAdditionalMarginOverLengthPercent = preferences.FloatSpin().getFromValue( 0.5, 'Raft Additional Margin over Length (%):', self, 1.5, 1.0 )
		self.raftMargin = preferences.FloatSpin().getFromValue( 1.0, 'Raft Margin (mm):', self, 5.0, 3.0 )
		self.supportCrossHatch = preferences.BooleanPreference().getFromValue( 'Support Cross Hatch', self, False )
		self.supportFlowRateOverOperatingFlowRate = preferences.FloatSpin().getFromValue( 0.7, 'Support Flow Rate over Operating Flow Rate (ratio):', self, 1.1, 1.0 )
		self.supportGapOverPerimeterExtrusionWidth = preferences.FloatSpin().getFromValue( 0.5, 'Support Gap over Perimeter Extrusion Width (ratio):', self, 1.5, 1.0 )
		self.supportMaterialChoice = preferences.MenuButtonDisplay().getFromName( 'Support Material Choice: ', self )
		self.supportChoiceNoSupportMaterial = preferences.MenuRadio().getFromMenuButtonDisplay( self.supportMaterialChoice, 'No Support', self, True )
		self.supportChoiceSupportMateriaEverywhere = preferences.MenuRadio().getFromMenuButtonDisplay( self.supportMaterialChoice, 'Support Everywhere', self, False )
		self.supportChoiceSupportMaterialOnExteriorOnly = preferences.MenuRadio().getFromMenuButtonDisplay( self.supportMaterialChoice, 'Support on Exterior Only', self, False )
		self.supportMinimumAngle = preferences.FloatSpin().getFromValue( 40.0, 'Support Minimum Angle (degrees):', self, 80.0, 60.0 )
		self.temperatureChangeBeforeTimeRaft = preferences.FloatSpin().getFromValue( 0.0, 'Temperature Change Time Before Raft (seconds):', self, 180.0, 150.0 )
		self.temperatureChangeTimeBeforeFirstLayerOutline = preferences.FloatSpin().getFromValue( 0.0, 'Temperature Change Time Before First Layer Outline (seconds):', self, 60.0, 30.0 )
		self.temperatureChangeTimeBeforeNextThreads = preferences.FloatSpin().getFromValue( 0.0, 'Temperature Change Time Before Next Threads (seconds):', self, 60.0, 30.0 )
		self.temperatureChangeTimeBeforeSupportLayers = preferences.FloatSpin().getFromValue( 0.0, 'Temperature Change Time Before Support Layers (seconds):', self, 60.0, 30.0 )
		self.temperatureChangeTimeBeforeSupportedLayers = preferences.FloatSpin().getFromValue( 0.0, 'Temperature Change Time Before Supported Layers (seconds):', self, 60.0, 30.0 )
		self.temperatureRaft = preferences.FloatSpin().getFromValue( 140.0, 'Temperature of Raft (Celcius):', self, 260.0, 200.0 )
		self.temperatureShapeFirstLayerOutline = preferences.FloatSpin().getFromValue( 140.0, 'Temperature of Shape First Layer Outline (Celcius):', self, 260.0, 220.0 )
		self.temperatureShapeFirstLayerWithin = preferences.FloatSpin().getFromValue( 140.0, 'Temperature of Shape First Layer Within (Celcius):', self, 260.0, 195.0 )
		self.temperatureShapeNextLayers = preferences.FloatSpin().getFromValue( 140.0, 'Temperature of Shape Next Layers (Celcius):', self, 260.0, 230.0 )
		self.temperatureShapeSupportLayers = preferences.FloatSpin().getFromValue( 140.0, 'Temperature of Support Layers (Celcius):', self, 260.0, 200.0 )
		self.temperatureShapeSupportedLayers = preferences.FloatSpin().getFromValue( 140.0, 'Temperature of Supported Layers (Celcius):', self, 260.0, 230.0 )
		self.executeTitle = 'Raft'

	def execute( self ):
		"Raft button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )



class RaftSkein:
	"A class to raft a skein of extrusions."
	def __init__( self ):
		self.addLineLayerStart = True
		self.boundaryLayers = []
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.extrusionStart = True
		self.extrusionTop = 0.0
		self.feedRateMinute = 961.0
		self.interfaceStepsUntilEnd = []
		self.isFirstLayerWithinTemperatureAdded = False
		self.isStartupEarly = False
		self.isSurroundingLoop = True
		self.layerIndex = - 1
		self.layerStarted = False
		self.layerThickness = 0.4
		self.lineIndex = 0
		self.lines = None
		self.oldFlowRateString = None
		self.oldLocation = None
		self.operatingFlowRateString = None
		self.operatingLayerEndLine = '(<operatingLayerEnd> </operatingLayerEnd>)'
		self.operatingJump = None
		self.orbitalFeedRatePerSecond = 2.01
		self.perimeterWidth = 0.6
		self.supportFlowRateString = None
		self.supportLayers = []
		self.travelFeedRatePerMinute = None

	def addBaseLayer( self, baseExtrusionWidth, baseStep, stepBegin, stepEnd ):
		"Add a base layer."
		baseLayerThickness = self.layerThickness * self.baseLayerThicknessOverLayerThickness
		halfBaseExtrusionWidth = 0.5 * baseExtrusionWidth
		stepsUntilEnd = self.getStepsUntilEnd( stepBegin.real + halfBaseExtrusionWidth, stepEnd.real, baseStep )
		baseOverhang = self.raftRepository.infillOverhang.value * halfBaseExtrusionWidth - halfBaseExtrusionWidth
		beginY = stepBegin.imag - baseOverhang
		endY = stepEnd.imag + baseOverhang
		segments = []
		zCenter = self.extrusionTop + 0.5 * baseLayerThickness
		z = zCenter + baseLayerThickness * self.raftRepository.baseNozzleLiftOverBaseLayerThickness.value
		for x in stepsUntilEnd:
			begin = complex( x, beginY )
			end = complex( x, endY )
			segments.append( euclidean.getSegmentFromPoints( begin, end ) )
		if len( segments ) < 1:
			print( 'This should never happen, the base layer has a size of zero.' )
			return
		self.addLayerFromSegments( baseLayerThickness, self.baseLayerThicknessOverLayerThickness, segments, z )

	def addFlowRateLineIfNecessary( self, flowRateString ):
		"Add a line of flow rate if different."
		if flowRateString == self.oldFlowRateString:
			return
		if flowRateString != None:
			self.distanceFeedRate.addLine( 'M108 S' + flowRateString )
		self.oldFlowRateString = flowRateString

	def addInterfaceLayer( self ):
		"Add an interface layer."
		interfaceLayerThickness = self.layerThickness * self.interfaceLayerThicknessOverLayerThickness
		segments = []
		zCenter = self.extrusionTop + 0.5 * interfaceLayerThickness
		z = zCenter + interfaceLayerThickness * self.raftRepository.interfaceNozzleLiftOverInterfaceLayerThickness.value
		for y in self.interfaceStepsUntilEnd:
			begin = complex( self.interfaceBeginX, y )
			end = complex( self.interfaceEndX, y )
			segments.append( euclidean.getSegmentFromPoints( begin, end ) )
		if len( segments ) < 1:
			print( 'This should never happen, the interface layer has a size of zero.' )
			return
		self.addLayerFromSegments( interfaceLayerThickness, self.interfaceLayerThicknessOverLayerThickness, segments, z )

	def addLayerFromSegments( self, layerLayerThickness, layerThicknessRatio, segments, z ):
		"Add a layer from segments and raise the extrusion top."
		layerThicknessRatioSquared = layerThicknessRatio * layerThicknessRatio
		feedRateMinute = self.feedRateMinute / layerThicknessRatioSquared
		firstSegment = segments[ 0 ]
		nearestPoint = firstSegment[ 1 ].point
		path = [ firstSegment[ 0 ].point, nearestPoint ]
		for segment in segments[ 1 : ]:
			segmentBegin = segment[ 0 ]
			segmentEnd = segment[ 1 ]
			nextEndpoint = segmentBegin
			if abs( nearestPoint - segmentBegin.point ) > abs( nearestPoint - segmentEnd.point ):
				nextEndpoint = segmentEnd
			path.append( nextEndpoint.point )
			nextEndpoint = nextEndpoint.otherEndpoint
			nearestPoint = nextEndpoint.point
			path.append( nearestPoint )
		self.addLayerLine( z )
		if layerThicknessRatioSquared != 1.0:
			self.distanceFeedRate.addExtrusionDistanceRatioLine( 1.0 * layerThicknessRatioSquared )
		self.distanceFeedRate.addGcodeFromFeedRateThreadZ( feedRateMinute, path, z )
		self.extrusionTop += layerLayerThickness

	def addLayerLine( self, z ):
		"Add the layer gcode line and close the last layer gcode block."
		if self.layerStarted:
			self.distanceFeedRate.addLine( '(</layer>)' )
		self.distanceFeedRate.addLine( '(<layer> ' + self.distanceFeedRate.getRounded( z ) + ' )' ) # Indicate that a new layer is starting.
		self.layerStarted = True

	def addOperatingOrbits( self, boundaryLoops, pointComplex, temperatureChangeTime, z ):
		"Add the orbits before the operating layers."
		if len( boundaryLoops ) < 1:
			return
		insetBoundaryLoops = intercircle.getInsetLoopsFromLoops( self.perimeterWidth, boundaryLoops )
		if len( insetBoundaryLoops ) < 1:
			insetBoundaryLoops = boundaryLoops
		largestLoop = euclidean.getLargestLoop( insetBoundaryLoops )
		if pointComplex != None:
			largestLoop = euclidean.getLoopStartingNearest( self.perimeterWidth, pointComplex, largestLoop )
		intercircle.addOrbitsIfLarge( self.distanceFeedRate, largestLoop, self.orbitalFeedRatePerSecond, temperatureChangeTime, z )

	def addRaft( self ):
		"Add the raft."
		self.extrusionTop = self.raftRepository.bottomAltitude.value
		self.baseLayerThicknessOverLayerThickness = self.raftRepository.baseLayerThicknessOverLayerThickness.value
		baseExtrusionWidth = self.perimeterWidth * self.baseLayerThicknessOverLayerThickness
		baseStep = baseExtrusionWidth / self.raftRepository.baseInfillDensity.value
		self.interfaceLayerThicknessOverLayerThickness = self.raftRepository.interfaceLayerThicknessOverLayerThickness.value
		interfaceExtrusionWidth = self.perimeterWidth * self.interfaceLayerThicknessOverLayerThickness
		self.interfaceStep = interfaceExtrusionWidth / self.raftRepository.interfaceInfillDensity.value
		self.setCornersZ()
		self.cornerLowComplex = self.cornerLow.dropAxis( 2 )
		originalExtent = self.cornerHighComplex - self.cornerLowComplex
		self.raftOutsetRadius = self.raftRepository.raftMargin.value + self.raftRepository.raftAdditionalMarginOverLengthPercent.value * 0.01 * max( originalExtent.real, originalExtent.imag )
		complexRadius = complex( self.raftOutsetRadius, self.raftOutsetRadius )
		self.complexHigh = complexRadius + self.cornerHighComplex
		self.complexLow = self.cornerLowComplex - complexRadius
		extent = self.complexHigh - self.complexLow
		extentStepX = interfaceExtrusionWidth + 2.0 * self.interfaceStep * math.ceil( 0.5 * ( extent.real - self.interfaceStep ) / self.interfaceStep )
		extentStepY = baseExtrusionWidth + 2.0 * baseStep * math.ceil( 0.5 * ( extent.imag - baseStep ) / baseStep )
		center = 0.5 * ( self.complexHigh + self.complexLow )
		extentStep = complex( extentStepX, extentStepY )
		stepBegin = center - 0.5 * extentStep
		stepEnd = stepBegin + extentStep
		zBegin = self.extrusionTop + self.layerThickness
		beginLoop = euclidean.getSquareLoop( self.cornerLowComplex, self.cornerHighComplex )
		extrudeRaft = self.raftRepository.baseLayers.value > 0 or self.raftRepository.interfaceLayers.value > 0
		if extrudeRaft:
			self.addTemperature( self.raftRepository.temperatureRaft.value )
		else:
			self.addTemperature( self.raftRepository.temperatureShapeFirstLayerOutline.value )
		if intercircle.orbitsAreLarge( beginLoop, self.raftRepository.temperatureChangeBeforeTimeRaft.value ):
			self.addLayerLine( zBegin )
			intercircle.addOrbitsIfLarge( self.distanceFeedRate, beginLoop, self.orbitalFeedRatePerSecond, self.raftRepository.temperatureChangeBeforeTimeRaft.value, zBegin )
		for baseLayerIndex in xrange( self.raftRepository.baseLayers.value ):
			self.addBaseLayer( baseExtrusionWidth, baseStep, stepBegin, stepEnd )
		self.setInterfaceVariables( interfaceExtrusionWidth, stepBegin, stepEnd )
		for interfaceLayerIndex in xrange( self.raftRepository.interfaceLayers.value ):
			self.addInterfaceLayer()
		self.operatingJump = self.extrusionTop - self.cornerLow.z + 0.5 * self.layerThickness + self.layerThickness * self.raftRepository.operatingNozzleLiftOverLayerThickness.value
		self.setBoundaryLayers()
		if extrudeRaft and len( self.boundaryLayers ) > 0:
			boundaryZ = self.boundaryLayers[ 0 ].z
			self.addLayerLine( boundaryZ )
			self.addTemperature( self.raftRepository.temperatureShapeFirstLayerOutline.value )
			squareLoop = euclidean.getSquareLoop( stepBegin, stepEnd )
			intercircle.addOrbitsIfLarge( self.distanceFeedRate, squareLoop, self.orbitalFeedRatePerSecond, self.raftRepository.temperatureChangeTimeBeforeFirstLayerOutline.value, boundaryZ )
			self.addLineLayerStart = False

	def addSupportSegmentTable( self, layerIndex ):
		"Add support segments from the boundary layers."
		aboveLayer = self.boundaryLayers[ layerIndex + 1 ]
		aboveLoops = aboveLayer.loops
		supportLayer = self.supportLayers[ layerIndex ]
		if len( aboveLoops ) < 1:
			supportLayer.xIntersectionsTable = {}
			return
		horizontalSegmentTable = {}
		boundaryLayer = self.boundaryLayers[ layerIndex ]
		rise = aboveLayer.z - boundaryLayer.z
		outsetSupportLayer = intercircle.getInsetSeparateLoopsFromLoops( - self.minimumSupportRatio * rise, boundaryLayer.loops )
		numberOfSubSteps = 4
		subStepSize = numberOfSubSteps + self.interfaceStep / float( numberOfSubSteps )
		untilEdgeSubSteps = int( self.supportOutset / subStepSize )
		for y in self.interfaceStepsUntilEnd:
			xTotalIntersectionIndexList = []
			for subStepIndex in xrange( - untilEdgeSubSteps, untilEdgeSubSteps + 1 ):
				ySubStep = y + subStepIndex * subStepSize
				xIntersectionIndexList = []
				euclidean.addXIntersectionIndexesFromLoopsY( aboveLoops, - 1, xIntersectionIndexList, ySubStep )
				euclidean.addXIntersectionIndexesFromLoopsY( outsetSupportLayer, 0, xIntersectionIndexList, ySubStep )
				xIntersections = euclidean.getXIntersectionsFromIntersections( xIntersectionIndexList )
				for xIntersection in xIntersections:
					xTotalIntersectionIndexList.append( euclidean.XIntersectionIndex( subStepIndex + untilEdgeSubSteps, xIntersection ) )
			xTotalIntersections = euclidean.getJoinOfXIntersectionIndexes( xTotalIntersectionIndexList )
			if len( xTotalIntersections ) > 0:
				supportLayer.xIntersectionsTable[ int( y / self.interfaceStep ) ] = xTotalIntersections

	def addSupportLayerTemperature( self, endpoints, z ):
		"Add support layer and temperature before the object layer."
		self.distanceFeedRate.addLinesSetAbsoluteDistanceMode( self.supportStartLines )
		self.addTemperatureOrbits( endpoints, self.raftRepository.temperatureShapeSupportLayers, self.raftRepository.temperatureChangeTimeBeforeSupportLayers, z )
		aroundPixelTable = {}
		layerFillInset = 0.9 * self.perimeterWidth
		aroundWidth = 0.12 * layerFillInset
		boundaryLoops = self.boundaryLayers[ self.layerIndex ].loops
		halfSupportOutset = 0.5 * self.supportOutset
		aroundBoundaryLoops = intercircle.getAroundsFromLoops( boundaryLoops, halfSupportOutset )
		for aroundBoundaryLoop in aroundBoundaryLoops:
			euclidean.addLoopToPixelTable( aroundBoundaryLoop, aroundPixelTable, aroundWidth )
		paths = euclidean.getPathsFromEndpoints( endpoints, layerFillInset, aroundPixelTable, aroundWidth )
		self.addFlowRateLineIfNecessary( self.supportFlowRateString )
		for path in paths:
			self.distanceFeedRate.addGcodeFromFeedRateThreadZ( self.feedRateMinute, path, z )
		self.addFlowRateLineIfNecessary( self.operatingFlowRateString )
		self.addTemperatureOrbits( endpoints, self.raftRepository.temperatureShapeSupportedLayers, self.raftRepository.temperatureChangeTimeBeforeSupportedLayers, z )
		self.distanceFeedRate.addLinesSetAbsoluteDistanceMode( self.supportEndLines )

	def addTemperature( self, temperature ):
		"Add a line of temperature."
		self.distanceFeedRate.addLine( 'M104 S' + euclidean.getRoundedToThreePlaces( temperature ) ) # Set temperature.

	def addTemperatureOrbits( self, endpoints, temperaturePreference, temperatureTimeChangePreference, z ):
		"Add the temperature and orbits around the support layer."
		if self.layerIndex < 0:
			return
		boundaryLoops = self.boundaryLayers[ self.layerIndex ].loops
		self.addTemperature( temperaturePreference.value )
		if len( boundaryLoops ) < 1:
			layerCornerHigh = complex( - 999999999.0, - 999999999.0 )
			layerCornerLow = complex( 999999999.0, 999999999.0 )
			for endpoint in endpoints:
				layerCornerHigh = euclidean.getMaximum( layerCornerHigh, endpoint.point )
				layerCornerLow = euclidean.getMinimum( layerCornerLow, endpoint.point )
			squareLoop = euclidean.getSquareLoop( layerCornerLow, layerCornerHigh )
			intercircle.addOrbitsIfLarge( self.distanceFeedRate, squareLoop, self.orbitalFeedRatePerSecond, temperatureTimeChangePreference.value, z )
			return
		perimeterInset = 0.4 * self.perimeterWidth
		insetBoundaryLoops = intercircle.getInsetLoopsFromLoops( perimeterInset, boundaryLoops )
		if len( insetBoundaryLoops ) < 1:
			insetBoundaryLoops = boundaryLoops
		largestLoop = euclidean.getLargestLoop( insetBoundaryLoops )
		intercircle.addOrbitsIfLarge( self.distanceFeedRate, largestLoop, self.orbitalFeedRatePerSecond, temperatureTimeChangePreference.value, z )

	def addToFillXIntersectionIndexTables( self, supportLayer ):
		"Add fill segments from the boundary layers."
		supportLoops = supportLayer.supportLoops
		supportLayer.fillXIntersectionIndexTable = {}
		if len( supportLoops ) < 1 or len( self.interfaceStepsUntilEnd ) < 1:
			return
		euclidean.addXIntersectionsFromLoopsForTable( supportLoops, supportLayer.fillXIntersectionIndexTable, self.interfaceStep )

	def extendXIntersections( self, loops, radius, xIntersectionsTable ):
		"Extend the support segments."
		xIntersectionsTableKeys = xIntersectionsTable.keys()
		for xIntersectionsTableKey in xIntersectionsTableKeys:
			lineSegments = euclidean.getSegmentsFromXIntersections( xIntersectionsTable[ xIntersectionsTableKey ], xIntersectionsTableKey )
			xIntersectionIndexList = []
			loopXIntersections = []
			euclidean.addXIntersectionsFromLoops( loops, loopXIntersections, xIntersectionsTableKey )
			for lineSegmentIndex in xrange( len( lineSegments ) ):
				lineSegment = lineSegments[ lineSegmentIndex ]
				extendedLineSegment = getExtendedLineSegment( radius, lineSegment, loopXIntersections )
				if extendedLineSegment != None:
					euclidean.addXIntersectionIndexesFromSegment( lineSegmentIndex, extendedLineSegment, xIntersectionIndexList )
			xIntersections = euclidean.getJoinOfXIntersectionIndexes( xIntersectionIndexList )
			for xIntersectionIndex in xrange( len( xIntersections ) ):
				xIntersection = xIntersections[ xIntersectionIndex ]
				xIntersection = max( xIntersection, self.interfaceBeginX )
				xIntersection = min( xIntersection, self.interfaceEndX )
				xIntersections[ xIntersectionIndex ] = xIntersection
			if len( xIntersections ) > 0:
				xIntersectionsTable[ xIntersectionsTableKey ] = xIntersections
			else:
				del xIntersectionsTable[ xIntersectionsTableKey ]

	def getCraftedGcode( self, gcodeText, raftRepository ):
		"Parse gcode text and store the raft gcode."
		self.raftRepository = raftRepository
		self.supportEndText = preferences.getFileInAlterationsOrGivenDirectory( os.path.dirname( __file__ ), 'Support_End.gcode' )
		self.supportEndLines = gcodec.getTextLines( self.supportEndText )
		self.supportStartText = preferences.getFileInAlterationsOrGivenDirectory( os.path.dirname( __file__ ), 'Support_Start.gcode' )
		self.supportStartLines = gcodec.getTextLines( self.supportStartText )
		self.minimumSupportRatio = math.tan( math.radians( raftRepository.supportMinimumAngle.value ) )
		self.lines = gcodec.getTextLines( gcodeText )
		self.parseInitialization()
		if raftRepository.addRaftElevateNozzleOrbitSetAltitude.value:
			self.addRaft()
		self.addTemperature( raftRepository.temperatureShapeFirstLayerOutline.value )
		for line in self.lines[ self.lineIndex : ]:
			self.parseLine( line )
		return self.distanceFeedRate.output.getvalue()

	def getElevatedBoundaryLine( self, splitLine ):
		"Get elevated boundary gcode line."
		location = gcodec.getLocationFromSplitLine( None, splitLine )
		if self.operatingJump != None:
			location.z += self.operatingJump
		return self.distanceFeedRate.getBoundaryLine( location )

	def getRaftedLine( self, splitLine ):
		"Get elevated gcode line with operating feed rate."
		location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
		self.feedRateMinute = gcodec.getFeedRateMinute( self.feedRateMinute, splitLine )
		self.oldLocation = location
		z = location.z
		if self.operatingJump != None:
			z += self.operatingJump
		if not self.isFirstLayerWithinTemperatureAdded and not self.isSurroundingLoop:
			self.isFirstLayerWithinTemperatureAdded = True
			self.addTemperature( self.raftRepository.temperatureShapeFirstLayerWithin.value )
			if self.raftRepository.addRaftElevateNozzleOrbitSetAltitude.value:
				boundaryLoops = self.boundaryLayers[ self.layerIndex ].loops
				if len( boundaryLoops ) > 1:
					self.addOperatingOrbits( boundaryLoops, euclidean.getXYComplexFromVector3( self.oldLocation ), self.raftRepository.temperatureChangeTimeBeforeNextThreads.value, z )
		return self.distanceFeedRate.getLinearGcodeMovementWithFeedRate( self.feedRateMinute, location.dropAxis( 2 ), z )

	def getStepsUntilEnd( self, begin, end, stepSize ):
		"Get steps from the beginning until the end."
		step = begin
		steps = []
		while step < end:
			steps.append( step )
			step += stepSize
		return steps

	def getSupportEndpoints( self ):
		"Get the support layer segments."
		if len( self.supportLayers ) <= self.layerIndex:
			return []
		supportSegmentTable = self.supportLayers[ self.layerIndex ].supportSegmentTable
		endpoints = euclidean.getEndpointsFromSegmentTable( supportSegmentTable )
		if self.layerIndex % 2 == 0 or not self.raftRepository.supportCrossHatch.value:
			return endpoints
		crossEndpoints = []
		crossHatchPointLineTable = {}
		for endpoint in endpoints:
			self.interfaceStep
			segmentBeginXStep = int( math.ceil( min( endpoint.point.real, endpoint.otherEndpoint.point.real ) / self.interfaceStep ) )
			segmentEndXStep = int( math.ceil( max( endpoint.point.real, endpoint.otherEndpoint.point.real ) / self.interfaceStep ) )
			for step in xrange( segmentBeginXStep, segmentEndXStep ):
				x = self.interfaceStep * step
				crossHatchPointLine = getCrossHatchPointLine( crossHatchPointLineTable, x )
				crossHatchPointLine[ int( round( endpoint.point.imag / self.interfaceStep ) ) ] = True
		crossHatchPointLineTableKeys = crossHatchPointLineTable.keys()
		crossHatchPointLineTableKeys.sort()
		for crossHatchPointLineTableKey in crossHatchPointLineTableKeys:
			crossHatchPointLine = crossHatchPointLineTable[ crossHatchPointLineTableKey ]
			crossHatchPointLineKeys = crossHatchPointLine.keys()
			for crossHatchPointLineKey in crossHatchPointLineKeys:
				if not crossHatchPointLine.has_key( crossHatchPointLineKey - 1 ) and not crossHatchPointLine.has_key( crossHatchPointLineKey + 1 ):
					del crossHatchPointLine[ crossHatchPointLineKey ]
			crossHatchPointLineKeys = crossHatchPointLine.keys()
			crossHatchPointLineKeys.sort()
			yIntersections = []
			for crossHatchPointLineKey in crossHatchPointLineKeys:
				if crossHatchPointLine.has_key( crossHatchPointLineKey - 1 ) != crossHatchPointLine.has_key( crossHatchPointLineKey + 1 ):
					yIntersection = self.interfaceStep * crossHatchPointLineKey
					yIntersections.append( yIntersection )
			crossEndpoints += getEndpointsFromYIntersections( crossHatchPointLineTableKey, yIntersections )
		return crossEndpoints

	def parseInitialization( self ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == 'M108':
				self.setOperatingFlowString( splitLine )
			elif firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine( '(<procedureDone> raft </procedureDone>)' )
			elif firstWord == '(<layer>':
				return
			elif firstWord == '(<layerThickness>':
				self.layerThickness = float( splitLine[ 1 ] )
			elif firstWord == '(<orbitalFeedRatePerSecond>':
				self.orbitalFeedRatePerSecond = float( splitLine[ 1 ] )
			elif firstWord == '(<operatingFeedRatePerSecond>':
				self.feedRateMinute = 60.0 * float( splitLine[ 1 ] )
			elif firstWord == '(<perimeterWidth>':
				self.perimeterWidth = float( splitLine[ 1 ] )
				self.supportOutset = self.perimeterWidth + self.perimeterWidth * self.raftRepository.supportGapOverPerimeterExtrusionWidth.value
			elif firstWord == '(<travelFeedRatePerSecond>':
				self.travelFeedRatePerMinute = 60.0 * float( splitLine[ 1 ] )
			self.distanceFeedRate.addLine( line )

	def parseLine( self, line ):
		"Parse a gcode line and add it to the raft skein."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		if firstWord == 'G1':
			if self.extrusionStart:
				line = self.getRaftedLine( splitLine )
		elif firstWord == 'M101':
			if self.isStartupEarly:
				self.isStartupEarly = False
				return
		elif firstWord == 'M108':
			self.setOperatingFlowString( splitLine )
		elif firstWord == '(<boundaryPoint>':
			line = self.getElevatedBoundaryLine( splitLine )
		elif firstWord == '(</extrusion>)':
			self.extrusionStart = False
			self.distanceFeedRate.addLine( self.operatingLayerEndLine )
		elif firstWord == '(<layer>':
			self.layerIndex += 1
			boundaryLayer = None
			layerHeight = self.extrusionTop + float( splitLine[ 1 ] )
			if len( self.boundaryLayers ) > 0:
				boundaryLayer = self.boundaryLayers[ self.layerIndex ]
				layerHeight = boundaryLayer.z
			if self.operatingJump != None:
				line = '(<layer> ' + self.distanceFeedRate.getRounded( layerHeight ) + ' )'
			if self.layerStarted and self.addLineLayerStart:
				self.distanceFeedRate.addLine( '(</layer>)' )
			self.layerStarted = False
			if self.layerIndex > len( self.supportLayers ) + 1:
				self.distanceFeedRate.addLine( self.operatingLayerEndLine )
				self.operatingLayerEndLine = ''
			if self.addLineLayerStart:
				self.distanceFeedRate.addLine( line )
			self.addLineLayerStart = True
			line = ''
			endpoints = self.getSupportEndpoints()
			if self.layerIndex == 1:
				if len( endpoints ) < 1:
					self.addTemperature( self.raftRepository.temperatureShapeNextLayers.value )
					if self.raftRepository.addRaftElevateNozzleOrbitSetAltitude.value:
						boundaryLoops = boundaryLayer.loops
						if len( boundaryLoops ) > 0:
							temperatureChangeTimeBeforeNextThreads = self.raftRepository.temperatureChangeTimeBeforeNextThreads.value
							self.addOperatingOrbits( boundaryLoops, euclidean.getXYComplexFromVector3( self.oldLocation ), temperatureChangeTimeBeforeNextThreads, layerHeight )
			if len( endpoints ) > 0:
				self.addSupportLayerTemperature( endpoints, layerHeight )
		self.distanceFeedRate.addLine( line )

	def setBoundaryLayers( self ):
		"Set the boundary layers."
		boundaryLoop = None
		boundaryLayer = None
		for line in self.lines[ self.lineIndex : ]:
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			if firstWord == '(</boundaryPerimeter>)':
				boundaryLoop = None
			elif firstWord == '(<boundaryPoint>':
				location = gcodec.getLocationFromSplitLine( None, splitLine )
				if boundaryLoop == None:
					boundaryLoop = []
					boundaryLayer.loops.append( boundaryLoop )
				boundaryLoop.append( location.dropAxis( 2 ) )
			elif firstWord == '(<layer>':
				z = float( splitLine[ 1 ] )
				if self.operatingJump != None:
					z += self.operatingJump
				boundaryLayer = euclidean.LoopLayer( z )
				self.boundaryLayers.append( boundaryLayer )
		if self.raftRepository.supportChoiceNoSupportMaterial.value:
			return
		if len( self.interfaceStepsUntilEnd ) < 1:
			return
		if len( self.boundaryLayers ) < 2:
			return
		for boundaryLayer in self.boundaryLayers:
			supportLoops = intercircle.getInsetSeparateLoopsFromLoops( - self.supportOutset, boundaryLayer.loops )
			supportLayer = SupportLayer( supportLoops )
			self.supportLayers.append( supportLayer )
		for supportLayerIndex in xrange( len( self.supportLayers ) - 1 ):
			self.addSupportSegmentTable( supportLayerIndex )
		self.truncateSupportSegmentTables()
		for supportLayerIndex in xrange( len( self.supportLayers ) - 1 ):
			self.extendXIntersections( self.boundaryLayers[ supportLayerIndex ].loops, self.supportOutset, self.supportLayers[ supportLayerIndex ].xIntersectionsTable )
		for supportLayer in self.supportLayers:
			self.addToFillXIntersectionIndexTables( supportLayer )
		if self.raftRepository.supportChoiceSupportMaterialOnExteriorOnly.value:
			for supportLayerIndex in xrange( 1, len( self.supportLayers ) ):
				self.subtractJoinedFill( supportLayerIndex )
		for supportLayerIndex in xrange( len( self.supportLayers ) - 2, - 1, - 1 ):
			xIntersectionsTable = self.supportLayers[ supportLayerIndex ].xIntersectionsTable
			aboveXIntersectionsTable = self.supportLayers[ supportLayerIndex + 1 ].xIntersectionsTable
			euclidean.joinXIntersectionsTables( aboveXIntersectionsTable, xIntersectionsTable )
		for supportLayerIndex in xrange( len( self.supportLayers ) ):
			supportLayer = self.supportLayers[ supportLayerIndex ]
			self.extendXIntersections( supportLayer.supportLoops, self.raftOutsetRadius, supportLayer.xIntersectionsTable )
		for supportLayer in self.supportLayers:
			euclidean.subtractXIntersectionsTable( supportLayer.xIntersectionsTable, supportLayer.fillXIntersectionIndexTable )
		for supportLayer in self.supportLayers:
			supportLayer.supportSegmentTable = {}
			xIntersectionsTable = supportLayer.xIntersectionsTable
			for xIntersectionsTableKey in xIntersectionsTable:
				y = xIntersectionsTableKey * self.interfaceStep
				supportLayer.supportSegmentTable[ xIntersectionsTableKey ] = euclidean.getSegmentsFromXIntersections( xIntersectionsTable[ xIntersectionsTableKey ], y )

	def setCornersZ( self ):
		"Set maximum and minimum corners and z."
		layerIndex = - 1
		self.cornerHighComplex = complex( - 999999999.0, - 999999999.0 )
		self.cornerLow = Vector3( 999999999.0, 999999999.0, 999999999.0 )
		for line in self.lines[ self.lineIndex : ]:
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon( line )
			firstWord = gcodec.getFirstWord( splitLine )
			if firstWord == 'G1':
				location = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
				self.cornerHighComplex = euclidean.getMaximum( self.cornerHighComplex, location.dropAxis( 2 ) )
				self.cornerLow = euclidean.getPointMinimum( self.cornerLow, location )
				self.oldLocation = location
			elif firstWord == '(<layer>':
				layerIndex += 1
				if self.raftRepository.supportChoiceNoSupportMaterial.value:
					if layerIndex > 1:
						return

	def setInterfaceVariables( self, interfaceExtrusionWidth, stepBegin, stepEnd ):
		"Set the interface variables."
		halfInterfaceExtrusionWidth = 0.5 * interfaceExtrusionWidth
		self.interfaceStepsUntilEnd = self.getStepsUntilEnd( stepBegin.imag + halfInterfaceExtrusionWidth, stepEnd.imag, self.interfaceStep )
		self.interfaceOverhang = self.raftRepository.infillOverhang.value * halfInterfaceExtrusionWidth - halfInterfaceExtrusionWidth
		self.interfaceBeginX = stepBegin.real - self.interfaceOverhang
		self.interfaceEndX = stepEnd.real + self.interfaceOverhang

	def setOperatingFlowString( self, splitLine ):
		"Set the operating flow string from the split line."
		self.operatingFlowRateString = splitLine[ 1 ][ 1 : ]
		self.supportFlowRateString = self.distanceFeedRate.getRounded( float( self.operatingFlowRateString ) * self.raftRepository.supportFlowRateOverOperatingFlowRate.value )

	def subtractJoinedFill( self, supportLayerIndex ):
		"Join the fill then subtract it from the support layer table."
		supportLayer = self.supportLayers[ supportLayerIndex ]
		fillXIntersectionIndexTable = supportLayer.fillXIntersectionIndexTable
		belowFillXIntersectionIndexTable = self.supportLayers[ supportLayerIndex - 1 ].fillXIntersectionIndexTable
		euclidean.joinXIntersectionsTables( belowFillXIntersectionIndexTable, supportLayer.fillXIntersectionIndexTable )
		euclidean.subtractXIntersectionsTable( supportLayer.xIntersectionsTable, supportLayer.fillXIntersectionIndexTable )

	def truncateSupportSegmentTables( self ):
		"Truncate the support segments after the last support segment which contains elements."
		for supportLayerIndex in xrange( len( self.supportLayers ) - 1, - 1, - 1 ):
			if len( self.supportLayers[ supportLayerIndex ].xIntersectionsTable ) > 0:
				self.supportLayers = self.supportLayers[ : supportLayerIndex + 1 ]
				return
		self.supportLayers = []


class SupportLayer:
	"Support loops with segment tables."
	def __init__( self, supportLoops ):
		self.supportLoops = supportLoops
		self.supportSegmentTable = {}
		self.xIntersectionsTable = {}

	def __repr__( self ):
		"Get the string representation of this loop layer."
		return '%s' % ( self.supportLoops )


def main():
	"Display the raft dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		preferences.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
