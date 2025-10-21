from typing import Dict, List, Tuple, Optional, Any, Union
import telebot
import sqlite3
import chess
import chess.engine
import chess.svg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from pathlib import Path
from ai import push
from os import remove
from telebot import types
import os

from DataBase import DataBase as Base

bot = telebot.TeleBot(token = "8406478816:AAF0BK2e7aI40aMK7Bf-YiLxhi9l5PzdzGg")

db = Base("GigaBase.db")

comands = [
    types.BotCommand("start", 'запускает бота'),\
    types.BotCommand('create_game', 'создает новую игру'),
    types.BotCommand('play_game', 'запускает уже существующую игру'),
    types.BotCommand('show_unfinished_games', 'показывает id незаконченных игр'),
    types.BotCommand('create_profile', 'регистрирует новый профиль'),
    types.BotCommand('help', 'Если тебе нужна помощь')
]

bot.set_my_commands(comands)

@bot.message_handler(commands=["start"])
def handler_start(message: Any) -> None:
    """
    Обрабатывает команду /start - приветственное сообщение.
    
    Args:
        message (Any): Объект сообщения от пользователя
        
    Returns:
        None
    """
    bot.send_message(message.chat.id, "Привет это GigaChess")

@bot.message_handler(commands=["help"])
def help_command(message: Any) -> None:
    """
    Обрабатывает команду /help - показывает инструкции по использованию.
    
    Args:
        message (Any): Объект сообщения от пользователя
        
    Returns:
        None
    """
    bot.send_message(message.chat.id, "Тебе нужна помощь??? Здесь нет ничего сложного, создай профиль, создай игру, выбери сложность и играй в свое удовольствие, ходы обозначаются форматом 'e2e4'")

def check_word(message: Any) -> bool:
    """
    Проверяет, является ли сообщение текстовым.
    
    Args:
        message (Any): Объект сообщения для проверки
        
    Returns:
        bool: Всегда возвращает True
    """
    return True

@bot.message_handler(commands=["create_profile"])
def handler_create_profile(message: Any) -> None:
    """
    Проверяет наличие профиля и запускает процесс создания при его отсутствии.
    
    Args:
        message (Any): Объект сообщения от пользователя
        
    Returns:
        None
        
    Raises:
        Exception: В случае ошибок при работе с базой данных
    """
    user_exist = db.if_profile_exist(message.from_user.id)
    if user_exist:
        bot.send_message(message.chat.id, "Чё ты доканался со своей регистрацией, есть у тебя аккаунт")
    else:
        bot.send_message(message.chat.id, "Чё не зареган, имя напиши!!!")
        bot.register_next_step_handler_by_chat_id(message.chat.id, process_user_name)

def process_user_name(message: Any) -> None:
    """
    Обрабатывает введенное имя пользователя и создает профиль.
    
    Args:
        message (Any): Объект сообщения с именем пользователя
        
    Returns:
        None
    """
    user_name: str = message.text
    spis: List[str] = db.select_all_user_names()
    
    if user_name not in spis:
        user_id: int = message.from_user.id
        if db.create_user(user_name, 0, 0, 0, user_id):
            bot.send_message(message.chat.id, "Я зарегал тебя аболтус")
        else:
            bot.send_message(message.chat.id, "Даже это ты смог сломать, иди и пытайся еще")
    else:
        bot.send_message(message.chat.id, "Никакой уникальности, придумай что то другое")
        bot.register_next_step_handler_by_chat_id(message.chat.id, process_user_name)

def finish_create_game(message: Any, description: str) -> None:
    """
    Завершает создание игры, устанавливая уровень сложности.
    
    Args:
        message (Any): Объект сообщения с уровнем сложности
        description (str): Описание игры
        
    Returns:
        None
    """
    levels: List[str] = ['легко', 'нормально', 'сложно']
    level: str = message.text.lower()
    
    if level in levels:
        tg_id: int = message.from_user.id
        player1: int = db.select_player1_by_tg_id(tg_id)[0]
        db.create_game(player1, description, level)
        bot.send_message(message.chat.id, "Игра успешно создана")
    else:
        bot.send_message(message.chat.id, "Уровень введен неправильно. Введите уровень заново")
        bot.register_next_step_handler_by_chat_id(message.chat.id, finish_create_game, description)

def process_create_game(message: Any) -> None:
    """
    Обрабатывает описание игры и запрашивает уровень сложности.
    
    Args:
        message (Any): Объект сообщения с описанием игры
        
    Returns:
        None
    """
    description: str = message.text
    bot.send_message(message.chat.id, "Введи сложность игры: леко, нормально, сложно")
    bot.register_next_step_handler_by_chat_id(message.chat.id, finish_create_game, description)

@bot.message_handler(commands=["show_unfinished_games"])
def show_unfinished_games(message: Any) -> None:
    """
    Показывает список незавершенных игр пользователя.
    
    Args:
        message (Any): Объект сообщения от пользователя
        
    Returns:
        None
    """
    tg_id: int = message.from_user.id
    player1: int = db.select_player1_by_tg_id(tg_id)[0]
    games: List[Tuple] = db.select_games(player1)
    msg: str = ""
    
    for game in games:
        row: str = f'айди игры - {game[0]}, описание - {game[3]}\n'
        msg += row
        
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=["create_game"])
def create_game(message: Any) -> None:
    """
    Начинает процесс создания новой игры.
    
    Args:
        message (Any): Объект сообщения от пользователя
        
    Returns:
        None
    """
    user_id: int = message.from_user.id 
    if db.if_profile_exist(user_id):
        bot.send_message(message.chat.id, "Введи описание игры")
        bot.register_next_step_handler_by_chat_id(message.chat.id, process_create_game)
    else:
        bot.send_message(message.chat.id, "Мамкин хакер, иди профиль создай!!!")

def process_play_game(message: Any) -> None:
    """
    Запускает игру по указанному ID и отображает текущее состояние доски.
    
    Args:
        message (Any): Объект сообщения с ID игры
        
    Returns:
        None
        
    Raises:
        TypeError: В случае ошибок при обработке SVG/FEN
    """
    game_id: str = message.text
    bot.send_message(message.chat.id, f"Игра с ID - {game_id} запущена")
    image_path: Path = Path('image_base') / game_id

    try:
        if check_path_svg(game_id + ".png"):
            send_photo(image_path.with_suffix(".png"), message.chat.id)
        else:
            fen: str = db.select_fen(game_id)[0]
            board: chess.Board = chess.Board(fen)
            svg_data: str = chess.svg.board(board=board)

            with open(image_path.with_suffix(".svg"), "w", encoding="utf-8") as f:
                f.write(svg_data)

            drawing = svg2rlg(image_path.with_suffix(".svg"))
            renderPM.drawToFile(drawing, image_path.with_suffix(".png"), fmt="PNG")
            send_photo(image_path.with_suffix(".png"), message.chat.id)
            
        bot.send_message(message.chat.id, "Введите ваш ход, пример: е2е4")
        bot.register_next_step_handler_by_chat_id(message.chat.id, next_move, game_id)

    except TypeError as E:
        bot.send_message(message.chat.id, str(E))

@bot.message_handler(commands=["play_game"])
def play_game(message: Any) -> None:
    """
    Запрашивает ID игры для начала игры.
    
    Args:
        message (Any): Объект сообщения от пользователя
        
    Returns:
        None
    """
    bot.send_message(message.chat.id, "Напиши ID игры в которую хочешь поиграть")
    bot.register_next_step_handler_by_chat_id(message.chat.id, process_play_game)

def check_path_svg(file_name: str) -> bool:
    """
    Проверяет существование файла с изображением доски.
    
    Args:
        file_name (str): Имя файла для проверки
        
    Returns:
        bool: True если файл существует, иначе False
    """
    path: Path = Path('image_base') / file_name
    return path.exists()

def send_photo(image_path: Path, chat_id: int) -> None:
    """
    Отправляет фото шахматной доски в чат.
    
    Args:
        image_path (Path): Путь к файлу изображения
        chat_id (int): ID чата для отправки
        
    Returns:
        None
    """
    with open(image_path, "rb") as image:
        bot.send_photo(chat_id, image)

def next_move(message: Any, game_id: str) -> None:
    """
    Обрабатывает ход игрока и обновляет состояние игры.
    
    Args:
        message (Any): Объект сообщения с ходом игрока
        game_id (str): ID текущей игры
        
    Returns:
        None
    """
    image_path: Path = Path('image_base') / game_id
    text: str = message.text

    if text == "exit":
        bot.send_message(message.chat.id, "Игра приостановлена")
    else:
        fen: str = db.select_fen(game_id)[0]
        board: chess.Board = chess.Board(fen)
        result: Dict[str, Any] = push(board, text, game_id)

        if result["finish"]:
            delete_image(game_id)
            bot.send_message(message.chat.id, result["message"])
            
            if result["message"] == "Мат! Победил кожаный":
                win_numeral: int = int(db.select_win(message.from_user.id)[0]) + 1
                db.update_win(message.from_user.id, win_numeral)
            elif result["message"] == "Мат! Победило ведро с гвоздями":
                lose_numeral: int = int(db.select_lose(message.from_user.id)[0]) + 1
                db.update_lose(message.from_user.id, lose_numeral)
            else:
                draw_numeral: int = int(db.select_draw(message.from_user.id)[0]) + 1
                db.update_draw(message.from_user.id, draw_numeral)

        elif not result["finish"] and result["message"] != "illegal_move":
            board: chess.Board = result["board"]
            db.update_fen(board.fen(), game_id)
            send_photo(image_path.with_suffix(".png"), message.chat.id)
            bot.send_message(message.chat.id, result["message"])
            bot.send_message(message.chat.id, "Введи следующий ход")
            bot.register_next_step_handler_by_chat_id(message.chat.id, next_move, game_id)

        elif not result["finish"] and result["message"] == "illegal_move":
            bot.send_message(message.chat.id, result["message"])
            bot.send_message(message.chat.id, "Ход невозможен. Введите другой ход")
            bot.register_next_step_handler_by_chat_id(message.chat.id, next_move, game_id)

def delete_image(game_id: str) -> None:
    """
    Удаляет файлы изображений для указанной игры.
    
    Args:
        game_id (str): ID игры для удаления изображений
        
    Returns:
        None
    """
    image_path: Path = Path('image_base') / game_id
    svg_path: Path = image_path.with_suffix(".svg")
    png_path: Path = image_path.with_suffix(".png")
    
    if svg_path.exists():
        os.remove(svg_path)
    if png_path.exists():
        os.remove(png_path)

@bot.message_handler(func=check_word)
def handler_all(message: Any) -> None:
    """
    Обрабатывает все текстовые сообщения, не соответствующие командам.
    
    Args:
        message (Any): Объект сообщения от пользователя
        
    Returns:
        None
    """
    bot.send_message(message.chat.id, "Ты русский??? Скажи нормально")


    



if __name__ == "__main__":
    bot.polling(none_stop=True)

    

