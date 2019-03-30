####################
# We're getting conflict with ROS.
# Move this to a package?  Then we'd always import this package
# if we're not using ROS?
import sys
if ('/opt/ros/kinetic/lib/python2.7/dist-packages' in sys.path):
	sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
# https://stackoverflow.com/questions/43019951/after-install-ros-kinetic-cannot-import-opencv
####################

import numpy as np
from gurobipy import *
from collections import defaultdict
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2


def make_dict():
	return defaultdict(make_dict)


class make_sign:
	def __init__(self):

		self.EQ = 0
		self.LE = 1
		self.GE = 2

		
class make_dvtype:
	def __init__(self):
			
		# Continuous Variables:
		self.CONT_NN	= 0		# Non-negative
		self.CONT_URS	= 1		# Unrestricted in Sign
		self.CONT_BNDED	= 2		# Bounded
		self.CONT_HARD	= 3		# Hard-coded (e.g., there's a constraint that says "x = 0")
		self.CONT_SLACK	= 4		# Slack OR Surplus variable
		
		# Integer Variables:
		self.INT_BIN	= 10	# Binary
		self.INT_GEN	= 11	# General Integer
		self.INT_BNDED	= 12	# Bounded (but not binary)
		self.INT_HARD	= 13	# Hard-coded (e.g., y = 1)
	
	
SIGN 	= make_sign()
DV 		= make_dvtype()


# We will assume that all formulations are **minimization**.
# Multiply objective function coefficients by (-1) for max problems.
# FIXME -- WHERE ARE WE MAKING USE OF THIS???
OBJ_TYPE = 'min'

HOME_DIRECTORY 	= os.environ['HOME']  	# '/home/murray'


# Grayscale (GS) Mapping:
# Map from [-1,1] to the BW range of [0, 255], such that
#	0 --> 0
#	Negatives: [-1, 0) --> [128, 191]
#	Positives: ( 0, 1] --> [192, 255]
GSneg = [128, 191]
GSpos = [192, 255]

# HSV Mapping:
# Map from [-1,1] to HSV values, such that:
# [0] --> [0, 0, 0] (black)
# [-1,0) --> Shades of red.
# 		More negative --> brighter red
# 		We'll leave H = 0 (red hue), S = 255 (max saturation).
# 		Vary V from 102 (closer to 0) to 255 (closer to -1)
# 		HSVneg = [Hue, Sat, ValLow, ValHigh]
HSVneg = [0, 255, 102, 255]
# (0, 1] --> Shades of green.
# 		More positve --> brighter green
# 		We'll leave H = 70 (green hue), S = 255 (max saturation).
# 		Vary V from 102 (closer to 0) to 255 (closer to +1)
# 		HSVpos = [Hue, Sat, ValLow, ValHigh]
HSVpos = [70, 255, 102, 255]


# https://stackoverflow.com/questions/38647230/get-constraints-in-matrix-format-from-gurobipy
def get_expr_coos(expr, var_indices):
	# Returns the coeffient and corresponding column:
	for i in range(expr.size()):
		dvar = expr.getVar(i)
		yield expr.getCoeff(i), var_indices[dvar]


def buildA(m, dvars, constrs, r, c, d, dprime, d_details):
	
	# We're going to create an A matrix for Ax = b
	# (convert each inequality constraint to an equality)
	r = np.array(r)
	
	rows = len(constrs)
	cols = len(dvars) + len(r[r > 0])	# Add columns for non-equality constraints
	
	'''
	print rows
	print cols
	print len(dvars)
	print len(r[r > 0])
	'''
	
	numConstr = rows
	numDvars = len(dvars)
	numSlacks = cols - numDvars
	
	A = np.zeros((rows, cols))
	
	# Initialize the column counter for adding slack/surplus variables
	slack_col = len(dvars) - 1

	# Create IDs for slack/surplus variables
	slackGroupID = max(d) + 1
	surplusGroupID = slackGroupID + 1

	var_indices = {v: i for i, v in enumerate(dvars)}
	for row_idx, constr in enumerate(constrs):
		for coeff, col_idx in get_expr_coos(m.getRow(constr), var_indices):
			# yield row_idx, col_idx, coeff
			A[row_idx, col_idx] = coeff

		# Add slack/surplus variables for each inequality constraint:
		if (r[row_idx] == SIGN.LE):
			# Add a "+1" in this row in a new column:
			slack_col += 1
			A[row_idx, slack_col] = 1
			
			c.append(0)
			d.append(DV.CONT_SLACK)
			dprime.append(slackGroupID)
			d_details[len(d)-1]['vtype'] = GRB.CONTINUOUS
			d_details[len(d)-1]['lb'] 	 = 0.0
			d_details[len(d)-1]['ub'] 	 = GRB.INFINITY
						
		elif (r[row_idx] == SIGN.GE):
			# Add a "-1" in this row in a new column:
			slack_col += 1
			A[row_idx, slack_col] = -1

			c.append(0)
			d.append(DV.CONT_SLACK)
			dprime.append(surplusGroupID)
			d_details[len(d)-1]['vtype'] = GRB.CONTINUOUS
			d_details[len(d)-1]['lb'] 	 = 0.0
			d_details[len(d)-1]['ub'] 	 = GRB.INFINITY
				
	return (A, c, d, dprime, d_details, numConstr, numDvars, numSlacks)
                        
def packMatrix(g, gprime, c, A, d, dprime, r, b):
		
	# Combine the inputs into a single np ndarray.
		
	rows = len(A) + 3		# Add row for c, row for d, and row for dprime
	cols = len(A[0]) + 4	# Add cols for g, gprime, r, and b
	
	packed = np.zeros((rows, cols))
		
	packed[1:-2, 0] = g					# First column, skip 1st row and last 2 rows
	packed[1:-2, 1] = gprime			# Second column, skip 1st row and last 2 rows	
	packed[0, 2:len(c)+2] = c			# First row, skip 1st 2 columns
	packed[1:-2, 2:len(A[0])+2] = A		# Skip 1st row and last 2 rows. Skip 1st 2 columns
	packed[-2, 2:len(d)+2] = d			# 2nd-to-last row.  Skip 1st 2 columns
	packed[-1, 2:len(d)+2] = dprime		# Last row.  Skip 1st 2 columns
	packed[1:-2, -2] = r				# 2nd-to-last column.  Skip 1st row and last 2 rows.
	packed[1:-2, -1] = b				# Last column.  Skip 1st row and last 2 rows.
	
	return packed
	
def myNormalize(inArray):
	
	# For each subset of our giant packed array,
	# (c, d, b, and A),
	# normalize the values to be in the range [-1, 1]

	c = inArray[0, 0:-1]				# first row, ignoring the last column (b)	
	c = c / np.max(np.abs(c))			# scale to [-1, 1]
	inArray[0, 0:-1] = c
	
	d = inArray[-1, 0:-1]				# last row, ignoring the last column (b)
	d = d / np.max(np.abs(d))			# scale to [0, 1] (our "d" values are all non-negative)
	inArray[-1, 0:-1] = d

	b = inArray[1:-1, -1]				# last column, ignoring first and last rows
	b = b / np.max(np.abs(b))			# scale to [-1, 1]
	inArray[1:-1, -1] = b

	A = inArray[1:-1, :-1]				# Ignore top and bottom rows, ignore last column
	A = A / np.max(np.abs(A))			# scale to [-1, 1]
	inArray[1:-1, :-1] = A
	
	return inArray

def myConvertGS(inArray):
	
	# Given an inArray (2-D matrix),
	# with values in range [-1, 1],
	# convert to a grayscale image with
	# values in the range [0, 255].
	#
	# Specifically, if 
	# 	GSneg = [128, 191]
	# 	GSpos = [192, 255]
	# then
	#	0 --> 0
	#	Negatives: [-1, 0) --> [128, 191]
	#	Positives: ( 0, 1] --> [192, 255]
		
	negMask = inArray < 0						
	posMask = inArray > 0
	inArray[negMask] = (1 + inArray[negMask])*(GSneg[1] - GSneg[0]) + GSneg[0]
	inArray[posMask] = inArray[posMask]*(GSpos[1] - GSpos[0]) + GSpos[0]
	
	return inArray

def myConvertHSV(inArray):
	
	# NOTE:
	# OpenCV uses  H: 0 - 179, S: 0 - 255, V: 0 - 255
	
	# Create an array, with 3 channels in each row/col.
	# Initialize it with [H,S,V] = [0,0,0] (black)
	imgFullHSV = np.full((inArray.shape[0], inArray.shape[1], 3), [0, 0, 0])
		
	# For each value in inArray, convert to HSV.
	# Unfortunately, I don't know how to do this without two nested for loops.
	for i in range(0, inArray.shape[0]):
		for j in range(0, inArray.shape[1]):
			if (inArray[i,j] < 0):
				# Shades of red.
				# More negative --> brighter red
				# We'll leave H = 0 (red hue), S = 255 (max saturation).
				# Vary V from 102 (closer to 0) to 255 (closer to -1)
				
				# imgFullHSV[i,j] = [0, 255, 102 - (255-102)*inArray[i,j]]		HARDCODED
				# myHue = HSVneg[0]
				# mySat = HSVneg[1]
				# myValLow = HSVneg[2]
				# myValHigh = HSVneg[3]
				imgFullHSV[i,j] = [HSVneg[0], HSVneg[1], HSVneg[2] - (HSVneg[3]-HSVneg[2])*inArray[i,j]]
				
			elif (inArray[i,j] > 0):
				# Shades of green.
				# More positve --> brighter green
				# We'll leave H = 70 (green hue), S = 255 (max saturation).
				# Vary V from 102 (closer to 0) to 255 (closer to +1)

				# imgFullHSV[i,j] = [70, 255, 102 + (255-102)*inArray[i,j]]		HARDCODED
				# myHue = HSVpos[0]
				# mySat = HSVpos[1]
				# myValLow = HSVpos[2]
				# myValHigh = HSVpos[3]
				imgFullHSV[i,j] = [HSVpos[0], HSVpos[1], HSVpos[2] + (HSVpos[3]-HSVpos[2])*inArray[i,j]]
					
	return imgFullHSV
	
			
def createImages(inArray):

	# This function will return several images:
	# 1)  Include slack/surplus variables.  Specifically, grab everything except the "g" and "r" columns. 
	# 2)  No slack/surplus variables.  This is a subset of (1).
	# imgFullGS
	# imgFullHSV
	# imgNoSlackGS
	# imgNoSlackHSV
	# imgNonzerosBW
	# imgNonzerosHSV


	# Get everything, except 
	#	- the g (index 0) gprime (index 1) and r (index -2) columns,
	#	- the last row (dprime).
	cols = list(range(2, inArray.shape[1]))
	cols.remove(cols[-2])
	
	imgFull = inArray[:-1, cols]

	'''
	===============NOTE==========================
	For each image we create, first create
	a **copy** of imgFull.
	
		newImage = np.copy(imgFull)
	 
	Otherwise, if you do 
	newImage = imgFull, you will be making
	changes to imgFull.  This would mean that
	your later use of imgFull will be using 
	contaminated/modified data.
	=============================================
	'''


	# =================================================
	# Create a BW image showing all non-zero values 
	# in the raw np array (i.e., before normalizing)
	# -------------------------------------------------
	# 0 --> 0
	# Not zero --> 255
	imgNonzerosBW = np.copy(imgFull)
	nonzeroMask = imgNonzerosBW != 0
	imgNonzerosBW[nonzeroMask] = 255
	# =================================================


	# =================================================
	# Create a grayscale image, including slack/surplus variables
	# -------------------------------------------------

	# Make a copy of imgFull
	imgFullGS = np.copy(imgFull)

	# Normalize, independently, the values in c, d, b, and A
	# to be in the range [-1, 1].
	imgFullGS = myNormalize(imgFullGS)

	# Map the normalized values to the BW range of [0, 255]
	imgFullGS = myConvertGS(imgFullGS)
	
	# Convert to uint8 (so we can display the image)
	imgFullGS = imgFullGS.astype(np.uint8)	
	# =================================================

	'''
	SEE DIRECTLY ABOVE.
	# -------------------------------------------------
	# Create a grayscale image, including slack/surplus variables
	imgFullGS = np.copy(imgFull)
	
	# Scale the values in the image "appropriately"
	# Map values in c from 0 - 255.
	c = imgFullGS[0, 0:-1]				# first row, ignoring the last column (b)	
	c = c / np.max(np.abs(c))			# scale to [-1, 1]
	negMask = c < 0						
	posMask = c > 0
	# c[negMask] = (1+c[negMask])*63 + 128		HARDCODED
	# c[posMask] = c[posMask]*63 + 192
	c[negMask] = (1 + c[negMask])*(GSneg[1] - GSneg[0]) + GSneg[0]
	c[posMask] = c[posMask]*(GSpos[1] - GSpos[0]) + GSpos[0]
	imgFullGS[0, 0:-1] = c[:]
		
	# Map values in d from 0 - 255.
	# Technically, these will be mapped to the range [ GSpos[0], GSpos[1] ].
	d = imgFullGS[-1, 0:-1]				# last row, ignoring the last column (b)
	d = d / np.max(np.abs(d))			# scale to [0, 1] (our "d" values are all non-negative)
	# d = d*63 + 192					HARDCODED
	d = d*(GSpos[1] - GSpos[0]) + GSpos[0]
	imgFullGS[-1, 0:-1] = d[:]
	
	# Map values in b from 0 - 255.
	b = imgFullGS[1:-1, -1]				# last column, ignoring first and last rows
	b = b / np.max(np.abs(b))			# scale to [-1, 1]
	negMask = b < 0
	posMask = b > 0
	b[negMask] = (1 + b[negMask])*(GSneg[1] - GSneg[0]) + GSneg[0]
	b[posMask] = b[posMask]*(GSpos[1] - GSpos[0]) + GSpos[0]
	imgFullGS[1:-1, -1] = b[:]

	# Map values in A from 0 - 255.
	A = imgFullGS[1:-1, :-1]			# Ignore top and bottom rows, ignore last column
	A = A / np.max(np.abs(A))			# scale to [-1, 1]
	negMask = A < 0
	posMask = A > 0
	A[negMask] = (1 + A[negMask])*(GSneg[1] - GSneg[0]) + GSneg[0]
	A[posMask] = A[posMask]*(GSpos[1] - GSpos[0]) + GSpos[0]
	imgFullGS[1:-1, :-1] = A[:, :]
	
	# Convert to uint8 (so we can display the image)
	imgFullGS = imgFullGS.astype(np.uint8)	
	# -------------------------------------------------
	'''

	# -------------------------------------------------
	# Create an image like imgFullGS, but remove the slack/surplus variables. 
	# Find the columns of imgFullGS such that the last row doesn't equal DV.CONT_SLACK:
	slackColsMask = imgFull[-1,:] != DV.CONT_SLACK		# NOTE: We're looking at the unmodified imgFull
	
	imgNoSlackGS = imgFullGS[:, slackColsMask]
	# -------------------------------------------------


	# =================================================
	# Create HSV and BGR versions of imgFull
	# -------------------------------------------------
	# HSV Mapping:
	'''
	1)  For each of c, b, d, and A, normalize to the range [-1, 1].
	2)  Map these values to the BW range of [0, 255], such that
		0 --> black
		Negatives: [-1, 0) --> shades of red.  Closer to -1 is a brighter red.
		Positives: ( 0, 1] --> shades of green.  Closer to -1 is a brighter green.
	'''
	
	# Make a copy of imgFull
	# This is a 2-D array
	tmpHSV = np.copy(imgFull)

	# Normalize, independently, the values in c, d, b, and A
	# to be in the range [-1, 1].
	tmpHSV = myNormalize(tmpHSV)

	# Map the normalized values to HSV (color)
	# This is now a 3-D array (3-channels for each row/column)
	imgFullHSV = myConvertHSV(tmpHSV)
	
	# Convert to uint8 (so we can display the image)
	imgFullHSV = imgFullHSV.astype(np.uint8)	
	
	# For display purposes, convert HSV to BGR
	# NOTE:  We can't use imshow() to display an HSV image.
	imgFullBGR = cv2.cvtColor(imgFullHSV, cv2.COLOR_HSV2BGR)
				
	# Now, convert back from BGR to HSV
	# FIXME -- Need to find a way for cv2 to know initially
	#          that we had an HSV-formatted image.
	# UPDATE:  cv2 can't display an HSV image directly.
	#		   Perhaps we just need to export the HSV info
	#          as a numpy array and re-read it separately.
	# imgFullHSV = cv2.cvtColor(imgFullBGR, cv2.COLOR_BGR2HSV)
	# =================================================


	# =================================================
	# Create an image like imgFullBGR, but remove the slack/surplus variables. 
	# -------------------------------------------------	
	imgNoSlackBGR = imgFullBGR[:, slackColsMask, :]
	# =================================================
	
	
	return (imgFullGS, imgNoSlackGS, imgNonzerosBW, imgFullBGR, imgNoSlackBGR)
	
def export(g, numConstr, numDvars, numSlacks, packed, imgFullGS, imgNoSlackGS, imgNonzerosBW, imgFullBGR, imgNoSlackBGR, n, label, folder):

	# Write info to file(s)
	
	# Create the subfolder, if it doesn't already exist
	folder = '%s/Projects/tspml/output/%s_%s' % (HOME_DIRECTORY, folder, n)	

	if (not os.path.isdir(folder)):
		print("%s does not exist" % (folder))
		os.makedirs(folder)

	# 1) Save our "packed" np array as a .csv
	# print(packed.dtype)
	np.savetxt(folder + "/packed.csv", packed, delimiter=",")
	
	# 2) Save our images as .png files
	cv2.imwrite(folder + "/imgFullGS.png", imgFullGS, [int(cv2.IMWRITE_PNG_COMPRESSION), 0]) # 0 --> no compression
	cv2.imwrite(folder + "/imgNoSlackGS.png", imgNoSlackGS, [int(cv2.IMWRITE_PNG_COMPRESSION), 0]) # 0 --> no compression
	cv2.imwrite(folder + "/imgNonzerosBW.png", imgNonzerosBW, [int(cv2.IMWRITE_PNG_COMPRESSION), 0]) # 0 --> no compression
	cv2.imwrite(folder + "/imgFullBGR.png", imgFullBGR, [int(cv2.IMWRITE_PNG_COMPRESSION), 0]) # 0 --> no compression
	cv2.imwrite(folder + "/imgNoSlackBGR.png", imgNoSlackBGR, [int(cv2.IMWRITE_PNG_COMPRESSION), 0]) # 0 --> no compression
	
	# 3) Export the problem parameters
	outfile = open(folder + "/params.csv", "w")
	outfile.write("label,%s\n" % (label))	
	outfile.write("numNodes,%d\n" % (n))	
	outfile.write("numGroups,%d\n" % (max(g)))
	outfile.write("numConstr,%d\n" % (numConstr))
	outfile.write("numDecVars (without slacks),%d\n" % (numDvars))
	outfile.write("num slacks/surplus,%d\n" % (numSlacks))
	
	outfile.write("GSneg,%d,%d\n" % (GSneg[0], GSneg[1]))
	outfile.write("GSpos,%d,%d\n" % (GSpos[0], GSpos[1]))
	outfile.write("HSVneg,%d,%d,%d,%d\n" % (HSVneg[0], HSVneg[1], HSVneg[2], HSVneg[3]))
	outfile.write("HSVpos,%d,%d,%d,%d\n" % (HSVpos[0], HSVpos[1], HSVpos[2], HSVpos[3]))
	
	outfile.close()	
	
	return 0
	
def get_c_d(m, decvars):

	### c vector - index in this list will match variable index in m._vars 
	# (i.e. c[0] is cost for variable m._vars[0])
	
	# We're assuming all models are MINIMIZATION.
	if (m.ModelSense == GRB.MINIMIZE):
		multiplier = 1
	else:
		multiplier = -1
	
	
	### d vector - index in this dictionary will match variable index in m._vars 
	# (i.e. d[0] is info for variable m._vars[0])
	c = []
	d = []
	d_details = defaultdict(make_dict)
	for i in range(0,len(decvars)):
		d_details[i]['vtype'] = decvars[i].vtype
		d_details[i]['lb'] = decvars[i].lb
		d_details[i]['ub'] = decvars[i].ub
				
		'''	
		# Continuous Variables:
		self.CONT_NN	= 0		# Non-negative
		self.CONT_URS	= 1		# Unrestricted in Sign
		self.CONT_BNDED	= 2		# Bounded
		self.CONT_HARD	= 3		# Hard-coded (e.g., there's a constraint that says "x = 0")
		self.CONT_SLACK	= 4		# Slack OR Surplus variable
	
		# Integer Variables:
		self.INT_BIN	= 10	# Binary
		self.INT_GEN	= 11	# General Integer
		self.INT_BNDED	= 12	# Bounded (but not binary)
		self.INT_HARD	= 13	# Hard-coded (e.g., y = 1)
		'''
		
		# What are the options here?
		# GRB.CONTINUOUS (C)
		# GRB.BINARY (B)
		# GRB.INTEGER (I)
		# print m._vars[i].vtype
		if (decvars[i].vtype == GRB.CONTINUOUS):
			tmpClass = DV.CONT_NN
			if (decvars[i].lb == decvars[i].ub):
				tmpClass = DV.CONT_HARD
			elif (decvars[i].lb < 0):
				tmpClass = DV.CONT_URS
			elif (decvars[i].ub < GRB.INFINITY): 	
				tmpClass = DV.CONT_BNDED
	
		elif (decvars[i].vtype == GRB.BINARY):
			tmpClass = DV.INT_BIN
			if (decvars[i].lb == decvars[i].ub):
				tmpClass = DV.INT_HARD
	
		else:	
			tmpClass = DV.INT_GEN
			if (decvars[i].lb == decvars[i].ub):
				tmpClass = DV.INT_HARD
			elif ((decvars[i].lb == 0) and (decvars[i].ub == 1)):
				tmpClass = DV.INT_BIN
			elif (decvars[i].ub < GRB.INFINITY): 	
				tmpClass = DV.INT_BNDED
	
				
		d.append(tmpClass)
				
		c.append(multiplier * decvars[i].obj)

	
	return (c, d, d_details)
	
def get_b_r(constrs):
	### r vector - index in this list will match constraint index in m._constrs
	# (i.e. r[0] is relationship for constraint m._constrs[0])
	
	### b vector - index in this list will match constraint index in m._constrs
	# (i.e. r[0] is RHS for constraint m._constrs[0])
	r = []
	b = []
	for i in range(0,len(constrs)):

		b.append(constrs[i].RHS)
		
		'''
		GRB.EQUAL         ('=')
		GRB.LESS_EQUAL    ('<')
		GRB.GREATER_EQUAL ('>')
		'''	
		if (constrs[i].Sense == GRB.LESS_EQUAL):
			tmpSense = SIGN.LE
		elif (constrs[i].Sense == GRB.GREATER_EQUAL):
			tmpSense = SIGN.GE
		else:
			tmpSense = SIGN.EQ
		
		r.append(tmpSense)
	
	return (b, r)
		
def get_gprime(g, A):
	# gprime vector.
	# For each constraint, classify it as being of a certain type.
	# See the bottom of http://miplib.zib.de/miplib2010.php for constraint types.
	
	print("FIXME -- gprime is just filled with -1s right now")
	gprime = np.full((len(g)), -1)
	
	return (gprime)
		
def generateOutput(m, g, dprime, n, folder, label, displayImages):	
	# This is our "main" function.
	
	# Get lists of variables and constraints
	decvars = m.getVars()
	constrs = m.getConstrs()	
			
	# Get the c and d lists
	# Get the d_details dictionary
	(c, d, d_details) = get_c_d(m, decvars)
	
	# Get the b and r lists
	(b, r) = get_b_r(constrs)
	
	# Get the A matrix (np) and update c, d, and d_details
	# Update dprime to include any slacks/surpluses we generate
	(A, c, d, dprime, d_details, numConstr, numDvars, numSlacks) = buildA(m, decvars, constrs, r, c, d, dprime, d_details)
		
	# FIXME
	# Get the gprime list
	print("FIXME - get_gprime()")
	gprime = get_gprime(g, A)
		
	# Pack everything up into a single large numpy ndarray
	packed = packMatrix(g, gprime, c, A, d, dprime, r, b)
	
	# Create images from the "packed" ndarray:
	(imgFullGS, imgNoSlackGS, imgNonzerosBW, imgFullBGR, imgNoSlackBGR) = createImages(packed)
	
	# Export data to files:
	export(g, numConstr, numDvars, numSlacks, packed, imgFullGS, imgNoSlackGS, imgNonzerosBW, imgFullBGR, imgNoSlackBGR, n, label, folder)	
	
	# Display Images
	if (displayImages):
		print("Hit 'ALT' to close windows")
		cv2.imshow("Full Grayscale", imgFullGS)
		cv2.imshow("No Slacks Grayscale", imgNoSlackGS)
		cv2.imshow("Non-zeros BW", imgNonzerosBW)
		cv2.imshow("Full BGR", imgFullBGR)
		cv2.imshow("No Slacks BGR", imgNoSlackBGR)

		cv2.waitKey(0)
		
