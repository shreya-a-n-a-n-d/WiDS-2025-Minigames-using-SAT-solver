"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.player_start = None

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()
        
        self.push_dir = {(-1, 0): 0, (1, 0): 1, (0, -1): 2, (0, 1): 3}

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        G = self.grid
        for i in range(len(G)):
            for j in range(len(G[i])):
                g = G[i][j]
                if g == 'P':
                    self.player_start = (i, j)
                    continue
                if g == 'G':
                    self.goals.append((i, j))
                    continue
                if g == 'B':
                    self.boxes.append((i, j))
                

    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        return (t * self.N * self.M + x * self.M + y + 1)
        

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        player_var_count = (self.T + 1) * self.N * self.M # Total possible values for var_player
        return ((1 + b) * player_var_count + t * self.N * self.M + x * self.M + y + 1) # 

    
    def var_push(self, b, sx, sy, dx, dy, t):
        # base offset beyond player+box ids
        base = (self.num_boxes + 1) * (self.T + 1) * self.N * self.M
        dir_index = self.push_dir[(dx, dy)] #this will give us a unique integer for every move
        # unique packing: keep linear form (expanded for clarity)
        return base + ( 4 * (t * self.num_boxes * self.N * self.M)
                        + 4 * b * self.N * self.M
                        + 4 * sx * self.M
                        + 4 * sy
                        + dir_index
                        + 1)
    # This above function encodes that a box b present at sx,sy at time t will shift to sx+dx, sy+dy at time t+1, since it has been pushed.

    
    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        # 2. Player movement
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints
        # 5. Goal conditionss
        # 6. Other conditions

        # Initial conditions
        
        t=self.T
        n=self.N
        m=self.M
        g=self.grid
        
        
        # * INITIALISATION
        
        # # to know where to start encode (x,y,0) time = 0
        self.cnf.append([self.var_player(self.player_start[0],self.player_start[1],0)])
        
        # # tell the solver where box must be when the game starts
        for i in range(self.num_boxes):
            x,y = self.boxes[i]
            self.cnf.append([self.var_box(i,x,y,0)])
            
            
        # * PLAYER CONSTRAINT
        
        # # player can only go to cells that are not '#'
        for i in range(0,t+1):
            positionsfort=[]
            for j in range(0,n):
                for k in range(0,m):
                    if (g[j][k]=='#') : 
                        continue
                    else : 
                        positionsfort.append(self.var_player(j,k,i))
            self.cnf.append(positionsfort)
            for c in range(len(positionsfort)):
                for q in range(c+1,len(positionsfort)):
                    self.cnf.append([-positionsfort[c],-positionsfort[q]])
                    # player will only be on one cell at time = t' 
                    # this will prevent player from disappearing and from going on any walls
                    
                    
                    
        # * BOX CONSTRAINTS

        # # box must be on exactly one cell at all times
        for w in range (self.num_boxes):

            for i in range(0,t+1):
                positionsfort=[]
                for j in range(0,n):
                    for k in range(0,m):
                        if (g[j][k]=='#'):
                            continue
                        else:
                            positionsfort.append(self.var_box(w,j,k,i)) #every box must be somewhere in the grid at time = t'
                self.cnf.append(positionsfort)
                for c in range(0,len(positionsfort)):
                    for q in range(c+1,len(positionsfort)):
                        self.cnf.append([-positionsfort[c],-positionsfort[q]])
                        # one box cannot appear at two cells simultaneously
                        
        # # each cell must have atmost one box at all times
                        
        for i in range(t+1):
            for j in range (n):
                for k in range (m):
                    if (g[j][k]=='#'):
                        continue
                    else:
                        for b in range(self.num_boxes):
                            for brem in range(b+1,self.num_boxes):
                                self.cnf.append([-self.var_box(b,j,k,i),-self.var_box(brem,j,k,i)])
                                # two boxes cannot appear on the same cell simultaneously
                        
        # * FINAL STATE
        
        # # each box must be on some goal cell
                        
        for i in range (self.num_boxes):
            boxatendcheck=[]
            for (p1,p2) in self.goals:
                boxatendcheck.append(self.var_box(i,p1,p2,t))
                # when time = T each box must be at any of the goals
                # ! this is safe because we've already encoded that no two boxes can be on the same cell so never on the same goal too 
            self.cnf.append(boxatendcheck)

        
        # * PREVENT BOX - PLAYER OVERLAP
                    
        for i in range (t+1):
            for j in range (n):
                for k in range (m):
                    if (g[j][k]=='#'):
                        continue
                    else :
                        for b in range(0,self.num_boxes):
                            self.cnf.append([-self.var_box(b,j,k,i),-self.var_player(j,k,i)])
                            # box and player cannot be on the same cell


        # TODO: Add constraints for:
        # 1. Initial conditions - DONE
        # 2. Player movement - DONE
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints - DONE
        # 5. Goal conditions - DONE
        # 6. Other conditions ?
        
        # * PLAYER MOVEMENT CONSTRAINT
        
        for tym in range(t) :
            for i in range(n):
                for j in range(m):
                    if g[i][j] == '#' :
                        continue
                    # psbl contains all possible moves for the player at current state
                    # it alr contains i,j because not moving is allowed
                    
                    psbl = [(i,j)]
                    
                    for dx,dy in DIRS.values():
                        x,y = i+dx, j+dy
                        if (x>=0 and x <n) and (y>=0 and y<m) and g[x][y]!='#' :
                            psbl.append((x,y))
                            
                    # to keep the player from teleporting we need to add a clause such that
                    # player(x,y,t) -> player (psbl,t)
                    cls = [-self.var_player(i,j,tym)]
                    cls += [self.var_player(x,y,tym+1) for x,y in psbl]
                    self.cnf.append(cls)
                    
                    
                    # !!!!!!! BACKWARD PENDING
                    clause = [-self.var_player(i, j, tym + 1)]
                    clause += [self.var_player(x, y, tym) for x, y in psbl]
                    self.cnf.append(clause)
                            
                            
            # back to time blocks
            for i in range(n):
                for j in range(m):
                    if g[i][j] == '#':
                        continue
                    for dx,dy in DIRS.values():
                        bx, by = i + dx, j + dy # at time t
                        nbx, nby = bx + dx, by + dy # at time t+!
                        # nbx is new bx if pushed
                        
                        if bx < 0 or nbx < 0 or bx >= n or nbx >= n or by < 0 or nby < 0 or by >= m or nby >= m :
                            continue
                        if g[bx][by]=='#' or g[nbx][nby]=='#':
                            continue
                        
                        for b in range(self.num_boxes):
                            push = self.var_push(b,bx,by,dx,dy,tym)
                            
                            # push => player was at (i,j) at time t
                            self.cnf.append([-push, self.var_player(i,j,tym)])
                            # push => box was at (i,j) at time t
                            self.cnf.append([-push, self.var_box(b,bx,by,tym)])
                            # push => player came to (bx,by) at time t+1
                            self.cnf.append([-push, self.var_player(bx,by,tym+1)])
                            # push => box moves to (nbx,nby) at time t+1 
                            self.cnf.append([-push, self.var_box(b,nbx,nby,tym+1)]) 
                            
                            
                            # ! converse                     
                            # c1 and c2 and c3 and c4 => push
                            self.cnf.append([
                                -self.var_player(i, j, tym),
                                -self.var_box(b, bx, by, tym),
                                -self.var_player(bx, by, tym + 1),
                                -self.var_box(b,nbx,nby,tym+1),
                                push
                            ])
                            
                            
            # prevent boxes from teleporting 
            for b in range(self.num_boxes):
                for i in range(n):
                    for j in range(m):
                        if g[i][j] == '#':
                            continue
                        push_vars = []
                        for dx, dy in DIRS.values():
                            x, y = i - dx, j - dy # box old pos
                            nx, ny = x - dx, y - dy # player old pos
                            if not (0 <= x < n and 0 <= y < m and 0 <= nx < n and 0 <= ny < m):
                                continue
                            if g[x][y] == '#' or g[nx][ny] == '#':
                                continue
                            push_vars.append(self.var_push(b, x, y, dx, dy, tym))

                        # either box stays at the same spot or moves while obeying constraints 
                        clause = [-self.var_box(b, i, j, tym + 1), self.var_box(b, i, j, tym)]
                        clause += push_vars
                        self.cnf.append(clause)
        
        return self.cnf


def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T

    # TODO: Map player positions at each timestep to movement directions
    N, M, T = encoder.N, encoder.M, encoder.T
    moves = []
    times = [None] * (T + 1)

    for v in model:
        if v <= 0:
            continue
        # only player variables
        if v <= (T + 1) * N * M:
            v0 = v - 1
            t, rem = divmod(v0, N * M)
            x, y = divmod(rem, M)
            times[t] = (x, y)
            

    for t in range(T):
        if times[t] is None or times[t + 1] is None:
            continue
        dx = times[t + 1][0] - times[t][0]
        dy = times[t + 1][1] - times[t][1]
        if (dx, dy) in DIRS.values():
            moves.append([k for k, v in DIRS.items() if v == (dx, dy)][0])

    return moves    


def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.

    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1

        return decode(model, encoder)
