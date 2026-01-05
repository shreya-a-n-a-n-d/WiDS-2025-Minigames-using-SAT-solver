def dpll(cnf, assignment={}):
    if not cnf:
        return assignment # Assignment works as a potential solution, SAT
        
    if any(len(clause) == 0 for clause in cnf):
        return None # A clause is completely empty => UNSAT

    for clause in cnf:
        if len(clause) == 1: # Checking unit literal clauses
            literal = clause[0]
            return dpll(simplify(cnf, literal), {**assignment, abs(literal): literal > 0}) # Creates a new dictionary that is a copy of assignment, + a new assignment

    literals = {lit for clause in cnf for lit in clause}
    for lit in literals:
        if -lit not in literals: # Checking pure literal clauses
            return dpll(simplify(cnf, lit), {**assignment, abs(lit): lit > 0})

    literal = cnf[0][0] # Random literal branching

    result = dpll(simplify(cnf, literal), {**assignment, abs(literal): literal > 0}) # Trying with literal = true
    
    if result is not None:
        return result # Yay it worked

    return dpll(simplify(cnf, -literal), {**assignment, abs(literal): literal < 0}) # Trying with literal = false

def simplify(cnf, literal):
    new_cnf = []
    for clause in cnf:
        if literal in clause:
            continue
        if -literal in clause:
            new_clause = [l for l in clause if l != -literal] # Ignoring the false literal in the clauses with it (based on our setting)
            new_cnf.append(new_clause) # Only counting the new clauses with -literal, removing -literal (aren't satisfied yet)
        else:
            new_cnf.append(clause) # Counting clauses without literal or -literal
    return new_cnf
