'''
Supply and Demand Network Flow Problem
An LP of a directed, connected graph of m nodes and n arcs. Each arc has a known capacity and unit cost, each node has a fixed external flow.
Determine the minimum cost plan to send flow through the network to satisfy the supply and demand requirements. 
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
# python supply_demand_NFP.py -n 50 -f Network -l Network -d 1

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



## V is the list of i's (every node that we have)
## starting at 1, up to but not including the second number, so use n+1 to go to n
V = list(range(1, n+1))

###################################################################################################### Create a list of arcs leaving node i and terminating at node i?


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
u = defaultdict(make_dict)
b = {}

# c(k) unit cost of flow through arc k[i][j]
# b(i) net supply (arc flow out - arc flow in) at node i
# u(k) capacity of arc k(i,j)


Ko = {}					# set of arcs leaving node i, creates an empty dictionary.... uses dictionary because the index starts at 1, lists start at 0
Kt = {}					# set of arcs ending at node i

for i in V:				#for every new node i, a new list is created.
	Ko[i] = []
	Kt[i] = []
k = 1 
for i in V:				#for every new node i, a new list is created.
	for j in V:
		if (j != i):
			c[k] = random.random()  	# cost to travel on that arc
			u[k] = 2		# assume that all capacities are the same in this case, and equal to 2
			Ko[i].append(k)			# add arc k to the list of arcs leaving node i
			Kt[j].append(k)			# add arc k to the list of arcs ending at node j
			
			k = k+1
n = k-1 					# n is the number of arcs in the network, assuming the graph is fully connected.


##randomly assign b[i] some +,-,0			
for i in V:						
	tmpRand = random.random()
	if (tmpRand <= 0.33):
		b[i] = -1				# if i is a demand node b[i]< 0
	elif (tmpRand <= 0.66):
		b[i] = 1				# if i is a supply node b[i]> 0
	else:
		b[i] = 0				# if i is a transhipment node b[i] = 0

	
	
	
		

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


# x[k] = flow through arc k(i,j) from node i to node j
for k in range(1, n+1):
	decvarx[k] = m.addVar(lb=0, ub=u[k], vtype=GRB.CONTINUOUS, obj= c[k], name="x.%d"%(k))
		
	dprime.append(1)

#range of arcs defined above in parameters, n starts at 1, up to and including n so se n+1


m.update()



'''
# Labels each iteration of the constraint %d integer and the integer it chooses is i
# "Constr. %d. %d" % (i, j) fills in i as first %d and j as second.
'''
# ==================================================================
# Constraints
# ==================================================================
for i in V:
	m.addConstr(quicksum(decvarx[k] for k in Ko[i]) - quicksum(decvarx[k] for k in Kt[i]) == b[i], "Constr.1.%d" % (i))
	# =================================================================
	g.append(1)
	# =================================================================

'''
places an upper bound on decvarx[k], or labeled already within the decision variable definition
for k in range(1, n+1):
	m.addConstr(decvarx[k] <= u[k], "Constr.2.%d" %(k))
	# =================================================================
	g.append(2)
	# =================================================================
'''



# m.optimize()		<---  We won't need to actually solve these problems



# =================================================================
# Call our package to generate our required information:
m.update()
common.generateOutput(m, g, dprime, n, args["folder"], args["label"], bool(args["displayImages"]))
# =================================================================
