import random
import sys

class Bot:

    def __init__(self):
        self.game = None

    def setup(self, game):
        self.game = game

    def do_turn(self):

        # Dijkstra_Usage
        # moves, directions = self.game.field.dijkstra_path(dest_row=0, dest_col=0, cell=self.game.field.cell,
        #                                                   my_id=self.game.my_botid, players=self.game.players)
        # self.game.issue_order(directions.pop(0))

        #Flood_fill Use
        direction_moves = self.game.field.calculate_remaining_movable_area(player_id=self.game.my_botid, players=self.game.players)
        value = max(direction_moves.iterkeys(), key=(lambda key: direction_moves[key]))

        sys.stderr.write("GAME ROUND: %s \n" % self.game.round)
        sys.stderr.flush()
        updated_cell = self.game.field.get_cell_given_direction(self.game.field.cell, value, self.game.my_player())
        enemy, moves, trapped, future_cell = self.game.field.smell_trap(self.game.my_botid, self.game.other_botid, self.game.players, enemy=None, future_cell=updated_cell, moves=0)
        if moves:
            sys.stderr.write("MOVE: %s\n" % moves)
            sys.stderr.write("Is Trapped?: %s\n" % trapped)
            sys.stderr.write("END POS: %s,%s\n" % (str(enemy.row), str(enemy.col)))
            sys.stderr.flush()

        if value:
            self.game.issue_order(value)
        else:
            self.game.issue_order_pass()

        # legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
        # if len(legal) == 0:
        #     self.game.issue_order_pass()
        # else:
        #     (_, chosen) = random.choice(legal)
        #     self.game.issue_order(chosen)
