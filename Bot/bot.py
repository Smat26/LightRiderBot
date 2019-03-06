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

        for key, val in direction_moves.items():
            print key, "=>", val
        sys.stderr.write("directions\n")
        sys.stderr.write(str(value) + ' ')
        sys.stderr.write("\n")
        sys.stderr.flush()
        updated_cell = self.game.field.get_cell_given_direction(self.game.field.cell, value, self.game.my_player())
        self.game.field.smell_trap(self.game.my_botid, self.game.other_botid, self.game.players, enemy=None, future_cell=updated_cell, moves=0)


        self.game.issue_order(value)

        # legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
        # if len(legal) == 0:
        #     self.game.issue_order_pass()
        # else:
        #     (_, chosen) = random.choice(legal)
        #     self.game.issue_order(chosen)
