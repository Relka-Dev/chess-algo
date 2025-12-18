#
#   Example function to be implemented for
#       Single important function is next_best
#           color: a single character str indicating the color represented by this bot ('w' for white)
#           board: a 2d matrix containing strings as a descriptors of the board '' means empty location "XC" means a piece represented by X of the color C is present there
#           budget: time budget allowed for this turn, the function must return a pair (xs,ys) --> (xd,yd) to indicate a piece at xs, ys moving to xd, yd
#

#   Be careful with modules to import from the root (don't forget the Bots.)
from Bots.ChessBotList import register_chess_bot
from dataclasses import dataclass

# Quality of pieces
KINGS_WEIGHT = 100
QUEENS_WEIGHT = 9
ROOKS_WEIGHT = 5
KNIGHTS_WEIGHT = 3
BISHOPS_WEIGHT = 3
PAWNS_WEIGHT = 1

# Number of moves ahead
DEPTH = 3

from dataclasses import dataclass


@dataclass
class Board:
    data: list[list[str]]
    initial_piece_position: tuple[int, int]
    next_piece_position: tuple[int, int]

def chess_bot(player_sequence, board, time_budget, **kwargs):
    # Ajouter 3 métriques
    old_boards = []
    new_boards = []
    
    # Créer le board initial
    initial_board = Board(board, (0, 0), (0, 0))
    old_boards.append(initial_board)

    
    best_new_board = [-999999, None]  # [board_score, Board]
    color = player_sequence[1]  # à qui jouer
    
    # generation des boards
    for i in range(DEPTH-1):
        for old_board in old_boards:
            for x in range(len(old_board.data)):
                for y in range(len(old_board.data[0])):
                    # Making a tree out of every piece
                    if old_board.data[x][y] != ' ' and old_board.data[x][y][0] == color:
                        new_boards.extend(possible_mov((x, y), old_board))
        old_boards = new_boards
        new_boards = []
        
        if color == 'w':
            color = 'b'
        elif color == 'b':
            color = 'w'
    
    for board_to_evaluate in old_boards:
        board_score = board_evaluation(board_to_evaluate)
        if board_score > best_new_board[0]:
            best_new_board = [board_score, board_to_evaluate]
    
    if best_new_board[1]:
        return best_new_board[1].initial_piece_position, best_new_board[1].next_piece_position
    return (0, 0), (0, 0)

def possible_mov(piece_pos: tuple[int, int], board: Board):
    piece = board.data[piece_pos[0]][piece_pos[1]][0]
    color = board.data[piece_pos[0]][piece_pos[1]][1]
    moves = []
    boards = []
    
    match piece:
        case 'p':
            moves = pawn_moves(piece_pos, board.data, color)
        case 'r':
            moves = rook_moves(piece_pos, board.data, color)
        case 'n':
            moves = knight_moves(piece_pos, board.data, color)
        case 'b':
            moves = bishop_moves(piece_pos, board.data, color)
        case 'q':
            moves = queen_moves(piece_pos, board.data, color)
        case 'k':
            moves = king_moves(piece_pos, board.data, color)
    
    for move in moves:
        new_data = [row[:] for row in board.data]
        new_data[move[0]][move[1]] = new_data[piece_pos[0]][piece_pos[1]]
        new_data[piece_pos[0]][piece_pos[1]] = ' '
        
        if board.initial_piece_position == (0, 0):
            new_board = Board(new_data, piece_pos, move)
        else:
            new_board = Board(new_data, board.initial_piece_position, board.next_piece_position)
        
        boards.append(new_board)
    
    return boards


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
    """
    Docstring for board_evaluation
    
    :param old_scores: Description
    :param board: Description
    :param color: Description
    """

    white_value = 0
    black_value = 0

    for x in range(board.shape[0]-1):
         for y in range(board.shape[1]):
                piece_pos = (x, y)
                piece = board[piece_pos][0]
                color = board[piece_pos][1]

                # Evaluation de qualité
                match piece:
                    case 'p':
                        if color == "b": black_value += PAWNS_WEIGHT
                        if color == "w": white_value += PAWNS_WEIGHT
                    case 'r':
                        if color == "b": black_value += ROOKS_WEIGHT
                        if color == "w": white_value += ROOKS_WEIGHT
                    case 'n':
                        if color == "b": black_value += KNIGHTS_WEIGHT
                        if color == "w": white_value += KNIGHTS_WEIGHT
                    case 'b':
                        if color == "b": black_value += BISHOPS_WEIGHT
                        if color == "w": white_value += BISHOPS_WEIGHT
                    case 'q':
                        if color == "b": black_value += QUEENS_WEIGHT
                        if color == "w": white_value += QUEENS_WEIGHT
                    case 'k':
                        if color == "b": black_value += KINGS_WEIGHT
                        if color == "w": white_value += KINGS_WEIGHT
                    
                # Evaluation par carré magique

    if color == 'w':
        return white_value - black_value # Plus ce score est élevée, plus blanc a de valeur et noir en a peu
    
    return black_value - white_value

    
    
    
#   Example how to register the function
register_chess_bot("Martin", chess_bot)