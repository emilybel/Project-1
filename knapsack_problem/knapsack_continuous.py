# =================================================================
# Include our required packages and initialize the "g" list:
import common
import argparse
g = []
dprime = []

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--numitems", help = "number of items, (e.g., books)")
ap.add_argument("-f", "--folder", help = "name of subfolder that will hold our generated output (like 'tsp_mtz')")
ap.add_argument("-l", "--label", help = "label describing this problem (like 'tsp_mtz')")
ap.add_argument("-d", "--displayImages", default = 0, help = "binary value; 0 --> don't display images; 1 --> show the images")

args = vars(ap.parse_args())

n = int(args["numitems"])

# Example Usage:
# python knapsack_continuous.py -n 200 -f knapsack_cont -l knapsack_cont -d 1

# NOTE:  I've only tested this with Python 2.7.
#        I couldn't get gurobipy to work with Python 3.5.
# =================================================================




from gurobipy import *
from collections import defaultdict
from math import *
import random

# import csv			(doesn't appear to be used)
# import time			(doesn't appear to be used)
# import sys			(doesn't appear to be used)
# import os				(doesn't appear to be used)

def make_dict():
	return defaultdict(make_dict)



V = list(range(0, n+1))

# =================================================================
# Parameters
c = defaultdict(make_dict)
a = defaultdict(make_dict)

for i in V:
	c[i] = random.random()
	a[i] = random.random()
	
b = 1

# =================================================================


m = Model('knap_cont')
m.ModelSense = GRB.MINIMIZE

# =================================================================
# Tell Gurobi not to print to a log file
m.params.OutputFlag = 0				# MAKE SURE THIS IS ADDED
# =================================================================


# m.Params.TimeLimit = 600			(we don't need this)




# Decision Variables

## x[i] binary 1 if packed, 0 if left out
decvarx = defaultdict(make_dict)
'''
for i in E:
	for j in E[i]:
		decvarx[i][j] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, obj=E[i][j].c, name="x.%d.%d"%(i,j))
'''
for i in V:
	decvarx[i] = m.addVar(lb=0, ub=1, vtype=GRB.CONTINUOUS, obj=c[i], name="x.%d" % (i))
	# =================================================================
	dprime.append(1)
	# =================================================================

decvaru = defaultdict(make_dict)

m.update()




# Constraints


m.addConstr(quicksum(a[i] * decvarx[i] for i in V) <= b, "Constr.1")
# =================================================================
g.append(1)
# =================================================================





# m.optimize()		<---  We won't need to actually solve these problems



# =================================================================
# Call our package to generate our required information:
m.update()
common.generateOutput(m, g, dprime, n, args["folder"], args["label"], bool(args["displayImages"]))
# =================================================================
