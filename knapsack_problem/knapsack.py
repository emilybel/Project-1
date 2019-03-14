'''
Formulation from: https://www.win.tue.nl/~wscor/OW/2V300/H4.pdf
The knapsack problem is a way of optimizing the items that can fit inside of the bag.
Each item has a value of importance and a weight.
The objective is to maximize the value of the items inside the knapsack
without exceeding the available capacity of the bag.
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
# python knapsack.py -n 20 -f knapsack -l knapsack -d 1
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

c = defaultdict(make_dict) #benefit of having each item
a = defaultdict(make_dict) #weight of each item

for i in V:
	c[i] = random.random()
	a[i] = random.random() 
b = 1 #capacity of the knapsack
# =================================================================

#Name the model

m = Model('knapsack')
m.ModelSense = GRB.MINIMIZE

# =================================================================
# Tell Gurobi not to print to a log file
m.params.OutputFlag = 0				# MAKE SURE THIS IS ADDED
# =================================================================


# m.Params.TimeLimit = 600			(we don't need this)



'''
x[i] binary 1 if packed, 0 if left out
list = [1,3,5,7]
list[1] = 3 (first is entry 0)
dict = {'name/type' : 'value'}
decvarx stores the {variable number: m.addVar data}
'''

# ==================================================================
# Decision Variables
# ==================================================================


decvarx = defaultdict(make_dict)
'''
for i in E:
	for j in E[i]:
		decvarx[i][j] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, obj=E[i][j].c, name="x.%d.%d"%(i,j))
'''
#uses for because we need all of the variables defined in the total number of items
for i in V:
	decvarx[i] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, obj=c[i], name="x.%d" % (i))
	# =================================================================
	dprime.append(1)
	# =================================================================

m.update()




# ==================================================================
# Constraints
# ==================================================================

m.addConstr(quicksum(a[i] * decvarx[i] for i in V) <= b, "Constr.1")
# =================================================================
g.append(1)
# =================================================================
# Labels each iteration of the constraint %d integer and the integer it chooses is i
# "Constr. %d. %d" % (i, j) fills in i as first %d and j as second.



# m.optimize()		<---  We won't need to actually solve these problems



# =================================================================
# Call our package to generate our required information:
m.update()
common.generateOutput(m, g, dprime, n, args["folder"], args["label"], bool(args["displayImages"]))
# =================================================================
