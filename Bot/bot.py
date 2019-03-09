import random
import sys


class Bot:

    def __init__(self):
        self.game = None
        self.killshot = False
        self.directions = []
        self.trapped_enemy = False
        self.converse_directions = [('up', 'down'), ('down', 'up'), ('right', 'left'), ('left', 'right')]

    def setup(self, game):
        self.game = game
        self.killshot = False

    def do_turn(self):
        sys.stderr.write("GAME ROUND: %s \n" % self.game.round)
        sys.stderr.flush()

        # Are we Going for a kill?
        if self.killshot and self.directions:
            next_move = self.directions.pop()
            row, col = self.game.field.get_coordinate_given_direction(next_move, self.game.my_player().row,
                                                                      self.game.my_player().col)
            if self.game.field.is_legal(row, col, self.game.my_botid):
                self.game.issue_order(next_move)
                # Target has been eliminated
                if not self.directions:
                    self.killshot = False
                    self.trapped_enemy = True

        # Is enemy trapped?
        if self.trapped_enemy:
            legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)

        # Can we go for a Kill?
        enemy, moves, trapped, future_cell = self.game.field.smell_trap(self.game.my_botid, self.game.other_botid,
                                                                        self.game.players, enemy=None,
                                                                        future_cell=self.game.field.cell, moves=0)
        if moves:
            sys.stderr.write("***** SMELL TRP *****")
            sys.stderr.write("MOVE: %s\n" % moves)
            sys.stderr.write("Is Trapped?: %s\n" % trapped)
            sys.stderr.write("END POS: %s,%s\n" % (str(enemy.row), str(enemy.col)))
            sys.stderr.flush()

        if not trapped and moves:

            # Dijkstra_Usage
            moves_to_reach, directions = self.game.field.dijkstra_path(dest_row=enemy.row, dest_col=enemy.col,
                                                                       cell=self.game.field.cell,
                                                                       my_id=self.game.my_botid,
                                                                       players=self.game.players)
            for direction in directions:
                sys.stderr.write(" Djisktra output: %s \n" % direction)
            sys.stderr.flush()

            if moves_to_reach < moves:
                self.killshot = True
                self.directions = directions
                self.game.issue_order(self.directions.pop())
                return

        # What are the legal moves we can make?
        legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
        trapped = []
        good_move = {}

        # d0414c00-e161-49a6-8604-58e139ee4a91

        direction_moves = self.game.field.calculate_remaining_movable_area(player_id=self.game.my_botid,
                                                                           players=self.game.players)
        backup_move = direction_moves.copy()

        value = max(direction_moves.keys(), key=(lambda key: direction_moves[key]))
        updated_cell, is_updated = self.game.field.get_cell_given_direction(self.game.field.cell, value, self.game.my_player(), self.game.my_botid)
        # more_legal = self.game.field.legal_moves2(my_id=self.game.my_botid, players=self.game.players,cell=updated_cell, direction=[value])
        my_pos, my_moves, my_trapped, my_future_cell = self.game.field.leak_fix2( self.game.my_botid, self.game.other_botid, self.game.players, enemy=None, future_cell=updated_cell, moves=0, direction=value)

        if my_moves:
            sys.stderr.write("***** LEAK FIX *****")
            sys.stderr.write("MOVE: %s\n" % my_moves)
            sys.stderr.write("Is Trapped?: %s\n" % my_trapped)
            sys.stderr.write("END POS: %s,%s\n" % (str(my_pos.row), str(my_pos.col)))
        sys.stderr.flush()
        best_next_move={}
        while(my_trapped):

            row, col = self.game.field.get_coordinate_given_direction(value, self.game.my_player().row,self.game.my_player().col)
            if self.game.field.is_legal(row, col, self.game.my_botid):
                best_next_move[value] = my_moves
            del direction_moves[value]

            if not direction_moves:
                break
            value = max(direction_moves.keys(), key=(lambda key: direction_moves[key]))
            if direction_moves[value] != 0:
                my_pos, my_moves, my_trapped, my_future_cell = self.game.field.leak_fix2(self.game.other_botid,
                                                                                            self.game.my_botid,
                                                                                            self.game.players, enemy=None,
                                                                                            future_cell=self.game.field.cell,
                                                                                            moves=0, direction=value)
            else:
                my_trapped = True

        if not direction_moves:

            value1=value2=0
            if best_next_move:
                value1 = max(best_next_move.keys(), key=(lambda key: best_next_move[key]))
            if backup_move:
                value2 = max(backup_move.keys(), key=(lambda key: backup_move[key]))

            value = max(value1,value2)
            # All directions are trapped
            # if best_next_move:
            #     sys.stderr.write("BEST NEXT MOVE %s\n" % (str(value)))
            #
            # if not value:
            #     sys.stderr.write("value if no BEST NEXT MOVE %s\n" %(str(value)))
            #     sys.stderr.write("\n")



        # while( not len(more_legal)):
        #     del direction_moves[value]
        #     value = max(direction_moves.keys(), key=(lambda key: direction_moves[key]))
        #     more_legal = self.game.field.legal_moves2(my_id=self.game.my_botid, players=self.game.players,
        #                                               cell=updated_cell, direction=[value])

        if value:
            self.game.issue_order(value)
        else:
            self.game.issue_order_pass()


        # for move in legal:
        #     _, direction = move

        # Would this move trap us?
        # my_pos, my_moves, my_trapped, my_future_cell = self.game.field.leak_fix( self.game.other_botid,self.game.my_botid, self.game.players, enemy=None, future_cell=self.game.field.cell, moves=0)
        # if my_trapped:
        #     trapped.append(direction)
        #     sys.stderr.write("%s leads to TRAP!\n" % direction)
        #     sys.stderr.flush()
        #     continue

        # # The map after we made that move:
        # updated_cell, is_updated = self.game.field.get_cell_given_direction(self.game.field.cell, direction, self.game.my_player(), self.game.my_botid)

        # for row in updated_cell:
        #     sys.stderr.write("\n")
        #     for cel in row:
        #         sys.stderr.write(str(cel) + ' ')
        # sys.stderr.write("\n")
        # sys.stderr.flush()

        # What Moves we can make from this move?
        # more_legal = self.game.field.future_legal_moves(self.game.players[self.game.my_botid], updated_cell,self.game.other_botid)
        # more_legal = self.game.field.legal_moves2(my_id=self.game.my_botid, players=self.game.players,cell=updated_cell, direction=[direction])
        # sys.stderr.write("Moves after %s are %s\n" % (direction, str(len(more_legal))))

        # for more_moves in ['up','down','left','right']:
        #     more_direction = more_moves
        #     if (more_direction,direction) in self.converse_directions:
        #         continue
        #     sys.stderr.write("Direction: %s\n" % more_direction)
        #     sys.stderr.flush()
        #     direction_moves = self.game.field.calculate_remaining_movable_area(player_id=self.game.my_botid, players=self.game.players, directions= [direction, more_direction])
        #     good_move[direction] = good_move.get(direction, 0) + sum(direction_moves.values())
        #     sys.stderr.write("Good-Move-Direction: %s\n" % str(good_move[direction]))
        #     sys.stderr.flush()
        #     sys.stderr.write("=========================\n" )
        # for k,v in good_move.items():
        #     sys.stderr.write("Key: %s Value: %s\n" % (k, str(v)))
        #     sys.stderr.flush()

        # sys.stderr.flush()
        # if direction in good_move.keys():
        #     sys.stderr.write("Direction: %s have score %s\n" % (direction, str(good_move[direction])))
        #     sys.stderr.flush()

        # if good_move:
        #     maxval = max(good_move.values())
        #     # If Trapped
        #     if not maxval:
        #         sys.stderr.write("MOVING IF ALL ZERO (NO OPTION): %s\n" % "PASSED")
        #         sys.stderr.flush()
        #         self.game.issue_order_pass()
        #         return

        #     direction = [k for k,v in good_move.items() if v==maxval][0]
        #     sys.stderr.write("MOVING: %s\n" % direction)
        #     sys.stderr.flush()
        #     self.game.issue_order(direction)
        # elif trapped:
        #     sys.stderr.write("MOVING INSIDE TRAPPED: %s\n" % trapped[0])
        #     sys.stderr.flush()
        #     # Improvise trap comparison
        #     self.game.issue_order(trapped[0])
        # else:
        #     sys.stderr.write("MOVING IF PASSED: %s\n" % "PASSED")
        #     sys.stderr.flush()
        #     self.game.issue_order_pass()

        # my_pos, my_moves, my_trapped, my_future_cell = self.game.leak_fix( self.game.other_botid,self.game.my_botid, self.game.players, enemy=None, future_cell=self.game.field.cell, moves=0)
        #     if my_trapped:
        #         trapped.append(move)
        #         continue
        # safe_move.append(direction)

        # Flood_fill Use
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
