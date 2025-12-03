import numpy as np
from PyQt6 import QtCore


class ParallelTurn(QtCore.QThread):
    """ Thread wrapper """

    def __init__(self, ai_func, player_sequence, board, time_budget, tile_width, tile_height):
        super().__init__()

        self.ai_func = ai_func
        self.board = board
        self.player_sequence = player_sequence
        self.time_budget = time_budget

        self.team = int(player_sequence[0])
        self.color = player_sequence[1]
        self.board_orientation = int(player_sequence[2])

        self.tile_width = tile_width
        self.tile_height = tile_height

        self.next_move = ((0,0), (0,0))

    def run(self):
        self.next_move = self.ai_func(self.player_sequence,
                            np.copy(self.board),
                            self.time_budget,
                            tile_width=self.tile_width,
                            tile_height=self.tile_height)
        

