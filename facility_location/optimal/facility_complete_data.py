'''
Facility Location Problem
5 possible warehouse locations and 5 customers
Each location will have a unique capacity, fixed(building costs) and variable(cost to increase facility size by one unit) costs, 
and shipping costs to the respective customer locations.
Select a facility location that minimizes the costs of shipping to all customers, building the facility, meet demand, and not exceed capacity.
'''
# =================================================================
# Include our required packages:
import argparse


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--datafolder", help = "import data from .csv")
ap.add_argument("-t", "--maxTime", help = "maximum run time in seconds")

args = vars(ap.parse_args())


datafile = str(args["datafolder"])
maxTime = int(args["maxTime"])

# Example Usage:
# python facility_complete_data.py -d dataset1 -t 30

# =================================================================

from gurobipy import *
from collections import defaultdict
from math import *
import random

import csv			
# import time			(doesn't appear to be used)
# import sys			(doesn't appear to be used)
# import os				(doesn't appear to be used)

def make_dict():
	return defaultdict(make_dict)

####################################################################
'''
We need to set the parameters that determine the solution.
When individual items have specific weights/distances and costs/benefits, those values
need to be set in a dictionary.
'''
# =================================================================
# Parameters

c = defaultdict(make_dict)
f = {}
v = {}
u = {}
d = {}
cust = {}

# c[i][j] shipping cost
# f[i] fixed cost to build warehouse
# v[i] variable cost per unit of warehouse capacity
# u[i] max capacity of warehouse i
# d[j] demand for customer j

######################### IMPORT DATA
import csv
import numpy as np

W = []
C = []
with open('dataset1/shipping_cost_matrix.csv', 'r') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	first = True
	for row in spamreader:
		if (row[0][0] != '%'):
			if first:
				#for only the first row that isnt a %
				for z in range(1, len(row)):
					cust[z] = int(row[z])
					first = False
					#cust[index#] = 101...
					print ('cust[%d] = %d' %(z, cust[z]))
					#print z
					#print row
					#print row[z]
					C.append(cust[z])
			else:
				#for the remaining rows we have the warehouse number
				i = int(row[0])
				W.append(i)
				for j in range(1, len(row)):	
					c[i][cust[j]]= float(row[j])
					#print c[i][cust[j]]
					#cost information
					print ('c[%d][%d] = %f' %(i, cust[j], c[i][cust[j]]))
					
					
					
with open('dataset1/extra.csv', 'r') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in spamreader:
		if (row[0][0] != '%'):		
			i = int(row[0])
			u[i] = float(row[1])
			f[i] = float(row[2])
			v[i] = float(row[3])
'''
Add print statements to show what the indices of u[], f[], v[], and their values
'''

#print u
#print f
#print v


with open('dataset1/demand.csv', 'r') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in spamreader:
		if (row[0][0] != '%'):
			for i in range(0,len(row)):
				#print row[i]
				d[C[i]] = float(row[i])

'''
Add print statements to show what the indices of d[], and their values
'''
# =================================================================

#Name the model

#minimize the cost of building warehouses, and fulfilling demand to all customers
m = Model('facility_location')
m.ModelSense = GRB.MINIMIZE



# =================================================================
# Tell Gurobi not to print to a log file
m.params.OutputFlag = 0				# MAKE SURE THIS IS ADDED
# =================================================================


m.Params.TimeLimit = maxTime			



# ==================================================================
# Decision Variables
# ==================================================================

decvary = defaultdict(make_dict)
# y[i] = is a warehouse located at site i?
for i in W:
	decvary[i] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, obj= f[i], name="y.%d"%(i))



decvarz = defaultdict(make_dict)
#z[i] = size of warehouse at location i
for i in W:
	decvarz[i] = m.addVar(lb=0, ub=u[i], vtype=GRB.CONTINUOUS, obj=v[i], name="z.%d"%(i))			## ub is max capacity



decvarx = defaultdict(make_dict)
# x[i][j] = amount of product shipped from warehouse i to customer j
for i in W:
	for j in C:
		decvarx[i][j] = m.addVar(lb=0, ub=d[j], vtype=GRB.CONTINUOUS, obj= c[i][j], name="x.%d.%d"%(i,j)) ## demand
		

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
	m.addConstr(quicksum(decvarx[i][j] for i in W) == d[j], "Constr.1.%d" % (j))


# Supply must not exceed capacity of warehouse
for i in W:
	m.addConstr(quicksum(decvarx[i][j] for j in C)<= decvarz[i], "Constr.2.%d" %(i))



# capacity of warehouse is less than max capacity of site i
for i in W:
	m.addConstr(decvarz[i] <= (u[i]*decvary[i]), "Constr.3.%d" %(i))


m.update()
m.optimize()		


# from http://www.gurobi.com/documentation/8.1/examples/workforce1_py.html
m.optimize()
status = m.status
if status == GRB.Status.UNBOUNDED:
	print('The model cannot be solved because it is unbounded')
	exit(0)
if status == GRB.Status.OPTIMAL:
	print('The optimal objective is %g' % m.objVal)
	
	for i in W:
		if decvary[i].x >= 0.0001:
			print ('Build a warehouse at location %d' %(i))
			#print decvary[i].x
		if decvarz[i].x >= 0.0001:
			print ('The capacity of warehouse %d is %f' %(i, decvarz[i].x))
			#print decvarz[i].x
		
	for i in W:
		for j in C:
			if decvarx[i][j].x >= 0.0001:
				print ('Warehouse %d will ship %f units to customer %d' %(i, decvarx[i][j].x, j))
				#print decvarx[i][j].x 
			
	exit(0)
if status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
    print('Optimization was stopped with status %d' % status)
    exit(0)

# do IIS
print('The model is infeasible; computing IIS')
m.computeIIS()
if m.IISMinimal:
	print('IIS is minimal\n')
else:
	print('IIS is not minimal\n')
print('\nThe following constraint(s) cannot be satisfied:')
for c in m.getConstrs():
	if c.IISConstr:
		print('%s' % c.constrName)

