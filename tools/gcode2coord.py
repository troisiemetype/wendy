#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gcode parser to coordinates file, for simple use with Wendy laser projector.
#

import os
import re
import sys
import argparse
from copy import deepcopy
from math import fabs, ceil, cos, sin, acos, atan2, degrees, pi

position = {"X": 0, "Y": 0, "Z": 0}
tmpPos = {"X": 0, "Y": 0, "Z": 0}
circleOffset = {"I": 0, "J": 0, "R": 0}
moveType = {"G": 0, "M": 5}
coords = ("X", "Y", "Z")
circle = ("I", "J", "R")
index = 0
lineIndex = 0
error = 0.5

parser = argparse.ArgumentParser(description = "reads a Gcode file and export coordinates that can be read by Wendy laser projetcor")

parser.add_argument("i", help = "input Gcode file")
parser.add_argument("-o", "--output-file", dest = "output", metavar = "", default = "output.txt", help = "output coordinates text file")
parser.add_argument("-e", "--error", dest = "error", metavar = "", default = error, help = "max error value when approximating circle with lines")

args = parser.parse_args()

inputFile = open(args.i, "r")
outputFile = open(args.output, "w")
error = args.error

param_rex = {}
g_params = ("X", "Y", "Z", "I", "J", "R")
for g_param in g_params:
	param_rex[g_param] = re.compile("(%s[\+\-]?[\d\.]+)\D?" % g_param)

gcode_rex = re.compile("([G|M][\d]+)\D?")

def outputLine(x, y, z, g):
	outputFile.write("ID %u\n" % index)
	outputFile.write("G %u\n" %g)
	outputFile.write("X %f\n" %x)
	outputFile.write("Y %f\n" %y)
	outputFile.write("Z %f\n" %z)


def computeCircle(mode, direction):

	xStart = position["X"]
	yStart = position["Y"]

	xEnd = tmpPos["X"]
	yEnd = tmpPos["Y"]


	xOffset = xEnd - xStart
	yOffset = yEnd - yStart

	offset = (xOffset ** 2 + yOffset ** 2) ** 0.5
	
	print "\nmode %s" %mode
	print "start X: %f" % xStart
	print "start Y: %f" % yStart
	print "end X: %f" % xEnd
	print "end Y: %f" % yEnd
	print "offset X: %f" % xOffset
	print "offset Y: %f" % yOffset
	print "offset: %f\n" % offset
	

	if mode == "coords":
		xCenterOffset = circleOffset["I"]
		yCenterOffset = circleOffset["J"]
		xCenter = xCenterOffset  + position["X"]
		yCenter = yCenterOffset + position["Y"]
		radius = (xCenterOffset ** 2 + yCenterOffset ** 2) ** 0.5
	elif mode == "radius":
		radius = circleOffset["R"]

		# Let's compute the center position.
		# We know that the center of the circle is on a line mirroring the two points.
		# First, get the position of the point at half distance between start and end point
		xM = xOffset / 2 + xStart
		yM = yOffset / 2 + yStart
		'''outls trigonométriques
		print"xM: %f" %xM
		print"yM: %f" %yM
		'''
		# then, we need the direction of the vector going from that point to the center
		# (the mirror line)
		xVect = yOffset
		yVect = -xOffset
		# This gives the right vector direction for a G2 arc.
		# Reverse ti for G3
		if direction == 3:
			xVect *= -1
			yVect *= -1
		'''
		print"xVect: %f" %xVect
		print"yVect: %f" %yVect
		'''
		# And we need to normalise it, so its length is equal to 1
		xVect /= offset
		yVect /= offset
		'''
		print"xVect: %f" %xVect
		print"yVect: %f\n" %yVect
		'''
		# ok, now the distance from this point to the circle center
		# it's given by Pythagore
		try:
			d = (radius ** 2 - (offset / 2) ** 2) ** 0.5
		except:
			print "line %u: error in circle definition, radius too short." %lineIndex
			return
#		print "d: %f" %d

		# and finally, this distance applied to the above vector gives us the position of the center
		xCenter = xVect * d + xM
		yCenter = yVect * d + yM
		xCenterOffset = xCenter - xStart
		yCenterOffset = yCenter - yStart
	
	print "center X: %f" %xCenter
	print "center Y: %f" %yCenter
	print "center offset X: %f" %xCenterOffset
	print "center offset Y: %f" %yCenterOffset
	print "radius: %f\n" %radius
	
	'''
	print "X offset: %f" %xOffset
	print "Y offset: %f" %yOffset
	print "offset: %f" %offset
	print "radius: %f" %radius
	'''

	# Ok, now we can compute the path. But before that, we need a start and end angle
	# because we will be computing positions from the start point, rotating around centre.
	aStart = atan2(yStart - yCenter, xStart - xCenter)
#	aStart += 2 * pi
#	aStart %= 2 * pi
	aEnd = atan2(yEnd - yCenter, xEnd - xCenter)
#	aEnd += 2 * pi
#	aEnd %= 2 * pi

	a = fabs(aEnd - aStart)

	# Wen need to know how much segments we will do for this circle
	# The error parameter gives the max distance between the arc and the straight line going from start to end.
	# If we divide the angle per 2, we can use basic trigonometry
	# given an angle, line is the sine, perimeter is the arc length, and error is the difference between radius and cosine
	# error = r * (1 - cos(a))
	# error = r - r * cos(a)
	# cos(a) = (r - error) / r
	# a = acos((r - error) / r)
	# error angle is 2 * a, and we need to ceil it so we have equal increment angles
	# finally, we compute angle delta, and divide it by error angle to obtain error increment

	aError = acos((radius - error) / radius)
	aSteps = int(ceil(a / aError))
	aIncr = a / aSteps
	if direction == 2: aIncr *= -1

	print "start angle (degrees): %f" %degrees(aStart)
	print "end angle (degrees): %f" %degrees(aEnd)
	print "start angle : %f" %aStart
	print "end angle : %f" %aEnd
	print "travel angle : %f" %a
	print "error angle : %f" %aError
	print "steps : %u" %aSteps
	print "angle increment : %f" %aIncr

	for i in range(aSteps):
		a = aStart + aIncr
		x = xCenter + radius * cos(a)
		y = yCenter + radius * sin(a)
		z = position["Z"]
		g = 1
		global index
		index += 1
		outputLine(x, y, z, g)
		aStart = a
		position["X"] = x
		position["Y"] = y
	return


for line in inputFile:

	lineIndex += 1

	line.strip()
	line.upper()

	# skip empty and comment lines
	if len(line) == 0 or line[0] == "%" or line[0] == "(":
		continue

	update = 0

	# Find move type and spindle commands
	gcode = gcode_rex.findall(line)
	for code in gcode:
		moveType[code[0]] = int(code[1:])

	for parameter in g_params:
		match = param_rex[parameter].search(line)

		if match:
			param = match.group()[0]
			value = float(match.group()[1:])
			if param in coords:
#				print "%s: %f" %(param, value)
				update = 1
				tmpPos[param] = value
			elif param in circle:
				update = 1
				circleOffset[param] = value
				if param == "R":
					circleMode = "radius"
				else:
					circleMode = "coords"

	if update == 1:
		if moveType["G"] == 0 or moveType["G"] == 1:
			index += 1
#			print "update i %u" %index
			position = deepcopy(tmpPos)
			outputLine(position["X"], position["Y"], position["Z"], moveType["G"])
#			print "pos X: %f" %position["X"]
#			print "pos Y: %f" %position["Y"]
		elif moveType["G"] == 2 or moveType["G"] == 3:
			computeCircle(circleMode, moveType["G"]);


inputFile.close()
outputFile.close()
