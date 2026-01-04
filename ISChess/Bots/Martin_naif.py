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

KINGS_WEIGHT = 100
QUEENS_WEIGHT = 9
ROOKS_WEIGHT = 5
KNIGHTS_WEIGHT = 3
BISHOPS_WEIGHT = 3
PAWNS_WEIGHT = 1

DEPTH = 4

DEBUG = False

@dataclass
class Board:
    data: list[list[str]]
    initial_piece_position: tuple[int, int]
    next_piece_position: tuple[int, int]

def chess_bot(player_sequence, board, time_budget, **kwargs):
    old_boards = []
    new_boards = []
    
    initial_board = Board([[board[x, y] for y in range(board.shape[1])] for x in range(board.shape[0])], (0, 0), (0, 0))
    old_boards.append(initial_board)
    
    best_new_board = [-999999, None]
    color = player_sequence[1]
    initial_color = color
    
    if DEBUG:
        print(f"Bot Martin playing color {color} with time budget {time_budget} s")
    
    for i in range(DEPTH):
        for old_board in old_boards:
            for x in range(len(old_board.data)):
                for y in range(len(old_board.data[0])):
                    if old_board.data[x][y] != '' and len(old_board.data[x][y]) > 1 and old_board.data[x][y][1] == color:
                        new_boards.extend(possible_mov((x, y), old_board))
        
        if i == 0:
            first_level_boards = new_boards[:]
        
        old_boards = new_boards
        new_boards = []
        
        color = 'b' if color == 'w' else 'w'
    
    for board_to_evaluate in old_boards:
        board_score = board_evaluation(board_to_evaluate, initial_color)
        
        root_board = None
        for fb in first_level_boards:
            if (fb.initial_piece_position == board_to_evaluate.initial_piece_position and fb.next_piece_position == board_to_evaluate.next_piece_position):
                root_board = fb
                break
        
        if root_board and board_score > best_new_board[0]:
            best_new_board = [board_score, root_board]
    
    if best_new_board[1]:
        return best_new_board[1].initial_piece_position, best_new_board[1].next_piece_position
    return (0, 0), (0, 0)

#=================================================================================================
# l'idée de l'exploration des coups possibles :
# Parcourir l'entièreté du plateau (avec une couleur sélectionnée)
# pour chaque pièce de cette couleur, générer les coups possibles
# en fonction du type de pièce (pion, tour, cavalier, fou, reine, roi)
# pour chaque coup possible, remplir un tableau ou une liste avec les nouveaux états du plateau
# qui contient l'id de le pièce qui peut se déplacer sur la case ciblée
# on aura en résultat un tableau contenant tous les coups possibles pour la couleur sélectionnée avec l'id de la pièce
# Fonction récursive
def possible_mov(piece_pos, board_obj):
    board = board_obj.data
    piece = board[piece_pos[0]][piece_pos[1]][0]
    color = board[piece_pos[0]][piece_pos[1]][1]
    moves = []
    boards = []
    
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
    
    for move in moves:
        new_data = [row[:] for row in board]
        new_data[move[0]][move[1]] = new_data[piece_pos[0]][piece_pos[1]]
        new_data[piece_pos[0]][piece_pos[1]] = ''
        
        if board_obj.initial_piece_position == (0, 0):
            new_board = Board(new_data, piece_pos, move)
        else:
            new_board = Board(new_data, board_obj.initial_piece_position, board_obj.next_piece_position)
        
        boards.append(new_board)
    
    return boards

#=================================================================================================
# Fonction générale qui définis si une case est possible ou pas
def isMoveValid(target_pos, target_content, board, color):
    # si hors plateau alors alors move impossible
    if target_pos[0] < 0 or target_pos[0] >= len(board) or target_pos[1] < 0 or target_pos[1] >= len(board[0]):
        return False

    # si vide alors Move possible
    if target_content == '':
        return True
        
    # si ennemie alors move possible
    if len(target_content) > 1 and target_content[1] != color:
        return True
        
    # Si alliée alors c'est interdit (on ne fait rien)
    return False

#=================================================================================================
# mouvements possibles pour le pion
# attention le mouvement du pion est le seul avec une fonction spécifique pour manger les pions adverses en diagonale
def pawn_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []
    
    step = 1 if color == 'w' else -1
    
    # Mouvement en avant possible seulement si case vide
    if 0 <= x + step < len(board) and board[x + step][y] == '':
        moves.append((x + step, y))
    
    dirs = [(step, -1), (step, 1)]

    for dx, dy in dirs:
        nx = x + dx
        ny = y + dy
            
        if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
            continue
        target_content = board[nx][ny]
           
        # seulement si ennemie alors move possible
        if target_content != '' and len(target_content) > 1 and target_content[1] != color:
            moves.append((nx, ny))

    return moves

#=================================================================================================
# mouvements possible de la tour, si son mouvement est bloqué par une pièce alliée ou ennemie, il ne peut pas sauter par dessus
def rook_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []

    dirs = [(-1,0), (1,0), (0,-1), (0,1)]

    for dx, dy in dirs:
        step = 1

        while True:
            nx = x + dx * step
            ny = y + dy * step

            # si il y a une sortie plateau => on arrête la boucle
            if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
                break

            target_content = board[nx][ny]

            # si la case est vide, on peut continuer
            if target_content == '':
                moves.append((nx, ny))
                step += 1
                continue

            # si la case est occupée par une pièce ennemie, on peut manger => on arrête
            if len(target_content) > 1 and target_content[1] != color:
                moves.append((nx, ny))
                break

            # si la case est occupée par une pièce alliée, on arrête
            break

    return moves

#=================================================================================================
# mouvements possibles pour le cavalier
def knight_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []

    dirs = [(-2,-1), (-2,1),
            (-1,-2), (-1,2),
            (1,-2),  (1,2),
            (2,-1),  (2,1)]

    for dx, dy in dirs:
        nx = x + dx
        ny = y + dy

        target_pos = (nx, ny)
        if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
            continue
        target_content = board[nx][ny]

        if (isMoveValid(target_pos, target_content, board, color)):
            moves.append((nx, ny))

    return moves

#=================================================================================================
# mouvements possible du fou, si son mouvement est bloqué par une pièce alliée ou ennemie, il ne peut pas sauter par dessus
def bishop_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []

    dirs = [(-1,-1), (-1,1),
            (1,-1),  (1,1)]

    for dx, dy in dirs:
        step = 1
        while True:
            nx = x + dx * step
            ny = y + dy * step

            # si il y a une sortie plateau => on arrête la boucle
            if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
                break
            
            target_content = board[nx][ny]
            
            # si la case est vide, on peut continuer
            if target_content == '':
                moves.append((nx, ny))
                step += 1
                continue

            # si la case est occupée par une pièce ennemie, on peut capturer et arrêter
            if len(target_content) > 1 and target_content[1] != color:
                moves.append((nx, ny))
                break
            
            # si la case est occupée par une pièce alliée, on arrête
            break
        
    return moves

#=================================================================================================
# mouvements possible de la reine, si son mouvement est bloqué par une pièce alliée ou ennemie, il ne peut pas sauter par dessus
def queen_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []

    dirs = [(-1,0), (1,0), (0,-1), (0,1),
            (-1,-1), (-1,1), (1,-1), (1,1)]

    for dx, dy in dirs:
        step = 1

        while True:
            nx = x + dx * step
            ny = y + dy * step

            # hors plateau -> stop direction
            if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
                break

            target_content = board[nx][ny]

            # vide -> move possible, on continue
            if target_content == '':
                moves.append((nx, ny))
                step += 1
                continue

            # ennemie -> move possible (capture), stop
            if len(target_content) > 1 and target_content[1] != color:
                moves.append((nx, ny))
                break

            # alliée -> stop
            break

    return moves

#=================================================================================================
def king_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []    
    
    dirs = [(-1,-1), (-1,0), (-1,1),
            (0,-1),          (0,1),
            (1,-1),  (1,0),  (1,1)]

    for dx, dy in dirs:
        nx = x + dx
        ny = y + dy

        if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
            continue
        target_pos = (nx, ny)
        target_content = board[nx][ny]

        if (isMoveValid(target_pos, target_content, board, color)):
            moves.append((nx, ny))

    return moves

#=================================================================================================
def board_evaluation(board_obj, color):
    board = board_obj.data
    white_value = 0
    black_value = 0

    for x in range(len(board)):
        for y in range(len(board[0])):
            piece_content = board[x][y]
            if piece_content == '' or len(piece_content) < 2:
                continue
                
            piece = piece_content[0]
            piece_color = piece_content[1]

            match piece:
                case 'p':
                    if piece_color == "b": black_value += PAWNS_WEIGHT
                    if piece_color == "w": white_value += PAWNS_WEIGHT
                case 'r':
                    if piece_color == "b": black_value += ROOKS_WEIGHT
                    if piece_color == "w": white_value += ROOKS_WEIGHT
                case 'n':
                    if piece_color == "b": black_value += KNIGHTS_WEIGHT
                    if piece_color == "w": white_value += KNIGHTS_WEIGHT
                case 'b':
                    if piece_color == "b": black_value += BISHOPS_WEIGHT
                    if piece_color == "w": white_value += BISHOPS_WEIGHT
                case 'q':
                    if piece_color == "b": black_value += QUEENS_WEIGHT
                    if piece_color == "w": white_value += QUEENS_WEIGHT
                case 'k':
                    if piece_color == "b": black_value += KINGS_WEIGHT
                    if piece_color == "w": white_value += KINGS_WEIGHT

    if color == 'w':
        return white_value - black_value
    
    return black_value - white_value

#=================================================================================================
    
#   Example how to register the function
register_chess_bot("Martin_naif", chess_bot)