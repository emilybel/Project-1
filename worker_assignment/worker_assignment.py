'''
Worker Assignment

'''

# =================================================================
# Include our required packages and initialize the "g" list:
import common
import argparse
g = []
dprime = []

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--numitems", help = "number of items (e.g., books)")
ap.add_argument("-f", "--folder", help = "name of subfolder that will hold our generated output (like 'tsp_mtz')")
ap.add_argument("-l", "--label", help = "label describing this problem (like 'tsp_mtz')")
ap.add_argument("-d", "--displayImages", default = 0, help = "binary value; 0 --> don't display images; 1 --> show the images")

args = vars(ap.parse_args())

n = int(args["numitems"])

# Example Usage:
# python worker_assignment.py -n 50 -f work_assign -l work_assign -d 1

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


## V is the list of i's (every item that we have)
## starting at 1, up to but not including the second number, so use n+1 to go to n
V = list(range(1, n+1))


'''
We need to set the parameters that determine the solution.
When individual items have specific weights/distances and costs/benefits, those values
need to be set in a dictionary.
For the sake of just formulating the problem, each individual value can be set randomly.

random.random() sets a value between 0 and 1.
'''
# =================================================================
# Parameters

c = defaultdict(make_dict)

for i in V:
	for j in V:		
		c[i][j] = random.random()
		
#We need a cost associated for each worker/job combination
# =================================================================



'''
Name the model
'''
#minimize the cost of having each worker in each job
m = Model('work_assign')
m.ModelSense = GRB.MINIMIZE



# =================================================================
# Tell Gurobi not to print to a log file
m.params.OutputFlag = 0				# MAKE SURE THIS IS ADDED
# =================================================================


# m.Params.TimeLimit = 600			(we don't need this)



# ==================================================================
# Decision Variables
# ==================================================================


decvarx = defaultdict(make_dict)

for i in V:
	for j in V:
		decvarx[i][j] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, obj= c[i][j], name="x.%d.%d"%(i,j))
		
		dprime.append(1)

#uses for because we need all of the variables defined in the total number of workers and the total number of jobs


m.update()



'''
# Labels each iteration of the constraint %d integer and the integer it chooses is i
# "Constr. %d. %d" % (i, j) fills in i as first %d and j as second.
'''
# ==================================================================
# Constraints
# ==================================================================

m.addConstr(quicksum(c[i][j] * decvarx[i][j] for i in V) == 1, "Constr.%d")
# =================================================================
g.append(1)
# =================================================================


m.addConstr(quicksum(c[i][j] * decvarx[i][j] for j in V) == 1, "Constr.%d")
# =================================================================
g.append(2)
# =================================================================




# m.optimize()		<---  We won't need to actually solve these problems



# =================================================================
# Call our package to generate our required information:
m.update()
common.generateOutput(m, g, dprime, n, args["folder"], args["label"], bool(args["displayImages"]))
# =================================================================
