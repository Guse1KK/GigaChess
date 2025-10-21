class Queries():
    CREATE_USER = """INSERT INTO profiles (username, lose, draw, win, tg_id) VALUES (?,?,?,?,?)""" 
    UPDATE_WIN = """UPDATE profiles SET win = ? WHERE tg_id = ? """
    UPDATE_LOSE = """UPDATE profiles SET lose = ? WHERE tg_id = ?"""
    UPDATE_DRAW = """UPDATE profiles SET draw = ? WHERE tg_id = ?"""
    SELECT_WIN_BY_TG_ID = """SELECT win FROM profiles WHERE tg_id = ?"""
    SELECT_LOSE_BY_TG_ID = """SELECT lose FROM profiles WHERE tg_id = ?"""
    SELECT_DRAW_BY_TG_ID = """SELECT draw FROM profiles WHERE tg_id = ?"""
    SELECT_CHECK_PROFILE = """SELECT * FROM profiles WHERE tg_id = ?"""
    SELECT_PLAYER_ID_BY_TG_ID = """SELECT id FROM profiles WHERE tg_id = ?"""
    SELECT_USER_NAMES = """SELECT username FROM profiles"""

    CREATE_GAME = """INSERT INTO games (player1, status, description, fen, level) VALUES (?,'in progres',?, 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', ?)"""
    SELECT_GAMES_BY_PLAYER_ID = """SELECT * FROM games WHERE player1 = ?"""
    SELECT_FINISHED_GAMES_BY_PLAYER_ID = """SELECT * FROM games WHERE player1 = ? AND status = 'over'"""
    SELECT_FEN_BY_GAME_ID = """SELECT fen FROM games WHERE id = ? """
    UPDATE_FEN_BY_GAME_ID = """UPDATE games SET fen = ? WHERE id = ?"""
    SELECT_GAME_LEVEL_BY_GAME_ID = """SELECT level FROM games WHERE id = ? """

