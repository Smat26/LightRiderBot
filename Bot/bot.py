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
        # self.game.issue_order(self.directions.pop(0))

        legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
        if len(legal) == 0:
            self.game.issue_order_pass()
        else:
            (_, chosen) = random.choice(legal)
            self.game.issue_order(chosen)
