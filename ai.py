import chess
import chess.engine
import chess.svg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from os import remove
from typing import Dict, Any, Optional
from DataBase import DataBase 

db = DataBase("GigaBase.db")


def push(board: chess.Board, move: str, file: str) -> Dict[str, Any]:
    """
    Обрабатывает ход игрока и ответный ход бота, обновляет состояние игры.
    
    Преобразует текстовый ход в объект хода, проверяет его легальность,
    выполняет ход игрока, проверяет состояние игры, затем выполняет ход бота
    с учетом уровня сложности, сохраняет новое состояние доски в SVG/PNG.
    
    Args:
        board (chess.Board): Текущее состояние шахматной доски
        move (str): Ход игрока в формате UCI (например, 'e2e4')
        file (str): Идентификатор файла для сохранения изображения доски
        
    Returns:
        Dict[str, Any]: Словарь с информацией о состоянии игры, содержащий:
            - 'board' (chess.Board): Обновленное состояние доски
            - 'finish' (bool): Флаг завершения игры
            - 'message' (str): Сообщение о состоянии игры
            
    Raises:
        chess.engine.EngineTerminatedError: Если движок Stockfish завершился с ошибкой
        Exception: Другие ошибки при работе с движком или файловой системой
        
    Examples:
        >>> board = chess.Board()
        >>> result = push(board, "e2e4", "game_123")
        >>> print(result["message"])
    """
    engine = chess.engine.SimpleEngine.popen_uci(r"stockfish/stockfish-windows-x86-64-avx2.exe")
    move_obj: chess.Move = chess.Move.from_uci(move)

    if move_obj in board.legal_moves:
        board.push(move_obj)
        game_state: Dict[str, Any] = check_game_state(board)
        game_state["board"] = board
        
        if game_state["finish"]:
            if game_state["message"] == "Мат":
                game_state["message"] = "Мат! Победил кожаный"
            engine.quit()
            return game_state
    else: 
        illegal_move: Dict[str, Any] = {
            "board": board, 
            "finish": False, 
            "message": "illegal_move"
        }  
        engine.quit()
        return illegal_move 
    
    level: str = db.select_level(file)[0]
    
    # Устанавливаем время для хода бота в зависимости от уровня сложности
    time: float
    if level == 'легко':
        time = 0.03
    elif level == 'нормально':
        time = 0.075
    elif level == 'сложно':
        time = 0.09
    else:
        time = 0.075
        
    result: chess.engine.PlayResult = engine.play(board, chess.engine.Limit(time=time))
    board.push(result.move)
    engine.quit()
    
    game_state = check_game_state(board)
    game_state["board"] = board
    
    if game_state["finish"]:
        if game_state["message"] == "Мат":
            game_state["message"] = "Мат! Победило ведро с гвоздями"
    
    # Генерируем SVG изображение доски с подсветкой последнего хода
    svg_data: str = chess.svg.board(board=board, lastmove=board.peek())

    # Сохраняем SVG файл
    with open(f"image_base/{file}.svg", "w", encoding="utf-8") as f:
        f.write(svg_data)
    
    # Конвертируем SVG в PNG
    drawing = svg2rlg(f"image_base/{file}.svg")
    renderPM.drawToFile(drawing, f"image_base/{file}.png", fmt="PNG")
    
    return game_state


def check_game_state(board: chess.Board) -> Dict[str, Any]:
    """
    Проверяет текущее состояние шахматной игры на наличие завершающих условий.
    
    Проверяет различные условия окончания игры: мат, пат, недостаток материала,
    правило 75 ходов, пятикратное повторение позиции и другие варианты ничьи.
    
    Args:
        board (chess.Board): Шахматная доска для проверки состояния
        
    Returns:
        Dict[str, Any]: Словарь с информацией о состоянии игры:
            - 'finish' (bool): True если игра завершена, иначе False
            - 'message' (str): Описательное сообщение о состоянии игры
            
    Examples:
        >>> board = chess.Board()
        >>> state = check_game_state(board)
        >>> print(state["finish"], state["message"])
        False Игра продолжается.
    """
    if board.is_checkmate():
        return {
            "finish": True,
            "message": "Мат"
        }
    elif board.is_stalemate():
        return {
            "finish": True,
            "message": "Пат. Ничья."
        }
    elif board.is_insufficient_material():
        return {
            "finish": True,
            "message": "Недостаточно материала для мата. Ничья."
        }
    elif board.is_seventyfive_moves():
        return {
            "finish": True,
            "message": "Ничья по правилу 75 ходов."
        }
    elif board.is_fivefold_repetition():
        return {
            "finish": True,
            "message": "Ничья из-за пятикратного повторения позиции."
        }
    elif board.is_variant_draw():
        return {
            "finish": True,
            "message": "Ничья по правилам варианта игры."
        }
    else:
        # Игра продолжается
        if board.is_check():
            return {
                "finish": False,
                "message": "Шах!"
            }
        else:
            return {
                "finish": False,
                "message": "Игра продолжается."
            }


# Пример использования:
# board = chess.Board("r1bq1rk1/ppp2ppp/2n2n2/3p4/3P4/2bBPN2/PP3PPP/R1BQ1RK1 w - - 0 2")
# a = push(board, "b2c3", "test")
# print(a)