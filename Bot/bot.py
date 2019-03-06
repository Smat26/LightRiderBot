import random
import sys

class Bot:

    def __init__(self):
        self.game = None
        self.killshot = False
        self.directions = []

    def setup(self, game):
        self.game = game
        self.killshot = False

    def do_turn(self):
        sys.stderr.write("GAME ROUND: %s \n" % self.game.round)
        sys.stderr.flush()

        # Are we Going for a kill?
        if self.killshot:
            self.game.issue_order(self.directions.pop(0))
            # Target has been eliminated
            if not directions:
                self.killshot = False

        # Can we go for a Kill?
        enemy, moves, trapped, future_cell = self.game.field.smell_trap(self.game.my_botid, self.game.other_botid, self.game.players, enemy=None, future_cell=self.game.field.cell, moves=0)
        if moves:
            sys.stderr.write("MOVE: %s\n" % moves)
            sys.stderr.write("Is Trapped?: %s\n" % trapped)
            sys.stderr.write("END POS: %s,%s\n" % (str(enemy.row), str(enemy.col)))
            sys.stderr.flush()

            # Dijkstra_Usage
            moves_to_reach, directions = self.game.field.dijkstra_path(dest_row=enemy.row, dest_col=enemy.col, cell=self.game.field.cell,
                                                              my_id=self.game.my_botid, players=self.game.players)
            for direction in directions:
                sys.stderr.write(" Djisktra output: %s \n" % direction)
            sys.stderr.flush()

            if moves_to_reach < moves:
                self.killshot = True
                self.directions = directions
                self.game.issue_order(self.directions.pop(0))
        
        # What are the legal moves we can make?
        legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
        trapped = []
        good_move = {}
        for move in legal:
            _, direction = move

            # Would this move trap us?
            my_pos, my_moves, my_trapped, my_future_cell = self.game.field.leak_fix( self.game.other_botid,self.game.my_botid, self.game.players, enemy=None, future_cell=self.game.field.cell, moves=0)
            if my_trapped:
                trapped.append(direction)
                continue

            # The map after we made that move:
            updated_cell = self.game.field.get_cell_given_direction(self.game.field.cell, direction, self.game.my_player())
            
            # What Moves we can make from this move?
            more_legal = self.game.field.future_legal_moves(self.game.players[self.game.my_botid], updated_cell,self.game.other_botid)
            for more_moves in more_legal:
                more_, more_direction = more_moves
                direction_moves = self.game.field.calculate_remaining_movable_area(player_id=self.game.my_botid, players=self.game.players)
                good_move[direction] = good_move.get(direction, 0) + sum(direction_moves.values())
        
        if good_move:
            maxval = max(good_move.values())
            direction = [k for k,v in good_move.items() if v==maxval][0]
            self.game.issue_order(direction)
        else:
            # Improvise trap comparison:
            self.game.issue_order(trapped[0])


        
        # my_pos, my_moves, my_trapped, my_future_cell = self.game.leak_fix( self.game.other_botid,self.game.my_botid, self.game.players, enemy=None, future_cell=self.game.field.cell, moves=0)
        #     if my_trapped:
        #         trapped.append(move)
        #         continue
        # safe_move.append(direction)
    


        
        #Flood_fill Use
        # area = self.game.field.flood_fill(players=self.game.players, my_id=self.game.my_botid, start_row=None, start_col=None, cell=None)


        # for direction in directions:
        #     sys.stderr.write("Djisktra output: %s \n" % direction)
        # sys.stderr.flush()
        # self.game.issue_order(directions.pop(0))
      
        # value = max(direction_moves.iterkeys(), key=(lambda key: direction_moves[key]))
           
        # if value:
        #     self.game.issue_order(value)
        # else:
        #     self.game.issue_order_pass()

        # legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
        # if len(legal) == 0:
        #     self.game.issue_order_pass()
        # else:
        #     (_, chosen) = random.choice(legal)
        #     self.game.issue_order(chosen)
