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

DEPTH = 3
MAGIC_SQUARE = [(3, 3), (3, 4), (4, 3), (4, 4)]

DEBUG = False
PERSPECTIVE_COLOR = None  # couleur du joueur initial (référence pour le sens des pions)

CONTROL_CENTER_BONUS = 1
ADVANCED_PAWN_MULTIPLICATOR_BONUS = 0.5
ALLIED_KING_NOT_IN_CHECK_BONUS = 5
ENEMY_KING_IN_CHECK_BONUS = 3


@dataclass
class Board:
    data: list[list[str]]
    initial_piece_position: tuple[int, int]
    next_piece_position: tuple[int, int]

def chess_bot(player_sequence, board, time_budget, **kwargs):
    global PERSPECTIVE_COLOR
    
    initial_board = Board([[board[x, y] for y in range(board.shape[1])] for x in range(board.shape[0])], (0, 0), (0, 0))
    color = player_sequence[1]
    PERSPECTIVE_COLOR = color
    
    if DEBUG:
        print(f"Bot Martin playing color {color} with time budget {time_budget} s")
    
    best_score_board = min_max(DEPTH, initial_board, color, color, -999999, 999999)

    if best_score_board[1] == None:
        return (0, 0), (0, 0)

    return best_score_board[1].initial_piece_position, best_score_board[1].next_piece_position


def min_max(depth_remaining: int, board: Board, current_color: str, initial_color: str, alpha: int, beta: int) -> tuple[int, Board]:
    new_boards = [] 

    # Cas de base, profondeur 0, on explore plus
    if depth_remaining == 0:
        return board_evaluation(board, initial_color), board

    for x in range(len(board.data)):
        for y in range(len(board.data[0])):
            if board.data[x][y] != '' and len(board.data[x][y]) > 1 and board.data[x][y][1] == current_color:
                new_boards.extend(possible_mov((x, y), board))
                if DEBUG:
                    print(f"Board : {board} generated")
    
    # Joueur à maximiser
    if current_color == initial_color:
        best_score_board = (-999999, None)

        for new_board in new_boards:
            color = 'b' if current_color == 'w' else 'w'
            current_score_board = min_max(depth_remaining - 1, new_board, color, initial_color, alpha, beta)

            if current_score_board[0] > best_score_board[0]:
                best_score_board = (current_score_board[0], new_board)
            
            if current_score_board[0] > alpha:
                alpha = current_score_board[0]
            
            if alpha >= beta:
                break
    # Joueur à minimiser
    else:
        best_score_board = (9999999, None)
    
        for new_board in new_boards:
            color = 'b' if current_color == 'w' else 'w'
            current_score_board = min_max(depth_remaining - 1, new_board, color, initial_color, alpha, beta)
    
            if current_score_board[0] < best_score_board[0]:
                best_score_board = (current_score_board[0], new_board)
            
            if current_score_board[0] < beta:
                beta = current_score_board[0]
            
            if beta <= alpha:
                break
        
        if DEBUG:
            print(f"Meilleur Score : {best_score_board[0]}")
    
    return best_score_board

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

        # On refuse les coups qui laissent le roi en échec
        if is_king_in_check(new_data, color):
            continue

        new_board = Board(new_data, piece_pos, move)
        boards.append(new_board)
    
    return boards

#=================================================================================================
# Fonction pour trouver le roi (et gerer par le la suite les échecs et échecs et mat)
def find_king(board, color):
    for x in range(len(board)):
        for y in range(len(board[0])):
            pos = board[x][y]
            if pos != '' and len(pos) > 1 and pos[0] == 'k' and pos[1] == color:
                return (x, y)
    return None

#=================================================================================================
# Fonction pour check si un chemin n'est pas obstruer (de manière générale)
def is_path_clear(board, x, y, dx, dy, steps):
    for i in range(1, steps):
        nx = x + dx * i
        ny = y + dy * i
        if board[nx][ny] != '':
            return False
    return True

#=================================================================================================
# Fonction pour check si un chemin n'est pas obstruer (de manière générale)
def is_king_in_check(board, color):
    king_pos = find_king(board, color)
    if king_pos is None:
        return True  # pas de roi = situation invalide -> on considère "en échec"

    for x in range(len(board)):
        for y in range(len(board[0])):
            sq = board[x][y]
            if sq == '' or len(sq) < 2:
                continue
            if sq[1] == color:
                continue  # allié
            if attacks_square((x, y), king_pos, board):
                return True
    return False

#=================================================================================================
# Fonction pour check si une case est attaquée par une pièce ennemie (reflexion inversée des fonctions de mouvement qui suivent)
# la fonction is_path_clear est utilisée seulement ici et pas dans les fonctions de mouvement implémantées AVANT.
def attacks_square(from_pos, target_pos, board):
    fx, fy = from_pos
    tx, ty = target_pos

    attacker = board[fx][fy]
    if attacker == '' or len(attacker) < 2:
        return False

    piece = attacker[0]
    dx = tx - fx
    dy = ty - fy

    adx = abs(dx)
    ady = abs(dy)

    # Pion : dépend de la perspective (pas de flip dans le minmax)
    if piece == 'p':
        pawn_step = 1 if attacker[1] == PERSPECTIVE_COLOR else -1
        return (dx == pawn_step and (dy == -1 or dy == 1))

    # Roi
    if piece == 'k':
        return adx <= 1 and ady <= 1 and not (adx == 0 and ady == 0)

    # Cavalier
    if piece == 'n':
        return (adx, ady) in [(1, 2), (2, 1)]

    # Tour
    if piece == 'r':
        if dx == 0 and dy != 0:
            steps = ady
            step_y = 1 if dy > 0 else -1
            return is_path_clear(board, fx, fy, 0, step_y, steps)
        if dy == 0 and dx != 0:
            steps = adx
            step_x = 1 if dx > 0 else -1
            return is_path_clear(board, fx, fy, step_x, 0, steps)
        return False

    # Fou
    if piece == 'b':
        if adx == ady and adx != 0:
            steps = adx
            step_x = 1 if dx > 0 else -1
            step_y = 1 if dy > 0 else -1
            return is_path_clear(board, fx, fy, step_x, step_y, steps)
        return False

    # Reine
    if piece == 'q':
        # Diagonale
        if adx == ady and adx != 0:
            steps = adx
            step_x = 1 if dx > 0 else -1
            step_y = 1 if dy > 0 else -1
            return is_path_clear(board, fx, fy, step_x, step_y, steps)
        # Ligne ou colonne
        if dx == 0 and dy != 0:
            steps = ady
            step_y = 1 if dy > 0 else -1
            return is_path_clear(board, fx, fy, 0, step_y, steps)
        if dy == 0 and dx != 0:
            steps = adx
            step_x = 1 if dx > 0 else -1
            return is_path_clear(board, fx, fy, step_x, 0, steps)
        return False

    return False

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
    
    step = 1
    
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

        if isMoveValid(target_pos, target_content, board, color):
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
# mouvements possible du rois
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

        if isMoveValid(target_pos, target_content, board, color):
            moves.append((nx, ny))

    return moves

#=================================================================================================
def get_game_phase(board):
    pieces = count_pieces(board)
    if pieces >= 28: 
        return "EARLY"
    elif pieces >= 16:
        return "MID"
    else:
        return "LATE"

def count_pieces(board):
    total_pieces = 0
    for x in range(len(board.data)):
        for y in range(len(board.data[0])):
            if board.data[x][y] != '' and board.data[x][y] != 'X':
                total_pieces += 1
    return total_pieces

#=================================================================================================
# fonction d'évaluation du plateau
def board_evaluation(board_obj, color):
    board = board_obj.data
    white_value = 0
    black_value = 0

    # Poids des pièces
    piece_values = {
        'p': PAWNS_WEIGHT,
        'r': ROOKS_WEIGHT,
        'n': KNIGHTS_WEIGHT,
        'b': BISHOPS_WEIGHT,
        'q': QUEENS_WEIGHT,
        'k': KINGS_WEIGHT
    }
    
    game_phase = get_game_phase(board_obj)
    
    white_king_alive = False
    black_king_alive = False
    
    # Compteur de contrôle du centre pour early/mid game
    white_value = 0
    black_value = 0
    
    for x in range(len(board)):
        for y in range(len(board[0])):
            # String de la pièce
            piece_content = board[x][y]
            if piece_content != '':
                
                piece = piece_content[0]
                piece_color = piece_content[1]

                # On check si les rois sont en vie
                if piece == 'k':
                    if piece_color == 'w':
                        white_king_alive = True
                    else:
                        black_king_alive = True

                # Qualité de base de la pièce
                base_value = piece_values.get(piece, 0)

                # Bonus de position
                position_bonus = 0

                # Early game et Mid game: contrôle du centre
                if game_phase == "EARLY" or game_phase == "MID":
                    # Pour chaque case du carré magique, vérifier si cette pièce la contrôle (présente sur les cases ou peut l'attaquer / défendre)
                    for center_square in MAGIC_SQUARE:
                        # Pièce présente sur la case ou en capacité de la défendre / attaquer
                        if (x, y) == center_square or attacks_square((x, y), center_square, board):
                            if piece_color == "w":
                                white_value += CONTROL_CENTER_BONUS
                            else:
                                black_value += CONTROL_CENTER_BONUS

                if game_phase == "LATE":
                    if piece == 'p':
                        # Plus un pion est proche de la promotion, plus il vaux
                        if piece_color == 'w':
                            white_value +=  x * ADVANCED_PAWN_MULTIPLICATOR_BONUS
                        else:
                            black_value += x * ADVANCED_PAWN_MULTIPLICATOR_BONUS
    
    # Roi adverse pas présent -> victoire (valeur max)
    if color == 'w' and not black_king_alive:
        return 999999
    elif color == 'b' and not white_king_alive:
        return 999999
    
    # Roi pas présent -> défaite (valeur min)
    if color == 'w' and not white_king_alive:
        return -999999
    elif color == 'b' and not black_king_alive:
        return -999999

    # Bonus si le roi n'est pas en échec
    if not is_king_in_check(board, color):
        if color == 'w':
            white_value += ALLIED_KING_NOT_IN_CHECK_BONUS
        else:
            black_value += ALLIED_KING_NOT_IN_CHECK_BONUS
    
    # Bonus si le roi adverse est en échec
    enemy_color = 'b' if color == 'w' else 'w'
    if is_king_in_check(board, enemy_color):
        if color == 'w':
            white_value += ENEMY_KING_IN_CHECK_BONUS 
        else:
            black_value += ENEMY_KING_IN_CHECK_BONUS 

    if color == 'w':
        return white_value - black_value
    
    return black_value - white_value


#=================================================================================================
    
#   Example how to register the function
register_chess_bot("Martin_metrics", chess_bot)