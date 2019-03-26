There are m potential warehouse locations and n customers.
Each location will have a unique capacity, fixed (building costs) and variable (cost to increase facility size by one unit) costs, 
and shipping costs to the respective customer locations.
Select facility location(s) that minimizes the costs of shipping to all customers and building the facility, while meeting demand, and not exceeding the maximum capacity.

-----------------------------------------------------------------------------

To run this code, enter the directory where the facility_location.py script is located.

Copy and paste the following line into the terminal. Replace "-m 5" with the actual number of warehouses and "-n 5" with the actual number of customers for the problem.

python facility_location.py -m 5 -n 5 -f facility_location -l facility_location -d 1
