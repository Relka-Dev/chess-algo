import sys
import os

# Ajoute le chemin vers ISChess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ISChess'))

from Bots.Martin import chess_bot


def create_empty_board():
    """Crée un plateau d'échecs vide 8x8"""
    return [['' for _ in range(8)] for _ in range(8)]


def test_bot_returns_valid_format():
    """Test que le bot retourne bien deux tuples de coordonnées"""
    board = create_empty_board()
    board[1][0] = 'Pw'  # Pion blanc
    
    result = chess_bot('w', board, 1.0)
    
    # Vérifie que le retour est bien (src, dst)
    assert isinstance(result, tuple), "Le bot doit retourner un tuple"
    assert len(result) == 2, "Le bot doit retourner exactement 2 éléments"
    
    src, dst = result
    assert isinstance(src, tuple) and len(src) == 2, "src doit être un tuple (x, y)"
    assert isinstance(dst, tuple) and len(dst) == 2, "dst doit être un tuple (x, y)"


def test_bot_coordinates_within_bounds():
    """Test que les coordonnées retournées sont dans les limites du plateau"""
    board = create_empty_board()
    board[1][0] = 'Pw'
    board[6][7] = 'Pb'  # Pion noir
    
    src, dst = chess_bot('w', board, 1.0)
    
    # Vérifie que les coordonnées sont valides (0-7)
    assert 0 <= src[0] < 8, f"src x={src[0]} hors limites"
    assert 0 <= src[1] < 8, f"src y={src[1]} hors limites"
    assert 0 <= dst[0] < 8, f"dst x={dst[0]} hors limites"
    assert 0 <= dst[1] < 8, f"dst y={dst[1]} hors limites"


def test_bot_handles_white_pieces():
    """Test que le bot peut gérer des pièces blanches"""
    board = create_empty_board()
    board[0][0] = 'Rw'  # Tour blanche
    board[0][1] = 'Nw'  # Cavalier blanc
    board[1][0] = 'Pw'  # Pion blanc
    
    src, dst = chess_bot('w', board, 1.0)
    
    # Le bot doit retourner un coup valide
    assert src != dst, "La source et la destination ne peuvent pas être identiques"


def test_bot_handles_black_pieces():
    """Test que le bot peut gérer des pièces noires"""
    board = create_empty_board()
    board[7][0] = 'Rb'  # Tour noire
    board[7][1] = 'Nb'  # Cavalier noir
    board[6][0] = 'Pb'  # Pion noir
    
    src, dst = chess_bot('b', board, 1.0)
    
    # Le bot doit retourner un coup valide
    assert src != dst, "La source et la destination ne peuvent pas être identiques"


def test_bot_with_complex_board():
    """Test avec une position plus complexe"""
    board = create_empty_board()
    
    # Position de départ simplifiée
    # Pièces blanches
    board[0][0] = 'Rw'
    board[0][4] = 'Kw'
    board[1][0] = 'Pw'
    board[1][1] = 'Pw'
    
    # Pièces noires
    board[7][0] = 'Rb'
    board[7][4] = 'Kb'
    board[6][0] = 'Pb'
    board[6][1] = 'Pb'
    
    # Test pour les blancs
    src_w, dst_w = chess_bot('w', board, 1.0)
    assert isinstance(src_w, tuple) and isinstance(dst_w, tuple)
    
    # Test pour les noirs
    src_b, dst_b = chess_bot('b', board, 1.0)
    assert isinstance(src_b, tuple) and isinstance(dst_b, tuple)


def test_bot_respects_time_budget():
    """Test que le bot s'exécute dans le temps imparti"""
    import time
    
    board = create_empty_board()
    board[1][0] = 'Pw'
    
    time_budget = 0.5  # 500ms
    start = time.time()
    
    chess_bot('w', board, time_budget)
    
    elapsed = time.time() - start
    
    # Le bot devrait s'exécuter en moins de 2x le budget (marge de sécurité)
    assert elapsed < time_budget * 2, f"Bot trop lent: {elapsed:.3f}s pour un budget de {time_budget}s"


def test_bot_source_has_piece():
    """Test que la source du mouvement contient bien une pièce"""
    board = create_empty_board()
    board[1][0] = 'Pw'
    board[1][1] = 'Pw'
    
    src, dst = chess_bot('w', board, 1.0)
    
    # La position source doit contenir une pièce
    piece = board[src[1]][src[0]]  # Attention: board[y][x]
    assert piece != '', f"Aucune pièce à la position source {src}"
    assert piece.endswith('w'), f"La pièce source doit être blanche, trouvé: {piece}"