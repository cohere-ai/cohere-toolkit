import sympy
import sympy.solvers

from sympy import Symbol

# Define the variables
v = Symbol("v")

# Define the equations
A = -29 * v + 2 * v
B = -13 * v + 98

# Solve the equations
soln = sympy.solvers.solve(A - B, v)
print(f"The solution to {A - B} is v = {soln}")
