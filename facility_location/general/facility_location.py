'''
Facility Location Problem
5 possible warehouse locations and 5 customers
Each location will have a unique capacity, fixed(building costs) and variable(cost to increase facility size by one unit) costs, 
and shipping costs to the respective customer locations.
Select a facility location that minimizes the costs of shipping to all customers, building the facility, meet demand, and not exceed capacity.
'''
# =================================================================
# Include our required packages and initialize the "g" list:
import common
import argparse
g = []
dprime = []

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--numitems", help = "number of items (e.g., books)")
ap.add_argument("-n", "--numcustomers", help = "number of customers receiving")
ap.add_argument("-f", "--folder", help = "name of subfolder that will hold our generated output (like 'tsp_mtz')")
ap.add_argument("-l", "--label", help = "label describing this problem (like 'tsp_mtz')")
ap.add_argument("-d", "--displayImages", default = 0, help = "binary value; 0 --> don't display images; 1 --> show the images")

args = vars(ap.parse_args())

m = int(args["numitems"])
n = int(args["numcustomers"])


# Example Usage:
# python facility_location.py -m 5 -n 5 -f facility_location -l facility_location -d 1

# =================================================================

from gurobipy import *
from collections import defaultdict
from math import *
import random

def make_dict():
	return defaultdict(make_dict)
	
## W is the list of i's (every possible warehouse location that we have)
## C is the list of j's (customers)
## starting at 1, up to but not including the second number, so use n+1 to go to n
W = list(range(1, m+1))
C = list(range(1, n+1))

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
f = defaultdict(make_dict)
v = defaultdict(make_dict)
u = defaultdict(make_dict)
d = defaultdict(make_dict)

# c[i][j] shipping cost
# f[i] fixed cost to build warehouse
# v[i] variable cost per unit of warehouse capacity
# u[i] max capacity of warehouse i
# d[j] demand for customer j
 
for i in W:
	for j in C:
		c[i][j] = random.random()
		
for i in W:
	f[i] = random.random()
	v[i] = random.random()
	u[i] = 80
	
for j in C:
	d[j] = random.random()

'''
Ko = {}					# set of arcs leaving node i, creates an empty dictionary.... uses dictionary because the index starts at 1, lists start at 0
Kt = {}					# set of arcs ending at node i
k = 1 
for i in V:				#for every new node i, a new list is created.
	Ko[i] = []
	Kt[i] = []
	for j in V:
		if (j != i):
			c[k] = random.random()  	# cost to travel on that arc
			u[k] = 2		# assume that all capacities are the same in this case, and equal to 2
			Ko[i].append(k)			# add arc k to the list of arcs leaving node i
			Kt[j].append(k)			# add arc k to the lsit of arcs ending at node j
			
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
'''
	
	
	
		

# =================================================================



'''
Name the model
'''
#minimize the cost of building warehouses, and fulfilling demand to all customers
m = Model('facility_location')
m.ModelSense = GRB.MINIMIZE



# =================================================================
# Tell Gurobi not to print to a log file
m.params.OutputFlag = 0				# MAKE SURE THIS IS ADDED
# =================================================================


# m.Params.TimeLimit = 600			(we don't need this)



# ==================================================================
# Decision Variables
# ==================================================================

decvary = defaultdict(make_dict)
# y[i] = is a warehouse located at site i?

for i in W:
	decvary[i] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, obj= f[i], name="y.%d"%(i))
	dprime.append(1)


decvarz = defaultdict(make_dict)
#z[i] = size of warehouse at location i

for i in W:
	decvarz[i] = m.addVar(lb=0, ub=u[i], vtype=GRB.CONTINUOUS, obj=v[i], name="z.%d"%(i))			## ub is max capacity
	dprime.append(2)


decvarx = defaultdict(make_dict)
# x[i][j] = amount of product shipped from warehouse i to customer j
for i in W:
	for j in C:
		decvarx[i][j] = m.addVar(lb=0, ub=d[j], vtype=GRB.CONTINUOUS, obj= c[i][j], name="x.%d.%d"%(i,j)) ## demand
		
		dprime.append(3)

#range of arcs defined above in parameters, n starts at 1, up to and including n so se n+1


m.update()



'''
# Labels each iteration of the constraint %d integer and the integer it chooses is i
# "Constr. %d. %d" % (i, j) fills in i as first %d and j as second.
'''
# ==================================================================
# Constraints
# ==================================================================

# Meet all demand
for j in C:
	m.addConstr(quicksum(decvarx[i][j] for i in M) == d[j], "Constr.1.%d" % (j))
	# =================================================================
	g.append(1)
	# =================================================================


# Supply must not exceed capacity of warehouse
for i in W:
	m.addConstr(quicksum(decvarx[i][j] for j in N)<= decvarz[i], "Constr.2.%d" %(i))
	# =================================================================
	g.append(2)
	# =================================================================


# capacity of warehouse is less than max capacity of site i
for i in W:
	m.addConstr(decvarz[i] <= (u[i]*decvary[i]), "Constr.3.%d" %(i))
	# =================================================================
	g.append(3)
	# =================================================================

# m.optimize()		<---  We won't need to actually solve these problems



# =================================================================
# Call our package to generate our required information:
m.update()
common.generateOutput(m, g, dprime, n, args["folder"], args["label"], bool(args["displayImages"]))
# =================================================================
