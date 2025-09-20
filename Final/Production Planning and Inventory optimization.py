# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 12:43:56 2023

@author: muham
"""

from gurobipy import GRB,Model,quicksum #*


def Output(m):  
    # Print the result
    status_code = {1:'LOADED', 2:'OPTIMAL', 3:'INFEASIBLE', 4:'INF_OR_UNBD', 5:'UNBOUNDED'} #this is how a 'dictionary' 
                                                                                            #is defined in Python
    status = m.status
    
    print('The optimization status is ' + status_code[status])
    if status == 2:    
        # Retrieve variables value
        print('Optimal solution:')
        for v in m.getVars():
            print(str(v.varName) + " = " + str(v.x))    
        print('Optimal objective value: ' + str(m.objVal) + "\n")
        
        
def ProdPlan(demand, prodsell,prodcost,holdingcost,transport,initinv,finalinv):
    
    # Create the model
    model = Model('ProdPlan')
    
    # Set parameters
    model.setParam('OutputFlag',True)
    
    T= len(demand)
    
    #Monthly maintainance 
    P = 40000
    # Add variables
    x = model.addVars(T, lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER, name=["x_"+str(t+1) for t in range (T)])     
    #I[0] = I_1, I[1] = I_2,...
    I = model.addVars(T, lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER, name=["I_"+str(t+1) for t in range (T)])     
    
    #minimize cost
    #model.setObjective( quicksum(prodsell[t]*x[t] for t in range (T)) - (quicksum( holdingcost[t]*I[t] for t in range (T))+ quicksum( prodcost[t]*x[t] for t in range (T)) + quicksum( transport[t]*x[t] for t in range (T)) + P), GRB.MAXIMIZE)    
    
    model.setObjective(quicksum(prodsell[t] * x[t] for t in range(T)) - (quicksum(holdingcost[t] * I[t] for t in range(T)) + quicksum(prodcost[t] * x[t] for t in range(T)) + quicksum( transport[t]*x[t] for t in range (T)) + P) ,GRB.MAXIMIZE)

    
    
    
    #I[-1] == initial inventory
    model.addConstr(initinv + x[0] == demand[0] + I[0] + 2000) #for period 1
    
    model.addConstrs(I[t-1] + x[t] == demand[t] + I[t] for t in range(1,T)) #periods 2...T
   
    model.addConstr(I[T-1] == finalinv)
    # Define a list of expressions to sum
    sum_exprs = [x[t] for t in range(T)]
    #Use quicksum to sum the expressions
    model.addConstr(quicksum(sum_exprs) <= 20000)

    # we are looking to push inventory hence we try getting more inventory in each period 
    #model.addConstrs(I[t+1]  => 2000 for t in range(1,T))

    #model.addConstrs(I[t] <= capacity  for t in range(1,T))
    
    model.optimize()
    
    Output(model)
    
    # print the LP file
    model.write('ProdPlan.lp')
    
    # print the sol file
    model.write('ProdPlan.sol')
    

#ProdPlanQ1(demand=[40,70,30,50], prodcost=[5,10,6,8],holdingcost=[1,1,1,1], initinv=10, finalinv=10)    
ProdPlan(demand=[3940, 3687 , 4848 , 4848], prodsell=[615,625,635,645], prodcost = [595,590,585,580],holdingcost=[1,1,1,1] ,transport = [3,3,3,3] , initinv=10000, finalinv=1000)  