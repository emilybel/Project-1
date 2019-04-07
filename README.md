# Python Programming Project
IE 494 Spring 2019: Emily Belote with Dr. Murray
University at Buffalo
Industrial and Systems Engineering


# Project Objective
To learn how to code and solve Linear Programming problems in Python.

#Formulations Studied

####General Formulation:
- worker_assignment.py : (Jensen pg 193)
- supply_demand_NFP.py : (Jensen pg 204)
- facilty_location.py : (Jensen pg 232)
- knapsack.py and knapsack_continuous.py : (Hurkens)


####Optimal Formulation:
- facilty_complete_data.py : (Jensen pg 232)

# Directory Structure
After the repository has been downloaded, the Project-1 directory should look like this. 

- There will be a file called common.py which is necessary for the general formulations, this README.md document and a folder for each LP name.
- `facilty_location` determines the optimal warehouse location in order to  serve a list of customers.
	- There are two types of facility location problems: the general formulation and the optimization problem.
	- Within the `optimal`folder, there are multiple `dataset` folders which are used to store data for different FLP's. Each folder contains the same file names, but opening the files will reveal different data.
- `knapsack_problem` determines whic items should be packed in a finite bag.
	- There are two types of knapscak problems. One for discrete item weights, and another for continuous item weights.
- `network_flow`determines the shipping pattern between nodes in order to meet each node's supply and demand needs.
- `worker_assignment` determines how workers should be assigned to a list of jobs.
- `output` contains all of the graphs and data that is saved for each iteration of the general formulation problems.


~~~
├── common.py
├── facility_location
│   ├── general
│   │   ├── common.py
│   │   ├── common.pyc
│   │   ├── facility_location.py
│   │   ├── gurobi.log
│   │   └── README.md
│   └── optimal
│       ├── dataset1
│       │   ├── demand.csv
│       │   ├── extra.csv
│       │   ├── README.md
│       │   └── shipping_cost_matrix.csv
│       ├── dataset2
│       │   ├── demand.csv
│       │   ├── extra.csv
│       │   └── shipping_cost_matrix.csv
│       ├── facility_complete_data.py
│       └── README.md
├── knapsack_problem
│   ├── common.py
│   ├── knapsack_continuous.py
│   ├── knapsack.py
│   └── README.md
├── network_flow
│   ├── common.py
│   ├── README.md
│   └── supply_demand_NFP.py
├── output
├── README.md
└── worker_assignment
    ├── common.py
    ├── README.md
    └── worker_assignment.py



~~~
Output:
	- Each time a code is run, a folder will be saved with the name `ProblemName_n` where n represents the number of items in the formulation.
	- There will be 5 `imgX.png` files where X is replaced by the name of the image and files called `packed.csv` and `params.csv`.
When running any of the general formulation problems, a folder of output will be created. The contents of `output` will look like this.
- This shows that each problem can be run multiple times with different values of n to produce different results.

~~~
├── knapsack_20
│   ├── imgFullBGR.png
│   ├── imgFullGS.png
│   ├── imgNonzerosBW.png
│   ├── imgNoSlackBGR.png
│   ├── imgNoSlackGS.png
│   ├── packed.csv
│   └── params.csv
├── knapsack_200
│   ├── imgFullBGR.png
│   ├── imgFullGS.png
│   ├── imgNonzerosBW.png
│   ├── imgNoSlackBGR.png
│   ├── imgNoSlackGS.png
│   ├── packed.csv
│   └── params.csv
├── knapsack_cont_200
│   ├── imgFullBGR.png
│   ├── imgFullGS.png
│   ├── imgNonzerosBW.png
│   ├── imgNoSlackBGR.png
│   ├── imgNoSlackGS.png
│   ├── packed.csv
│   └── params.csv
├── Network_2450
│   ├── imgFullBGR.png
│   ├── imgFullGS.png
│   ├── imgNonzerosBW.png
│   ├── imgNoSlackBGR.png
│   ├── imgNoSlackGS.png
│   ├── packed.csv
│   └── params.csv
├── tsp_mtz_20
│   ├── imgFullBGR.png
│   ├── imgFullGS.png
│   ├── imgNonzerosBW.png
│   ├── imgNoSlackBGR.png
│   ├── imgNoSlackGS.png
│   ├── packed.csv
│   └── params.csv
├── work_assign_5
│   ├── imgFullBGR.png
│   ├── imgFullGS.png
│   ├── imgNonzerosBW.png
│   ├── imgNoSlackBGR.png
│   ├── imgNoSlackGS.png
│   ├── packed.csv
│   └── params.csv
└── work_assign_50
    ├── imgFullBGR.png
    ├── imgFullGS.png
    ├── imgNonzerosBW.png
    ├── imgNoSlackBGR.png
    ├── imgNoSlackGS.png
    ├── packed.csv
    └── params.csv

~~~

# Running the Code

- In order to run the code, first enter the proper directory
	- `cd Projects/Project-1/%S` (Replace %s with the folder name of the desired problem)
- Then insert the proper run command as found within the code itself.
	- For example, to run the facility_location.py script, use the command
	`python facility_location.py -m 5 -n 5 -f facility_location -l facility_location -d 1`
	- The run command can be found in each script after the 'arguments' section.
	

# Formulation Specifics
The components required to formulate a Python LP are outlined below. Specific sections of code come from *facility_location.py* 

### Opening Lines
---
Each python script will begin with a fairly similar block of code which sets up the problem and allows the code to work. For the general formulations, there will be no answer to the problem, but the code is set up to create output graphs that demonstrate the structure of the problem. This information is used by the University at Buffalo Industrial Engineering Department's student research. Therefore importing common, the variables g and dprime, and the arguments f, l and d, are specific to the UB research project.
~~~
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
~~~
Since it is possible to change the number of facilities m and the number of customers n, we require these arguments to be input by the user. They will run the code with the following line, and change -m 5 and -n 5 to the true values in each case. The arguments f, l, and d determine how the output is stored for the UB research project. Then we will import the necessary python packages to run the code, and initialize th warehouse facilities W and customers C as lists of length m and n respectively.
~~~
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
~~~

### Parameters
---
Parameters are the known values that help to determine the solution to the problem. Often times each DV will have weights associated with them, or costs to making certain decisions.

Examples of Parameters: The distance between two facilities, the weight of a book, the number of hours in a person's shift, the total supply available, the demand of a particular client.

---

##### The general formulation initializes the parameters with random values.

- random.random() sets each paramter to a random value between 0 and 1.

First create the dictionaries for each parameter.
~~~
c = defaultdict(make_dict)
f = defaultdict(make_dict)
v = defaultdict(make_dict)
u = defaultdict(make_dict)
d = defaultdict(make_dict)
~~~


c[i][j] is the shipping cost from warehouse i to customer j. 
~~~
for i in W:
	for j in C:
		c[i][j] = random.random()
~~~

f[i] is the fixed cost to build warehouse i
v[i] variable cost per unit of warehouse capacity
u[i] max capacity of warehouse i
~~~
for i in W:
	f[i] = random.random()
	v[i] = random.random()
	u[i] = 80
~~~
d[j] demand for customer j
~~~	
for j in C:
	d[j] = random.random()
~~~

---

#####In order to solve this problem with actual values, we will need to import values for the parameters.
- This code comes from *facility_complete_data.py*
- All of the data is stored as csv files in the folder called *dataset1*

First, create dictionaries for all of the parameters. Then import the csv package so the data files can be read properly. Create a list W for the number of warehouses and list C for the number of customers. The lists will be populated as the code iterates through the csv files.

~~~
c = defaultdict(make_dict)
f = {}
v = {}
u = {}
d = {}
cust = {}

import csv
import numpy as np

W = []
C = []
~~~
Now begin to import the data from the file into the actual paramter values. c[i][j] values can be found in the file called *shipping_cost_matrix.csv* within the folder *dataset1*.

The file will read each row in the file. For the first row that does not begin with a % and comment, we will save the customer numbers.
~~~
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
					print ('cust[%d] = %d' %(z, cust[z]))
					C.append(cust[z])
~~~
 For all subsequent rows, the first column denotes the warehouse numbe, and each additional entry tells the shipping cost from the warehouse to all possible customers.
~~~
			else:
				#for the remaining rows we have the warehouse number
				i = int(row[0])
				W.append(i)
				for j in range(1, len(row)):	
					c[i][cust[j]]= float(row[j])
					print ('c[%d][%d] = %f' %(i, cust[j], c[i][cust[j]]))
~~~
Now, read the extra.csv files to save the values of u, f, and v. Each of these values are stored in column vectors. u is found in column 1 (after skipping column 0). f is in column 2 and v is in column 3. 
~~~
with open('dataset1/extra.csv', 'r') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in spamreader:
		if (row[0][0] != '%'):		
			i = int(row[0])
			u[i] = float(row[1])
			f[i] = float(row[2])
			v[i] = float(row[3])
~~~
The demand.csv file contains the values of each customers' demand in a row vector. 
~~~
with open('dataset1/demand.csv', 'r') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
	for row in spamreader:
		if (row[0][0] != '%'):
			for i in range(0,len(row)):
				d[C[i]] = float(row[i])
~~~
### Objective Function
---
The objective function is solved to obtain the optimal value of the problem. It is an expression that combines Decision Variables and Parameters that impact the value of the Objective Function. This expression typically represents the total cost of the project, or the benefits received as a result of solving the problem. The goal will be to minimize the objective function if the expression represents a total cost, or the maximize the objective function if the expression represents the value or benefit of a project.

- For the problems that I have studied, the objective functions are fairly simple so they are handled within each Decision Variable.

We will need to tell the code whether to find the minimum or maximum solution. When solving for an optimal solution, the program may run for a long time. Setting a time limit will cancel the run if the solution is too complex to find in a reasonable amount of time.
~~~
#Name the model

#minimize the cost of building warehouses, and fulfilling demand to all customers
m = Model('facility_location')
m.ModelSense = GRB.MINIMIZE


m.Params.TimeLimit = maxTime
~~~

### Decision Variables
---
Decision Variables represent the choices being made, and they are the items whose values are being solved in the Objective Function. DV's can be continuous, integers, or binary values. It answers the questions "how much should be allocated" or "which option is best"?

- Examples of DV's: Which warehouse location should we choose? How much inventory will we send to each client? Which worker should be assigned to job A?


####How to set the DVs:
First, name the decision variable. The formula utilizes y[i] to represent the binary decision of whether a warehouse is located at site i or not. Since the variable has several indices it should be initialized as a dictionary.

Create a "for loop" over all possible warehouse locations to create y[i] for all possible i warehouses.
~~~
decvary = defaultdict(make_dict)
for i in W:
	decvary[i] = m.addVar(lb=0, ub=1, vtype=GRB.BINARY, obj= f[i], name="y.%d"%(i))
~~~
The command m.addVar denotes decvary[i] as a variable. lb represents the lower bound and ub represents the upper bount for the value of y. In this case the variable is binary and can only take the value of 0 or 1. 

The decision variable y[i] is dependent on the parameter f[i] therefore obj = f[i] tells us that the objective function contains the term f[i]*y[i]. The objective of y is minimize the fixed costs f[i] to build warehouse i.

Finally, each variable in the dictionary will be named y.%d and the %d is replaced in each iteration with the appropriate warehouse number i, as denoted by the for loop.

This problem also requires the continuous variable z[i] to determine the size of the warehouse that is built where the upperbound is the maximum capacity determined by the parameter u[i]. The objective is to minimize the variable cost per volume of the warehouse.

~~~
decvarz = defaultdict(make_dict)

for i in W:
	decvarz[i] = m.addVar(lb=0, ub=u[i], vtype=GRB.CONTINUOUS, obj=v[i], name="z.%d"%(i))	
~~~

The DV x[i][j] represents the amount of product that is shipped from warehouse i to customer j. The upper bound is the maximum amount of product that could be shipped which is the demand requested by the customer. The objective is to minimize the cost of shipping c[i][j] from warehouse i to customer j.

~~~
decvarx = defaultdict(make_dict)

for i in W:
	for j in C:
		decvarx[i][j] = m.addVar(lb=0, ub=d[j], vtype=GRB.CONTINUOUS, obj= c[i][j], name="x.%d.%d"%(i,j))  
~~~

###Constraints
---
The Objective Function helps to solve for the individual values of the Decision Variables subject to a list of constraints. Constraints are equations that restrict the values that the DV's can take. The equations are comprised of a combination of parameters and constraints, and create an upper or lower bound in the problem using an inequality such as <=, >=, <, or >.

- Examples of Constraints: The weight of all books in a knapsack must be less than or equal to the capacity. The total amount of product shipped to all customers must be less than or equal to the total supply in the warehouse.


The first constraint in the facility problem is that all of the product shipped from warehouse i to customer j must meet the customer's demand. The for loop creates a demand equation for each customer j. Inside the loop, we must sum the amount shipped from each warehouse to customer j and the total amount shipped must be equal to the customer's demand.
~~~
# Meet all demand
for j in C:
	m.addConstr(quicksum(decvarx[i][j] for i in M) == d[j], "Constr.1.%d" % (j))
	g.append(1)
~~~
Next, the total amount shipped from each warehouse cannot be greater than the actualsize of the warehouse. The for loop creates an equation for the capacity of each warehouse. Each equation sums the total amount shipped from warehouse i to all j customers and makes sure that it does not exceed the total capacity of warehouse i.
~~~
# Supply must not exceed size of warehouse
for i in W:
	m.addConstr(quicksum(decvarx[i][j] for j in N)<= decvarz[i], "Constr.2.%d" %(i))
	g.append(2)
~~~
Finally, there is a constraint on the size of the warehouse that can be built. For each warehouse, the size of the warehouse that is build z[i] cannot exceed the maximum capacity u[i] of warehouse i if it is in fact built y[i].
~~~
# size of warehouse is less than max capacity of site i
for i in W:
	m.addConstr(decvarz[i] <= (u[i]*decvary[i]), "Constr.3.%d" %(i))
	g.append(3)
~~~

# Output
###Optimal Formulation
---
If we wish to find the optimal solution, the command m.optimize() finds the optimal solution for the model. Then, we want the actual values of the objective function and all of the decision variables to print out to the terminal so we have the solution.

Some formulations are infeasible or unbounded therefore we will print a statement to the terminal expressing if this is the case. 

~~~
m.update()
m.optimize() 


# from http://www.gurobi.com/documentation/8.1/examples/workforce1_py.html
m.optimize()
status = m.status
if status == GRB.Status.UNBOUNDED:
	print('The model cannot be solved because it is unbounded')
	exit(0)
~~~

In the event that a solution can be found, the values will be printed.
First, loop over all warehouses. IF the value of y[i] is greater than 0, then warehouse i should be build. The statement "Build a warehouse at location i" will print to the terminal and the warehouse number will replace the letter i. The warehouse will also have a positive value size. The statement "The size of warehouse 'i' is 'z'" will print and the warehouse number, and capacity will replace i and z. 

Then loop over all warehouses and customers to determine the amount of product shipped from one to the other. If a positive quantity of x[i][j] is shipped,the terminal will display "Warehouse 'i' will shipp 'x[i][j]' units to customer 'j'" with the appropriate values replacing the variables.

Having printed output is important to make sure that a person can actually implement the solution to problems in real life.
~~~
if status == GRB.Status.OPTIMAL:
	print('The optimal objective is %g' % m.objVal)
	
	for i in W:
		if decvary[i].x >= 0.0001:
			print ('Build a warehouse at location %d' %(i))
			#print decvary[i].x
		if decvarz[i].x >= 0.0001:
			print ('The size of warehouse %d is %f' %(i, decvarz[i].x))
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

~~~
###General Formulation
The following code is needed to create the graphical displays.
~~~

# =================================================================
# Call our package to generate our required information:
m.update()
common.generateOutput(m, g, dprime, n, args["folder"], args["label"], bool(args["displayImages"]))
# =================================================================

~~~
The displays appear as popups and look similar to this.
![](/home/student/Projects/gurobipy/generaloutput.PNG) 


#References
Hurkens, Cor. “The Knapsack Problem.” Eindhoven University of Technology, 23 July 1999, www.win.tue.nl/~wscor/OW/2V300/H4.pdf.

Jensen, Paul A., and Jonathan F. Bard. Operations Research: Models and Methods. John Wiley & Sons, Inc., 2003.
