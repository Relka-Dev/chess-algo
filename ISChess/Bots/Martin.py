#
#   Example function to be implemented for
#       Single important function is next_best
#           color: a single character str indicating the color represented by this bot ('w' for white)
#           board: a 2d matrix containing strings as a descriptors of the board '' means empty location "XC" means a piece represented by X of the color C is present there
#           budget: time budget allowed for this turn, the function must return a pair (xs,ys) --> (xd,yd) to indicate a piece at xs, ys moving to xd, yd
#

#   Be careful with modules to import from the root (don't forget the Bots.)
from Bots.ChessBotList import register_chess_bot

def chess_bot(player_sequence, board, time_budget, **kwargs):

    color = player_sequence[1]

    
    for x in range(board.shape[0]-1):
         for y in range(board.shape[1]):
            # Making a tree out of every piece
            possible_mov([x,y], board)


    return (0,0), (0,0) 

# Fonction récursive
def possible_mov(piece_pos, board):
    piece = board[piece_pos][0]
    color = board[piece_pos][1]

    match piece:
        case 'p':
            moves = pawn_moves(piece_pos, board, color)
        case 'r':
            moves = rook_moves(piece_pos, board, color)
        case 'n':
            moves = knight_moves(piece_pos, board, color)
        case 'b':
            moves = bishop_moves(piece_pos, board, color)
        case 'q':
            moves = queen_moves(piece_pos, board, color)
        case 'k':
            moves = king_moves(piece_pos, board, color)

def pawn_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []
    
    if color == 'w':
        if board[x + 1, y] == ' ':
            moves.append((x + 1, y))
        if y > 0 and board[x + 1, y - 1] == 'b':
            moves.append((x + 1, y - 1))
        if y < board.shape[1] - 1 and board[x + 1, y + 1] == 'b':
            moves.append((x + 1, y + 1))
    elif color == 'b': 
        if board[x - 1, y] == ' ':
            moves.append((x - 1, y))
        if y > 0 and board[x - 1, y - 1] == 'w':
            moves.append((x - 1, y - 1))
        if y < board.shape[1] - 1 and board[x - 1, y + 1] == 'w':
            moves.append((x - 1, y + 1))
    
    return moves

def rook_moves(piece_pos, board):
    x, y = piece_pos


def knight_moves(piece_pos, board):
    
    pos_mov = [()]

def bishop_moves(piece_pos, board):
    pass

def queen_moves(piece_pos, board):
    pass

def king_moves(piece_pos, board):
    pass


def board_evaluation(board, color):
    pass
    
#   Example how to register the function
register_chess_bot("Martin", chess_bot)