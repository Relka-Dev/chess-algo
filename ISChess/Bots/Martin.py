# Project       : Martin - ISChess
# Authors       : Jowhn Blake, Karel Vilém Svoboda
# Affiliation   : HES-SO Valais, Algorithmes et Structures de données
# Date          : 07.01.2026

import time
import random
from Bots.ChessBotList import register_chess_bot
from dataclasses import dataclass

# Valeurs des pièces
KINGS_WEIGHT = 100
QUEENS_WEIGHT = 9
ROOKS_WEIGHT = 5
KNIGHTS_WEIGHT = 3
BISHOPS_WEIGHT = 3
PAWNS_WEIGHT = 1

DEPTH = 2

# Carré magique, la zone à contrôler pendant le EARLY / MID game
MAGIC_SQUARE = [(3, 3), (3, 4), (4, 3), (4, 4)]

# Variables pour le debug et les métriques
DEBUG = False
METRICS_ENABLED = True
METRICS_PRINT = True

METRICS = None  # Dictionnaire pour stocker les métriques de performance
PERSPECTIVE_COLOR = None  # Couleur du joueur initial (référence pour le sens des pions)

# Constantes pour les heuristiques de la board d'évaluation
CONTROL_CENTER_BONUS = 0.5
ADVANCED_PAWN_MULTIPLICATOR_BONUS = 0.2
ALLIED_KING_NOT_IN_CHECK_BONUS = 3
ENEMY_KING_IN_CHECK_BONUS = 1

# Constante pour la gestion du budget de temps
TIMER_PURCENT = 0.80 # Pourcentage du temps total utilisé
START_TIME = 0
TIME_LIMIT = 0

BOARD_POSITIONS = None
PREVIOUS_TABLE_DATA = {}

EARLY_GAME_PIECE_COUNT_MIN = 20
MID_GAME_PIECE_COUNT_MIN = 12

LATE_GAME_ENEMY_KING_IN_CHECK_BONUS = 3
LATE_GAME_DEPTH_BONUS = 2
ADVANCED_KING_MALUS_MULTIPLICATOR = -0.3
ADVANCED_QUEEN_MALUS_MULTIPLICATOR = -0.2

@dataclass
class Board:
    """
        Structure de données permettant de représenter un plateau de jeu
        data: Matrice 2D représentant le plateau
        initial_piece_position: Position (x,y) de la pièce initiale bougée
        next_piece_position: Position (x,y) de la pièce initiale au coup suivant
    """
    data: list[list[str]]
    initial_piece_position: tuple[int, int]
    next_piece_position: tuple[int, int]

def chess_bot(player_sequence, board, time_budget, **kwargs):
    global PERSPECTIVE_COLOR, START_TIME, TIME_LIMIT, BOARD_POSITIONS, METRICS, DEBUG, PREVIOUS_TABLE_DATA, DEPTH



    # Nettoyer le cache pour le nouveau coup
    # Pas de rétention entre les évaluations
    PREVIOUS_TABLE_DATA.clear()

    # Calcul du temps total avec la marge
    TIME_LIMIT = time_budget * TIMER_PURCENT
    START_TIME = time.time()
    
    # Initialisation des métriques
    if METRICS_ENABLED:
        METRICS = {
            # Temps
            "t_total": 0.0,
            "t_search": 0.0,
            "t_eval": 0.0,

            # Exploration
            "minmax_calls": 0,
            "boards_generated": 0,
            "moves_generated": 0,
            "moves_legal": 0,
            "moves_illegal_check": 0,

            # Alpha-beta / limites
            "cutoffs": 0,
            "timeouts": 0,
            "cache_hits": 0,

            # Profondeur
            "max_depth_reached": 0,
        }
        _t0_total = time.perf_counter()
    
    # Génération de la board initiale
    initial_board = Board([[board[x, y] for y in range(board.shape[1])] for x in range(board.shape[0])], (0, 0), (0, 0))
    color = player_sequence[1]
    PERSPECTIVE_COLOR = color 

    if get_game_phase(initial_board) == "LATE":
        DEPTH += LATE_GAME_DEPTH_BONUS


    # Création de la matrice 2D de toutes les positions possibles de la board. Utile pour la stochastique en cas de timeout
    BOARD_POSITIONS = [(x, y) for x in range(board.shape[0]) for y in range(board.shape[1])]

    if DEBUG:
        print(f"Bot Martin playing color {color} with time budget {time_budget} s")
    
    if METRICS_ENABLED:
        _t0_search = time.perf_counter()
    
    # Tuple[meilleur_score: int, meilleur_board: Board]
    best_score_board = min_max(DEPTH, initial_board, color, color, -999999, 999999)

    if METRICS_ENABLED:
        METRICS["t_search"] += (time.perf_counter() - _t0_search)

    # Retourne un coup illégal s'il n'y a pas de coup légal
    if best_score_board[1] == None:
        return (0, 0), (0, 0)

    if METRICS_ENABLED:
        METRICS["t_total"] = time.perf_counter() - _t0_total

        if METRICS_PRINT:
            print(
                f"[METRICS] total={METRICS['t_total']:.4f}s "
                f"search={METRICS['t_search']:.4f}s eval={METRICS['t_eval']:.4f}s | "
                f"minmax_calls={METRICS['minmax_calls']} boards={METRICS['boards_generated']} | "
                f"moves gen={METRICS['moves_generated']} legal={METRICS['moves_legal']} "
                f"illegal_check={METRICS['moves_illegal_check']} | "
                f"cutoffs={METRICS['cutoffs']} timeouts={METRICS['timeouts']} cache_hits={METRICS['cache_hits']} | "
                f"max_depth={METRICS['max_depth_reached']}"
            )

    # Retourne le meilleur coup trouvé
    return best_score_board[1].initial_piece_position, best_score_board[1].next_piece_position


def min_max(depth_remaining: int, board: Board, current_color: str, initial_color: str, alpha: int, beta: int) -> tuple[int, Board]:
    """
        Algorithme récursif de recherche de la board avec le meilleur score.
        L'objectif est de maximiser le score du joueur avec la initial_color.
        On part du principe que le joueur adverse va jouer le pire coup pour le joueur de initial_color.
        Ainsi de suite jusqu'à arriver au cas de base quand depth_remaining arrive à 0
        L'optimisation se fait avec la mémorisation et le alpha-beta pruning
        La mémorisation se fait en hashant les boards avec leur couleur et la profondeur restante puis en les stockant dans un dictionnaire {hash, [score, board]}
        L'alpha et beta pruning permet de couper les branches lesquelles on a la certitude qu'elles ne sont pas prises en compte
        Alpha   : Représente la meilleure valeur que le joueur MAX peut déjà garantir
        Beta    : Représente la pire valeur que le joueur MIN peut imposer à MAX
    """
    # Génération du hash de la board
    cache_key = (str(board.data), depth_remaining, current_color)
    
    # On vérifier si déjà calculé, si oui, on retourne le score et la board en cache
    if cache_key in PREVIOUS_TABLE_DATA:
        if METRICS_ENABLED:
            METRICS["cache_hits"] += 1
        return PREVIOUS_TABLE_DATA[cache_key]

    if METRICS_ENABLED:
        METRICS["minmax_calls"] += 1

        current_depth = DEPTH - depth_remaining
        if current_depth > METRICS["max_depth_reached"]:
            METRICS["max_depth_reached"] = current_depth
        
    # Cas de base, on s'arrête à la profondeur 0
    if depth_remaining == 0:
        return board_evaluation(board, initial_color), board

    new_boards = []

    # On choisit l'ordre des cases à scanner de façon aléatoire
    # Cela est utile en tant que stochastique, quand un timeout se produit, il n'y a pas de préférence au niveau des pièces
    positions = BOARD_POSITIONS.copy()
    random.shuffle(positions)
    for x, y in positions:
        if board.data[x][y] != '' and len(board.data[x][y]) > 1 and board.data[x][y][1] == current_color:
            new_boards.extend(possible_mov((x, y), board))
    
    # Si on peut capturer le roi au coup suivant, c'est le meilleur coup
    enemy_color = 'b' if current_color == 'w' else 'w'
    for board_candidate in new_boards:
        if find_king(board_candidate.data, enemy_color) is None:
            if current_color == initial_color:
                return 999999, board_candidate
            else:
                return -999999, board_candidate

    # Joueur à maximiser, on cherche la board avec le meilleur score
    if current_color == initial_color:
        best_score_board = (-999999, None)

        for new_board in new_boards:
            # Gestion du timeout, on remonte si on a dépassé le temps limite
            if time.time() - START_TIME > TIME_LIMIT:
                if METRICS_ENABLED:
                    METRICS["timeouts"] += 1
                return best_score_board
            
            current_score_board = min_max(depth_remaining - 1, new_board, enemy_color, initial_color, alpha, beta)

            # Recherche de la meilleure board possible pour le joueur avec initial_color
            if current_score_board[0] > best_score_board[0]:
                best_score_board = (current_score_board[0], new_board)
            
            # Si la board actuelle est meilleure que l'alpha, il prend sa place
            if current_score_board[0] > alpha:
                alpha = current_score_board[0]
            
            if alpha >= beta:
                # Le joueur MIN a déjà un coup qui empêche le joueur MAX d'obtenir un meilleur résultat, alors on coupe la branche.
                if METRICS_ENABLED:
                    METRICS["cutoffs"] += 1
                break
    # Joueur à minimiser
    else:
        best_score_board = (9999999, None)
    
        for new_board in new_boards:
            # Gestion du timeout, on remonte si on a dépassé le temps limite
            if time.time() - START_TIME > TIME_LIMIT:
                if METRICS_ENABLED:
                    METRICS["timeouts"] += 1
                return best_score_board

            current_score_board = min_max(depth_remaining - 1, new_board, enemy_color, initial_color, alpha, beta)
    
            # Recherche de la pire board possible pour le joueur avec initial_color
            if current_score_board[0] < best_score_board[0]:
                best_score_board = (current_score_board[0], new_board)
            
            if current_score_board[0] < beta:
                beta = current_score_board[0]
            
            if beta <= alpha:
                # Le joueur MIN a déjà un coup qui empêche le joueur MAX d'obtenir un meilleur résultat, alors on coupe la branche.
                if METRICS_ENABLED:
                    METRICS["cutoffs"] += 1
                break
    
    # On sauvegarde la board référencée par son hash dans le dictionnaire
    PREVIOUS_TABLE_DATA[cache_key] = best_score_board
    
    return best_score_board

#=================================================================================================
# L'idée de l'exploration des coups possibles :
# Parcourir l'entièreté du plateau (avec une couleur sélectionnée)
# Pour chaque pièce de cette couleur, générer les coups possibles
# en fonction du type de pièce (pion, tour, cavalier, fou, reine, roi)
# Pour chaque coup possible, remplir un tableau ou une liste avec les nouveaux états du plateau
# qui contient l'id de la pièce qui peut se déplacer sur la case ciblée
# On aura en résultat un tableau contenant tous les coups possibles pour la couleur sélectionnée avec l'id de la pièce
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
    
    if METRICS_ENABLED:
        METRICS["moves_generated"] += len(moves)
    
    for move in moves:
        new_data = [row[:] for row in board]
        new_data[move[0]][move[1]] = new_data[piece_pos[0]][piece_pos[1]]
        new_data[piece_pos[0]][piece_pos[1]] = ''

        if is_king_in_check(new_data, color):
            if METRICS_ENABLED:
                METRICS["moves_illegal_check"] += 1
            continue
        
        if METRICS_ENABLED:
            METRICS["moves_legal"] += 1
            METRICS["boards_generated"] += 1
        
        new_board = Board(new_data, piece_pos, move)
        boards.append(new_board)
    
    return boards

#=================================================================================================
# Fonction pour trouver le roi (et gérer par la suite les échecs et échecs et mat)
def find_king(board, color):
    for x in range(len(board)):
        for y in range(len(board[0])):
            pos = board[x][y]
            if pos != '' and len(pos) > 1 and pos[0] == 'k' and pos[1] == color:
                return (x, y)
    return None

#=================================================================================================
# Fonction pour vérifier si un chemin n'est pas obstrué (de manière générale)
def is_path_clear(board, x, y, dx, dy, steps):
    for i in range(1, steps):
        nx = x + dx * i
        ny = y + dy * i
        if board[nx][ny] != '':
            return False
    return True

#=================================================================================================
# Fonction pour vérifier si le roi est en échec
def is_king_in_check(board, color):
    king_pos = find_king(board, color)
    if king_pos is None:
        return True  # Pas de roi = situation invalide -> on considère "en échec"

    for x in range(len(board)):
        for y in range(len(board[0])):
            sq = board[x][y]
            if sq == '' or len(sq) < 2:
                continue
            if sq[1] == color:
                continue  # Allié
            if attacks_square((x, y), king_pos, board):
                return True
    return False

#=================================================================================================
# Fonction pour vérifier si une case est attaquée par une pièce ennemie (réflexion inversée des fonctions de mouvement qui suivent)
# La fonction is_path_clear est utilisée seulement ici et pas dans les fonctions de mouvement implémentées AVANT.
def attacks_square(from_pos, target_pos, board):
    fx, fy = from_pos
    tx, ty = target_pos

    attacker = board[fx][fy]
    if attacker == '' or len(attacker) < 2:
        return False

    piece = attacker[0]
    attacker_color = attacker[1]
    dx = tx - fx
    dy = ty - fy

    adx = abs(dx)
    ady = abs(dy)

    # Pion
    if piece == 'p':
        pawn_step = 1 if attacker_color == PERSPECTIVE_COLOR else -1
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
# Fonction générale qui définit si une case est possible ou pas
def isMoveValid(target_pos, target_content, board, color):
    # Si hors plateau alors move impossible
    if target_pos[0] < 0 or target_pos[0] >= len(board) or target_pos[1] < 0 or target_pos[1] >= len(board[0]):
        return False

    # Si vide alors move possible
    if target_content == '':
        return True
        
    # Si ennemie alors move possible
    if len(target_content) > 1 and target_content[1] != color:
        return True
        
    # Si alliée alors c'est interdit (on ne fait rien)
    return False

#=================================================================================================
# Mouvements possibles pour le pion
# Attention le mouvement du pion est le seul avec une fonction spécifique pour manger les pions adverses en diagonale
def pawn_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []
    
    step = 1 if color == PERSPECTIVE_COLOR else -1
    
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
           
        # Seulement si ennemie alors move possible
        if target_content != '' and len(target_content) > 1 and target_content[1] != color:
            moves.append((nx, ny))

    return moves

#=================================================================================================
# Mouvements possibles de la tour, si son mouvement est bloqué par une pièce alliée ou ennemie, elle ne peut pas sauter par-dessus
def rook_moves(piece_pos, board, color):
    x, y = piece_pos
    moves = []

    dirs = [(-1,0), (1,0), (0,-1), (0,1)]

    for dx, dy in dirs:
        step = 1

        while True:
            nx = x + dx * step
            ny = y + dy * step

            # S'il y a une sortie plateau => on arrête la boucle
            if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
                break

            target_content = board[nx][ny]

            # Si la case est vide, on peut continuer
            if target_content == '':
                moves.append((nx, ny))
                step += 1
                continue

            # Si la case est occupée par une pièce ennemie, on peut manger => on arrête
            if len(target_content) > 1 and target_content[1] != color:
                moves.append((nx, ny))
                break

            # Si la case est occupée par une pièce alliée, on arrête
            break

    return moves

#=================================================================================================
# Mouvements possibles pour le cavalier
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
# Mouvements possibles du fou, si son mouvement est bloqué par une pièce alliée ou ennemie, il ne peut pas sauter par-dessus
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

            # S'il y a une sortie plateau => on arrête la boucle
            if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
                break
            
            target_content = board[nx][ny]
            
            # Si la case est vide, on peut continuer
            if target_content == '':
                moves.append((nx, ny))
                step += 1
                continue

            # Si la case est occupée par une pièce ennemie, on peut capturer et arrêter
            if len(target_content) > 1 and target_content[1] != color:
                moves.append((nx, ny))
                break
            
            # Si la case est occupée par une pièce alliée, on arrête
            break
        
    return moves

#=================================================================================================
# Mouvements possibles de la reine, si son mouvement est bloqué par une pièce alliée ou ennemie, elle ne peut pas sauter par-dessus
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

            # Hors plateau -> stop direction
            if nx < 0 or nx >= len(board) or ny < 0 or ny >= len(board[0]):
                break

            target_content = board[nx][ny]

            # Vide -> move possible, on continue
            if target_content == '':
                moves.append((nx, ny))
                step += 1
                continue

            # Ennemie -> move possible (capture), stop
            if len(target_content) > 1 and target_content[1] != color:
                moves.append((nx, ny))
                break

            # Alliée -> stop
            break

    return moves

#=================================================================================================
# Mouvements possibles du roi
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
    if pieces >= EARLY_GAME_PIECE_COUNT_MIN: 
        return "EARLY"
    elif pieces >= MID_GAME_PIECE_COUNT_MIN:
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
# Fonction d'évaluation du plateau
def board_evaluation(board_obj, color):
    board = board_obj.data

    white_value = 0
    black_value = 0
    
    if METRICS_ENABLED:
        _t0_eval = time.perf_counter()

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
    
    for x in range(len(board)):
        for y in range(len(board[0])):
            # String de la pièce
            piece_content = board[x][y]
            if piece_content != '':
                
                piece = piece_content[0]
                piece_color = piece_content[1]

                # On vérifie si les rois sont en vie
                if piece == 'k':
                    if game_phase == "EARLY" or game_phase == "MID": 
                        if piece_color == 'w':
                            white_value +=  x * ADVANCED_KING_MALUS_MULTIPLICATOR
                        else:
                            black_value += x * ADVANCED_KING_MALUS_MULTIPLICATOR

                    if piece_color == 'w':
                        white_king_alive = True
                    else:
                        black_king_alive = True
                
                if piece == 'q':
                    if game_phase == "EARLY": 
                        if piece_color == 'w':
                            white_value +=  x * ADVANCED_QUEEN_MALUS_MULTIPLICATOR
                        else:
                            black_value += x * ADVANCED_QUEEN_MALUS_MULTIPLICATOR

                # Qualité de base de la pièce
                base_value = piece_values.get(piece, 0)

                if piece_color == 'w':
                    white_value += base_value
                else:
                    black_value += base_value

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
                        # Plus un pion est proche de la promotion, plus il vaut
                        if piece_color == 'w':
                            white_value +=  x * ADVANCED_PAWN_MULTIPLICATOR_BONUS
                        else:
                            black_value += x * ADVANCED_PAWN_MULTIPLICATOR_BONUS
    
    # Roi adverse pas présent -> victoire (valeur max)
    if color == 'w' and not black_king_alive:
        if METRICS_ENABLED:
            METRICS["t_eval"] += (time.perf_counter() - _t0_eval)
        return 999999
    elif color == 'b' and not white_king_alive:
        if METRICS_ENABLED:
            METRICS["t_eval"] += (time.perf_counter() - _t0_eval)
        return 999999
    
    # Roi pas présent -> défaite (valeur min)
    if color == 'w' and not white_king_alive:
        if METRICS_ENABLED:
            METRICS["t_eval"] += (time.perf_counter() - _t0_eval)
        return -999999
    elif color == 'b' and not black_king_alive:
        if METRICS_ENABLED:
            METRICS["t_eval"] += (time.perf_counter() - _t0_eval)
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
            if game_phase == "LATE":
                white_value += LATE_GAME_ENEMY_KING_IN_CHECK_BONUS
        else:
            black_value += ENEMY_KING_IN_CHECK_BONUS 
            if game_phase == "LATE":
                black_value += LATE_GAME_ENEMY_KING_IN_CHECK_BONUS

    if color == 'w':
        if METRICS_ENABLED:
            METRICS["t_eval"] += (time.perf_counter() - _t0_eval)
        return white_value - black_value
    
    if METRICS_ENABLED:
        METRICS["t_eval"] += (time.perf_counter() - _t0_eval)
        
    return black_value - white_value


#=================================================================================================

register_chess_bot("Martin", chess_bot)