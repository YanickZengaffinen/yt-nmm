import random

points = [
    (0, 6), (3, 6), (6, 6),
    (1, 5), (3, 5), (5, 5),
    (2, 4), (3, 4), (4, 4),
    (0, 3), (1, 3), (2, 3), (4, 3), (5, 3), (6, 3),
    (2, 2), (3, 2), (4, 2),
    (1, 1), (3, 1), (5, 1),
    (0, 0), (3, 0), (6, 0)
]

PIECES_PER_PLAYER = 9

EMPTY = 0
PLAYER_ONE = 1
PLAYER_TWO = -1

def opponent(player):
    if player == PLAYER_ONE:
        return PLAYER_TWO
    elif player == PLAYER_TWO:
        return PLAYER_ONE
    
    return None

PHASE_PLACING = -1
PHASE_NORMAL = 0
PHASE_WILD = 1

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = EMPTY

        cols = {
            0: (lambda y : [(0, 6), (0, 3), (0, 0)]),
            1: (lambda y : [(1, 5), (1, 3), (1, 1)]),
            2: (lambda y : [(2, 4), (2, 3), (2, 2)]),
            3: (lambda y : [(3, 2), (3, 1), (3, 0)] if y < 3 else [(3, 6), (3, 5), (3, 4)]),
            4: (lambda y : [(4, 4), (4, 3), (4, 2)]),
            5: (lambda y : [(5, 5), (5, 3), (5, 1)]),
            6: (lambda y : [(6, 6), (6, 3), (6, 0)])
        }

        rows = {
            0: (lambda x : [(6, 0), (3, 0), (0, 0)]),
            1: (lambda x : [(5, 1), (3, 1), (1, 1)]),
            2: (lambda x : [(4, 2), (3, 2), (2, 2)]),
            3: (lambda x : [(2, 3), (1, 3), (0, 3)] if x < 3 else [(6, 3), (5, 3), (4, 3)]),
            4: (lambda x : [(4, 4), (3, 4), (2, 4)]),
            5: (lambda x : [(5, 5), (3, 5), (1, 5)]),
            6: (lambda x : [(6, 6), (3, 6), (0, 6)])
        }

        self.col = cols[x](y)
        self.row = rows[y](x)

        self.value = EMPTY

class Board():
    def __init__(self) -> None:
        self._point_states = { f: Point(f[0], f[1]) for f in points }

    def value(self, point):
        return self._point_states[point].value

    def put(self, point, player):
        self._point_states[point].value = player
    
    def remove(self, point):
        self._point_states[point].value = EMPTY

    def move(self, from_point, to_point):
        self._point_states[to_point].value = self._point_states[from_point].value
        self._point_states[from_point].value = EMPTY
    
    def pieces(self, player):
        return [(ps.x, ps.y) for ps in self._point_states.values() if ps.value == player]
    
    def empty(self):
        return [(ps.x, ps.y) for ps in self._point_states.values() if ps.value == EMPTY]

    # check if a point is part of a mill
    def is_mill(self, point):
        point_value = self._point_states[point].value

        mill_cnt = 0
        # check if row is mill
        row = self._point_states[point].row
        if  self._point_states[row[0]].value == point_value and \
            self._point_states[row[1]].value == point_value and \
            self._point_states[row[2]].value == point_value:
            mill_cnt += 1
        
        # check if col is mill
        col = self._point_states[point].col
        if  self._point_states[col[0]].value == point_value and \
            self._point_states[col[1]].value == point_value and \
            self._point_states[col[2]].value == point_value:
            mill_cnt += 1
        
        return mill_cnt

    # check if there is a piece between the start and target or on the target itself
    def move_unobstructed(self, start, target):
        if self._point_states[target].value != EMPTY: return False # target state must be empty
        
        # state between start and target must be empty
        sx,sy = start
        ex,ey = target

        if sx == ex: # move on column
            # if moving 2 points => middle one must be empty
            col = self._point_states[start].col
            mx,my = col[1]
            if (sy != my and ey != my) and self._point_states[col[1]].value != EMPTY: return False
        elif sy == ey: # move on row
            # if moving 2 points => middle one must be empty
            row = self._point_states[start].row
            mx,my = row[1]
            if (sx != mx and ex != mx) and self._point_states[row[1]].value != EMPTY: return False

        return True
    
    # get all possible moves for the piece on the specified point
    def possible_moves(self, point):
        moves = []

        x,y = point
        piece = self._point_states[point]
        row = piece.row
        for p in row:
            px,py = p
            if p == point: continue # must move
            if self._point_states[p].value != EMPTY: continue # target must be empty
            mx,my = row[1]
            if (x != mx and px != mx) and self._point_states[row[1]].value != EMPTY: continue # if moving 2 points => middle one must be empty
            moves.append(p)

        col = piece.col
        for p in col:
            px,py = p
            if p == point: continue # must move
            if self._point_states[p].value != EMPTY: continue # target must be empty
            mx,my = col[1]
            if (y != my and py != my) and self._point_states[col[1]].value != EMPTY: continue # if moving 2 points => middle one must be empty
            moves.append(p)

        return moves

    # check if all pieces of a player are part of a mill
    def all_mill(self, player):
        # TODO: make this more efficient
        for point in self._point_states:
            if self._point_states[point].value != player: continue

            if not self.is_mill(point): return False
        
        return True



class Game():
    def start(self):
        self.board = Board()
        self._phase = { PLAYER_ONE: PHASE_PLACING, PLAYER_TWO: PHASE_PLACING }
        self._pieces = { PLAYER_ONE: 0, PLAYER_TWO: 0 }
        self._placed = { PLAYER_ONE: 0, PLAYER_TWO: 0 }
        self._remove = 0
        self._turn = PLAYER_ONE if random.randint(0, 1) == 0 else PLAYER_TWO
    
    def try_put(self, point, player):
        # check if valid move
        if self._remove > 0: return False # can not place while expecting a piece to be removed
        if not self._turn == player: return False # can only play if it is his turn
        if not self._phase[player] == PHASE_PLACING: return False # can only place piece in first phase
        if not self._placed[player] < PIECES_PER_PLAYER: return False # can only place if has pieces left
        if not self.board.value(point) == EMPTY: return False # destination must be empty

        # update state
        self.board.put(point, player)
        self._placed[player] += 1
        self._pieces[player] += 1

        # check if last piece of placement
        if self._placed[player] == PIECES_PER_PLAYER:
            self._phase[player] = PHASE_NORMAL if self._pieces[player] > 3 else PHASE_WILD
        
        # check if mill
        self._remove = self.board.is_mill(point) # set the amount of pieces that can be removed to the amount of mills, the new piece is part of
        if not self._remove: # if no mill then end turn
            self._switch_turns()

        return True
    
    def try_remove(self, point):
        # check if valid move
        if not self._remove > 0: return False # must be expecting a piece to be removed

        point_value = self.board.value(point)
        if point_value == EMPTY: return False # must have piece on it
        if point_value != opponent(self._turn): return False # must be from other player

        if self.board.is_mill(point) and not self.board.all_mill(opponent(self._turn)):
            return False # can only be part of a mill if all points are part of mills
        
        # update state
        self.board.remove(point)
        self._pieces[point_value] -= 1
        self._remove -= 1

        # check if game is won
        pieces_left = PIECES_PER_PLAYER - self._placed[point_value] + self._pieces[point_value]
        if pieces_left < 3:
            print("win")
        else:
            if pieces_left == 3:
                self._phase[opponent(self._turn)] = PHASE_WILD

            if self._remove == 0: # if not won and no more pieces to remove, then end turn
                self._switch_turns()
    
        return True


    def try_move(self, from_point, to_point):
        # check if valid move
        if self._phase[self._turn] == PHASE_PLACING: return False # cannot move during placing phase
        if self.board.value(from_point) != self._turn: return False # only player whos turn it is can move
        if from_point == to_point: return False # must move
        
        if self._phase[self._turn] == PHASE_NORMAL:
            if not self.board.move_unobstructed(from_point, to_point): return False # cannot move over or onto other pieces
            if from_point[0] != to_point[0] and from_point[1] != to_point[1]: return False # must move either on column or on row
        elif self._phase[self._turn] == PHASE_WILD:
            if self.board.value(to_point) != EMPTY: return False # target point must be empty

        # update state
        self.board.move(from_point, to_point)
        
        # check if mill
        self._remove = self.board.is_mill(to_point) # set the amount of pieces that can be removed to the amount of mills, the moved piece is part of
        if not self._remove: # if no mill then end turn
            self._switch_turns()

        return True

    def _switch_turns(self):
        self._turn = opponent(self._turn)

        possible_moves = self.possible_moves(self._turn)
        can_move = True
        if isinstance(possible_moves, list):
            can_move = len(possible_moves) > 0
        elif isinstance(possible_moves, dict):
            can_move = any([len(possible_moves[p]) > 0 for p in possible_moves])
        else:
            can_move = False
        
        # if the player cannot move then skip his turn
        if not can_move:
            self._switch_turns()

    def possible_moves(self, player):
        # if self._turn != player: return [] # cannot move if its not your turn

        if self._remove > 0:
            # return all the opponents pieces
            return self.board.pieces(opponent(player)) 
        
        phase = self.phase(player)
        if phase == PHASE_PLACING:
            # return all empty points
            return self.board.empty()
        
        if phase == PHASE_NORMAL:
            # return all possible moves for all pieces
            return { p: self.board.possible_moves(p) for p in self.board.pieces(player) }

        if phase == PHASE_WILD:
            # return all 3 pieces x all empty points
            empty = self.board.empty()
            return { p: empty for p in self.board.pieces(player) } 

        return None

    # get the player whos turn it is
    @property
    def turn(self):
        return self._turn

    # get the phase a player is in
    def phase(self, player):
        return self._phase[player]

    # amount of pieces to be placed by a player
    def to_place(self, player):
        return 9 - self._placed[player]

    # amount of pieces expected to be removed
    @property
    def remove(self):
        return self._remove

        



    
    

    
