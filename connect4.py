# All logic specific to the game of Connect4        
import re
from gamebases import TwoPlayerGame

class Connect4(TwoPlayerGame):
    def __init__(self):
        TwoPlayerGame.__init__(self)
        # these could be class attributes but we avoid sharing data between threads
        self.row_count = 6
        self.col_count = 7
        self.max_moves = self.row_count * self.col_count
        self.player_tokens = (1, -1)
        self.format_tokens = ('  ', ' X', ' O')
        self.directions = ((1,0), (0,1), (1,1), (-1,1))
        # instance-specific attributes
        self.board = [0] * self.max_moves
        self.col_heights = [0] * self.col_count
    # handle a move
    def do_move(self, move):
        # validate move
        try:
            move = int(move)
            assert move >= 0
            height = self.col_heights[move]
            assert height < self.row_count
        except:
            return (False,
                    'INVALID MOVE: Enter a column index between 0 and %d. The column must not be full.' % (self.col_count - 1))
        # update state
        token = self.player_tokens[self.next_player]
        row = self.row_count - 1 - height
        self.board[row * self.col_count + move] = token
        self.col_heights[move] = height + 1
        self.move_count += 1
        # check for end of game by win or draw
        self.game_over = any([self.find4(row, move, dx, dy, token) for dx, dy in self.directions])
        if self.game_over: self.winner = self.players[self.next_player]
        if self.move_count == self.max_moves: self.game_over = True
        if self.game_over:
            if self.winner:
                result = "\nGAME OVER: %s wins.\n" % self.winner.name
            else:
                result = "\nGAME OVER: It's a draw.\n"
        else:
            result = ''
        return True, self.format_board() + result
    # check for 4-in-a-row
    def find4(self, row, col, inc_row, inc_col, token):
        consecutive = self.count_run(row, col, -inc_row, -inc_col, token, 0)
        if consecutive == 4: return True
        consecutive = self.count_run(row+inc_row, col+inc_col, inc_row, inc_col, token, consecutive)
        if consecutive == 4: return True
        return False
    def count_run(self, row, col, inc_row, inc_col, token, consecutive):
        while 0 <= row < self.row_count and 0 <= col < self.col_count and self.index_board(row, col) == token:
            consecutive += 1
            if consecutive == 4: return consecutive
            row += inc_row
            col += inc_col
        return consecutive
    # make board state appear 2-dimensional
    def index_board(self, row, col):
        return self.board[row * self.col_count + col]
    # return a string representing the current board state
    def format_board(self):
        board_str = ''.join((self.format_tokens[t] for t in self.board))
        pattern = r'(.{14})'
        def add_newline(match):
            return match.groups()[0] + ' |\n|'
        return '|' + re.sub(pattern, add_newline, board_str) + ' 0 1 2 3 4 5 6 |\n'
