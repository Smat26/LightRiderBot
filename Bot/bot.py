import random
import sys

class Bot:

    def __init__(self):
        self.game = None

    def setup(self, game):
        self.game = game
        self.directions = None

    def do_turn(self):
        # flood = self.game.field.flood_fill(players=self.game.players, my_id=self.game.my_botid)
        # sys.stderr.write(str(flood)+' <--Movable area is \n' )
        # sys.stderr.flush()
        if not self.directions:
            moves, directions = self.game.field.dijkstra_path(dest_row=0,dest_col=0,cell=self.game.field.cell,my_id=self.game.my_botid, players=self.game.players)
            self.directions = directions
        for direction in self.directions:
            sys.stderr.write(direction+'\n' )
        sys.stderr.write('===========\n' )
        sys.stderr.flush()
        self.game.issue_order(self.directions.pop(0))
