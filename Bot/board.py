import copy
import sys
from . import player

PLAYER1, PLAYER2, EMPTY, BLOCKED = [0, 1, 2, 3]
S_PLAYER1, S_PLAYER2, S_EMPTY, S_BLOCKED, = ['0', '1', '.', 'x']

CHARTABLE = [(PLAYER1, S_PLAYER1), (PLAYER2, S_PLAYER2), (EMPTY, S_EMPTY), (BLOCKED, S_BLOCKED)]

DIRS = [
    ((-1, 0), "up"),
    ((0, 1), "right"),
    ((1, 0), "down"),
    ((0, -1), "left")
]


class Board:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell = [[[EMPTY] for col in range(0, width)] for row in range(0, height)]

    def parse_cell_char(self, players, row, col, char):
        result = -1
        if char == S_PLAYER1:
            players[0].row = row;
            players[0].col = col;
        elif char == S_PLAYER2:
            players[1].row = row;
            players[1].col = col;
        for (i, symbol) in CHARTABLE:
            if symbol == char:
                result = i
                break
        return result

    def parse_cell(self, players, row, col, data):
        cell = []
        for char in data:
            item = self.parse_cell_char(players, row, col, char)
            cell.append(item)
        return cell

    def parse(self, players, data):
        cells = data.split(',')
        col = 0
        row = 0
        for cell in cells:
            if (col >= self.width):
                col = 0
                row += 1
            self.cell[row][col] = self.parse_cell(players, row, col, cell)
            col += 1

    def in_bounds(self, row, col):
        return row >= 0 and col >= 0 and col < self.width and row < self.height

    def is_legal(self, row, col, my_id):
        enemy_id = my_id ^ 1
        return (self.in_bounds(row, col)) and (not BLOCKED in self.cell[row][col]) and (not enemy_id in self.cell[row][col])

    def is_legal_tuple(self, loc):
        row, col = loc
        return self.is_legal(row, col)

    def get_adjacent(self, row, col):
        result = []
        for (o_row, o_col), _ in DIRS:
            t_row, t_col = o_row + row, o_col + col
            if self.is_legal(t_row, t_col):
                result.append((t_row, t_col))
        return result

    def legal_moves(self, my_id, players):
        my_player = players[my_id]
        result = []
        for ((o_row, o_col), order) in DIRS:
            t_row = my_player.row + o_row
            t_col = my_player.col + o_col
            if self.is_legal(t_row, t_col, my_id):
                result.append(((o_row, o_col), order))
            else:
                pass
        return result

    def is_legal2(self, row, col, my_id,cell):
        enemy_id = my_id ^ 1
        return (self.in_bounds(row, col)) and (not BLOCKED in cell[row][col]) and (not enemy_id in cell[row][col])

    def legal_moves2(self, my_id, players,cell,direction):
        my_player = players[my_id]
        row,col = self.get_coordinate_given_direction(direction,my_player.row,my_player.col)
        result = []
        for ((o_row, o_col), order) in DIRS:
            t_row = row + o_row
            t_col = col + o_col
            if self.is_legal2(t_row, t_col, my_id,cell):
                result.append(((o_row, o_col), order))
            else:
                pass
        return result

    def leak_fix2(self, enemy_id, my_id, players, enemy=None, future_cell=None, moves=0, direction=None):
        '''
        Returns:
            enemy position, after M moves, and whether it's trapped, and cell at that time.
        '''
        if not enemy:
            enemy = players[enemy_id]
            my_id = enemy_id ^ 1

        if direction:
            row, col = self.get_coordinate_given_direction(direction, enemy.row, enemy.col)


        if not future_cell:
            future_cell = copy.deepcopy(self.cell)
        enemy_legal_moves = self.legal_moves2( enemy_id,players, future_cell,direction)
        if len(enemy_legal_moves) == 1:
            # self.output()
            if row >= self.height:
                row = self.height-1
            elif row < 0:
                row = 0
            if col >= self.width:
                col = self.width-1
            elif col < 0:
                col = 0

            future_cell[row][col] = [BLOCKED]  # Putting a blocked symbol on current head
            row = int(enemy_legal_moves[0][0][0]) + row
            col = int(enemy_legal_moves[0][0][1]) + col
            future_cell[row][col] = [enemy_id]  # Putting the head on the future move
            moves = moves + 1
            enemy = player.Player()
            enemy.row = row
            enemy.col = col
            return self.leak_fix(enemy_id, my_id, players, enemy, future_cell, moves)
        elif len(enemy_legal_moves) == 0:
            sys.stderr.write("Enemy trapped dies in %s moves\n" % str(moves))
            sys.stderr.flush()
            return enemy, moves, True, future_cell
        else:
            # returns enemy position and moves to get there
            sys.stderr.write("Enemy will be trapped for %s moves\n" % str(moves))
            sys.stderr.flush()
            return enemy, moves, False, future_cell


    def output_cell(self, cell):
        done = False
        for (i, symbol) in CHARTABLE:
            if i in cell:
                if not done:
                    sys.stderr.write(symbol)
                done = True
                break
        if not done:
            sys.stderr.write("!")
            done = True

    def output(self):
        for row in self.cell:
            sys.stderr.write("\n")
            for cell in row:
                self.output_cell(cell)
        sys.stderr.write("\n")
        sys.stderr.flush()

    # ===========================#
    # === STRATEGY: LEAK-FIX === #
    # ========================== #

    def is_future_legal(self, row, col, cell, my_id):
        '''
        my_id is used, because I am my enemy's enemy

        '''
        return (self.in_bounds(row, col)) and (not BLOCKED in cell[row][col]) and (not my_id in cell[row][col])

    def future_legal_moves(self, enemy, cell, my_id):
        '''
        Different than legal_moves because of added param of id, enemy and cell
        '''
        result = []
        for ((o_row, o_col), order) in DIRS:
            t_row = enemy.row + o_row
            t_col = enemy.col + o_col
            if self.is_future_legal(t_row, t_col, cell, my_id):
                result.append(((o_row, o_col), order))
            else:
                pass
        return result

    def leak_fix(self, enemy_id, my_id, players, enemy=None, future_cell=None, moves=0):
        '''
        Returns:
            enemy position, after M moves, and whether it's trapped, and cell at that time.
        '''
        if not enemy:
            enemy = players[enemy_id]
            my_id = enemy_id ^ 1

        if not future_cell:
            future_cell = copy.deepcopy(self.cell)
        enemy_legal_moves = self.future_legal_moves(enemy, future_cell, my_id)
        if len(enemy_legal_moves) == 1:
            # self.output()
            future_cell[enemy.row][enemy.col] = [BLOCKED]  # Putting a blocked symbol on current head
            enemy.row = int(enemy_legal_moves[0][0][0]) + enemy.row
            enemy.col = int(enemy_legal_moves[0][0][1]) + enemy.col
            future_cell[enemy.row][enemy.col] = [enemy_id]  # Putting the head on the future move
            moves = moves + 1
            return self.leak_fix(enemy_id, my_id, players, enemy, future_cell, moves)
        elif len(enemy_legal_moves) == 0:
            sys.stderr.write("Enemy trapped dies in %s moves\n" % str(moves))
            sys.stderr.flush()
            return enemy, moves, True, future_cell
        else:
            # returns enemy position and moves to get there
            sys.stderr.write("Enemy will be trapped for %s moves\n" % str(moves))
            sys.stderr.flush()
            return enemy, moves, False, future_cell

    # ===========================#
    # === STRATEGY: Dijkstra === #
    # ========================== #

    def calculate_path(self, row, col, cell):
        '''
        :return:
        Array of actions to be taken to reach teh target,
        False if unreachable
        '''
        cost = cell[row][col]
        directions = []
        last_cost = 9999
        while cost > 0:
            if last_cost == cost:
                return False
            last_cost = cost
            # for rowz in cell:
            #     sys.stderr.write("\n")
            #     for cel in rowz:
            #         sys.stderr.write(str(cel)+ ' ')
            # sys.stderr.write("\n")
            # sys.stderr.flush()

            for value in [1, -1]:
                if row == 0 and value == -1:
                    continue
                elif row == 15 and value == 1:
                    continue
                if cell[row + value][col] < cost:
                    if value == 1:
                        direction = 'up'
                    else:
                        direction = 'down'
                    directions.append(direction)
                    cost = cell[row + value][col]
                    row = row + value
                    break
            # For Col
            for value in [1, -1]:
                if col == 0 and value == -1:
                    continue
                elif col == 15 and value == 1:
                    continue
                if cell[row][col + value] < cost:
                    if value == 1:
                        direction = 'left'
                    else:
                        direction = 'right'
                    directions.append(direction)
                    cost = cell[row][col + value]
                    col = col + value
                    break
        return directions

    def dijkstra_update_around(self, row, col, cell):
        updated = []
        # For row
        for value in [1, -1]:
            if row == 0 and value == -1:
                continue
            elif row == 15 and value == 1:
                continue
            # sys.stderr.write("ROW:%s, COL:%s, VAL:%s \n" % (str(row), str(col), str(value)))
            # sys.stderr.flush()
            if BLOCKED != cell[row + value][col]:
                cell[row + value][col] = min(cell[row + value][col], cell[row][col] + 1)
                updated.append((row + value, col))
        # For Col
        for value in [1, -1]:
            if col == 0 and value == -1:
                continue
            elif col == 15 and value == 1:
                continue
            if BLOCKED != cell[row][col + value]:
                cell[row][col + value] = min(cell[row][col + value], cell[row][col] + 1)
                updated.append((row, col + value))
        return updated, cell

    def flood_fill_update_around(self, row, col, cell):
        updated = []
        # For row
        for value in [1, -1]:
            if row <= 0 and value == -1:
                continue
            elif row >= 15 and value == 1:
                continue
            if BLOCKED not in cell[row + value][col]:
                cell[row + value][col] = ['I']
                if row + value <= 15 and row+value >= 0:
                    updated.append((row +value, col))
        # For Col
        for value in [1, -1]:
            if col <= 0 and value == -1:
                continue
            elif col >= 15 and value == 1:
                continue
            if BLOCKED not in cell[row][col + value]:
                cell[row][col + value] = ['I']
                if col + value <= 15 and col+value >= 0:
                    updated.append((row , col+ value))

        return updated, cell

    def initialize_cell(self, cell):
        initialized_cell = [[item if item == '' else 99999 for item in row] for row in cell]
        return initialized_cell

    def dijkstra_path(self, dest_row, dest_col, cell, start_row=None, start_col=None, my_id=None, players=None):
        '''
        Return Moves and path

        '''
        cell = self.initialize_cell(cell)
        if not start_row or not start_col:
            start_row = players[my_id].row
            start_col = players[my_id].col
        cell[start_row][start_col] = 0
        frontier, cell = self.dijkstra_update_around(start_row, start_col, cell)
        sys.stderr.flush()
        while frontier and (dest_row, dest_col) not in frontier:
            new_frontier = set()
            for position in frontier:
                temp_frontier, cell = self.dijkstra_update_around(position[0], position[1], cell)
                for front in temp_frontier:
                    new_frontier.add(front)
            frontier = list(new_frontier)
        moves = cell[dest_row][dest_col]
        sys.stderr.write("Moves required by djisktra %s \n" % str(moves))
        sys.stderr.flush()
        # for row in cell:
        #     sys.stderr.write("\n")
        #     for cel in row:
        #         sys.stderr.write(str(cel) + ' ')
        # sys.stderr.write("\n")
        # sys.stderr.flush()
        directions = self.calculate_path(dest_row, dest_col, cell)
        return moves, directions

    # ===========================#
    # == STRATEGY: Smell-Trap == #
    # ========================== #

    def smell_trap(self, enemy_id, my_id, players, enemy=None, future_cell=None, moves=0):
        return self.leak_fix(my_id, enemy_id, players, enemy=None, future_cell=None, moves=0)

    def calculate_remaining_movable_area(self, player_id, players):
        my_position = players[player_id]
        up = 0
        down = 0
        right = 0
        left = 0
        allFalse = False

        while not allFalse:
            allFalse = True
            if self.is_legal(my_position.row + down + 1, my_position.col, player_id):
                allFalse = False
                down += 1
            if self.is_legal(my_position.row, my_position.col + right + 1, player_id):
                allFalse = False
                right += 1
            if self.is_legal(my_position.row - up - 1, my_position.col, player_id):
                allFalse = False
                up += 1
            if self.is_legal(my_position.row, my_position.col - left - 1, player_id):
                allFalse = False
                left += 1

        sys.stderr.write('(' + str(up) + "," + str(down) + "," + str(right) + "," + str(left) + ") <-up, down, right, left\n")
        sys.stderr.write("\n")
        sys.stderr.flush()
        return {'up':up, 'down':down, 'right':right, 'left':left}

    def flood_fill(self, players, my_id, start_row=None, start_col=None, cell=None):
        if not cell:
            cell = copy.deepcopy(self.cell)
        # cell = self.initialize_cell(cell)
        if not start_row or not start_col:
            start_row = players[my_id].row
            start_col = players[my_id].col
        cell[start_row][start_col] = ['I']
        frontier, cell = self.flood_fill_update_around(start_row, start_col, cell)
        discovered = set()
        while frontier:
            new_frontier = set()
            for position in frontier:
                temp_frontier, cell = self.flood_fill_update_around(position[0], position[1], cell)
                for front in temp_frontier:
                    new_frontier.add(front)
                    discovered.add(front)
            frontier = list(new_frontier)
        return len(discovered)


    def get_cell_given_direction(self, cell, direction, player, player_id):
        updated = False;

        row = col = 0
        if direction == 'up':
            row = -1
        elif direction == 'down':
            row = 1
        elif direction == 'right':
            col = 1
        elif direction == 'left':
            col = -1
        cell[player.row][player.col] = [BLOCKED]  # Putting a blocked symbol on current head
        if self.is_legal(player.row+row, player.col+col, player_id):
            cell[player.row+row][player.col+col] = [player_id]  # Putting player ID symbol on future head
            updated = True

        return cell, updated

    def get_coordinate_given_direction(self, direction, row, col):

        if direction == 'up':
            row += -1
        elif direction == 'down':
            row += 1
        elif direction == 'right':
            col += 1
        elif direction == 'left':
            col += -1

        # if row >= self.height:
        #     row = self.height-1
        # elif row < 0:
        #     row = 0
        # if col >= self.width:
        #     col = self.width-1
        # elif col < 0:
        #     col = 0


        return row,col