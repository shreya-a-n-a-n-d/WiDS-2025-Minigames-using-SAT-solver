"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    cnf = CNF()

    """
    Premise: Creating a CNF where each literal is ijn, where i, j are the coordinates of the cell we're filling and n is the number 
    we want to indicate for that cell, e.g. (111 or 112 or ... 119) and (-11n') for all n' in the corresponding row, column and box. 
    Also, for each box, only 1 possible number => (-111 or -112) and (-111 or -113) ... and (-118 or -119).
    If already filled with a number m, => add a unit literal clause (ijm) to the CNF.
    Also to make sure that no number repeats, we can add (-ija or -ika) clauses, (-ija or -kja) clauses, and then for the boxes too.
    """

    # Numbers already in grid + one number per grid rule
    
    for i in range(1, len(grid)+1):
        for j in range(1, len(grid[i-1])+1):
            if(grid[i-1][j-1]):
                cnf.append([i*100 + j*10 + grid[i-1][j-1]])
            else:
                cnf.append([i*100 + j*10 + 1, i*100 + j*10 + 2, i*100 + j*10 + 3, i*100 + j*10 + 4, i*100 + j*10 + 5, i*100 + j*10 + 6, i*100 + j*10 + 7, i*100 + j*10 + 8, i*100 + j*10 + 9])
                for p in range(1, 10):
                    for q in range(p+1, 10):
                        cnf.append([-1*(i*100 + j*10 + p), -1*(i*100 + j*10 + q)])
    
    # Rows and columns general rules
    
    for i in range(1, len(grid)+1):
        for j in range(1, len(grid[i-1])+1):
            for k in range(1, len(grid[i-1])+1):
                for p in range(1, 10):
                    if(j!=k):
                        cnf.append([-1*(i*100 + j*10 + p), -1*(i*100 + k*10 + p)])
                    if(i!=k):
                        cnf.append([-1*(i*100 + j*10 + p), -1*(k*100 + j*10 + p)])

    # Boxes rule

    for i in range(0, 3):
        for j in range(0, 3): 
            for l in range(i*3+1, i*3 + 4):
                for k in range(j*3+1, j*3 + 4):
                    for m in range(i*3+1, i*3 + 4):
                        for n in range(j*3+1, j*3 + 4):
                            for p in range(1, 10):
                                if(10*l + k != 10*m + n):
                                    cnf.append([-1*(l*100 + k*10 + p), -1*(m*100 + n*10 + p)])

                        
    # dpll(cnf) (using my own dpll algorithm)
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if not solver.solve():
            print("UNSAT")
            return None
        model = solver.get_model()

    solution = [[0]*9 for _ in range(9)]
    for lit in model:
        if lit > 0:
            i = (lit // 100) - 1
            j = (lit % 100) // 10 - 1
            p = lit % 10
            solution[i][j] = p

    return solution
