import sqlite3
from typing import List, Tuple, Optional, Any, Union
from queries import Queries as Q


class DataBase:
    """
    Класс для работы с базой данных SQLite.
    
    Обеспечивает подключение к базе данных и выполнение основных операций
    для управления пользователями и шахматными играми.
    """
    
    def __init__(self, name: str) -> None:
        """
        Инициализирует объект базы данных.
        
        Args:
            name (str): Имя файла базы данных
        """
        self.name: str = name
        self.cur: Optional[sqlite3.Cursor] = None
        self.con: Optional[sqlite3.Connection] = None
    
    def connect(self) -> None:
        """
        Устанавливает подключение к базе данных.
        
        Raises:
            sqlite3.Error: В случае ошибки подключения к базе данных
        """
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

    def show_tables(self) -> None:
        """
        Выводит список всех таблиц в базе данных.
        
        Returns:
            None
        """
        self.connect()
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        print(self.cur.fetchall())
        self.close()

    def close(self) -> None:
        """
        Закрывает подключение к базе данных с сохранением изменений.
        
        Returns:
            None
        """
        self.con.commit()
        self.con.close()

    def select_all_user_names(self) -> Union[List[str], bool]:
        """
        Получает список всех имен пользователей из базы данных.
        
        Returns:
            Union[List[str], bool]: Список имен пользователей или False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.SELECT_USER_NAMES)
            all_user_names: List[Tuple] = self.cur.fetchall()
            all_user_names_processed: List[str] = self.process_lift(all_user_names)
            return all_user_names_processed
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def create_user(self, user_name: str, win: int, lose: int, draw: int, tg_id: int) -> bool:
        """
        Создает нового пользователя в базе данных.
        
        Args:
            user_name (str): Имя пользователя
            win (int): Количество побед
            lose (int): Количество поражений
            draw (int): Количество ничьих
            tg_id (int): Telegram ID пользователя
            
        Returns:
            bool: True при успешном создании, False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.CREATE_USER, (user_name, win, lose, draw, tg_id))
            return True
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def update_win(self, win: int, tg_id: int) -> bool:
        """
        Обновляет количество побед пользователя.
        
        Args:
            win (int): Новое количество побед
            tg_id (int): Telegram ID пользователя
            
        Returns:
            bool: True при успешном обновлении, False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.UPDATE_WIN, (win, tg_id))
            return True
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()
    
    def update_lose(self, lose: int, tg_id: int) -> bool:
        """
        Обновляет количество поражений пользователя.
        
        Args:
            lose (int): Новое количество поражений
            tg_id (int): Telegram ID пользователя
            
        Returns:
            bool: True при успешном обновлении, False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.UPDATE_LOSE, (lose, tg_id))
            return True
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()
        
    def update_draw(self, draw: int, tg_id: int) -> Union[Tuple, bool]:
        """
        Обновляет количество ничьих пользователя.
        
        Args:
            draw (int): Новое количество ничьих
            tg_id (int): Telegram ID пользователя
            
        Returns:
            Union[Tuple, bool]: Результат запроса или False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.UPDATE_DRAW, (draw, tg_id))
            return self.cur.fetchone()
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def select_win(self, tg_id: int) -> Union[Tuple, bool]:
        """
        Получает количество побед пользователя.
        
        Args:
            tg_id (int): Telegram ID пользователя
            
        Returns:
            Union[Tuple, bool]: Количество побед или False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.SELECT_WIN_BY_TG_ID, (tg_id,))
            return self.cur.fetchone()
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def select_lose(self, tg_id: int) -> Union[Tuple, bool]:
        """
        Получает количество поражений пользователя.
        
        Args:
            tg_id (int): Telegram ID пользователя
            
        Returns:
            Union[Tuple, bool]: Количество поражений или False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.SELECT_LOSE_BY_TG_ID, (tg_id,))
            return self.cur.fetchone()
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()
    
    def select_draw(self, tg_id: int) -> Union[Tuple, bool]:
        """
        Получает количество ничьих пользователя.
        
        Args:
            tg_id (int): Telegram ID пользователя
            
        Returns:
            Union[Tuple, bool]: Количество ничьих или False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.SELECT_DRAW_BY_TG_ID, (tg_id,))
            return self.cur.fetchone()
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def if_profile_exist(self, tg_id: int) -> bool:
        """
        Проверяет существование профиля пользователя.
        
        Args:
            tg_id (int): Telegram ID пользователя
            
        Returns:
            bool: True если профиль существует, False если нет или при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.SELECT_CHECK_PROFILE, (tg_id,))
            if self.cur.fetchone() is not None:
                return True
            else:
                return False
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()
        
    def select_games(self, player_id: int, finished: bool = False) -> Union[List[Tuple], bool]:
        """
        Получает список игр пользователя.
        
        Args:
            player_id (int): ID игрока
            finished (bool, optional): Фильтр по завершенным играм. Defaults to False.
            
        Returns:
            Union[List[Tuple], bool]: Список игр или False при ошибке
        """
        self.connect()
        try:
            if not finished:
                self.cur.execute(Q.SELECT_GAMES_BY_PLAYER_ID, (player_id,))
            else:
                self.cur.execute(Q.SELECT_FINISHED_GAMES_BY_PLAYER_ID, (player_id,))
            return self.cur.fetchall()        
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def select_fen(self, game_id: str) -> Union[Tuple, bool]:
        """
        Получает FEN-строку для указанной игры.
        
        Args:
            game_id (str): ID игры
            
        Returns:
            Union[Tuple, bool]: FEN-строка или False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.SELECT_FEN_BY_GAME_ID, (game_id,))
            return self.cur.fetchone()
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def select_level(self, game_id: str) -> Union[Tuple, bool]:
        """
        Получает уровень сложности для указанной игры.
        
        Args:
            game_id (str): ID игры
            
        Returns:
            Union[Tuple, bool]: Уровень сложности или False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.SELECT_GAME_LEVEL_BY_GAME_ID, (game_id,))
            return self.cur.fetchone()
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def update_fen(self, fen: str, game_id: str) -> bool:
        """
        Обновляет FEN-строку для указанной игры.
        
        Args:
            fen (str): Новая FEN-строка
            game_id (str): ID игры
            
        Returns:
            bool: True при успешном обновлении, False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.UPDATE_FEN_BY_GAME_ID, (fen, game_id))
            return True
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()
    
    def create_game(self, player_id: int, description: str = "", level: str = 'средний') -> bool:
        """
        Создает новую игру в базе данных.
        
        Args:
            player_id (int): ID игрока
            description (str, optional): Описание игры. Defaults to "".
            level (str, optional): Уровень сложности. Defaults to 'средний'.
            
        Returns:
            bool: True при успешном создании, False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.CREATE_GAME, (player_id, description, level))
            return True
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def select_player1_by_tg_id(self, tg_id: int) -> Union[Tuple, bool]:
        """
        Получает ID игрока по Telegram ID.
        
        Args:
            tg_id (int): Telegram ID пользователя
            
        Returns:
            Union[Tuple, bool]: ID игрока или False при ошибке
        """
        self.connect()
        try:
            self.cur.execute(Q.SELECT_PLAYER_ID_BY_TG_ID, (tg_id,))
            return self.cur.fetchone()
        except Exception as E:
            print(E)
            return False
        finally:
            self.close()

    def process_lift(self, spisok: List[Tuple]) -> List[Any]:
        """
        Преобразует список кортежей в плоский список.
        
        Args:
            spisok (List[Tuple]): Список кортежей для обработки
            
        Returns:
            List[Any]: Плоский список значений
        """
        chto_to: List[Any] = []
        for i in spisok:
            chto_to.append(i[0])
        return chto_to


# Пример использования:
# db = DataBase(name="GigaBase.db")
# a = db.select_all_user_names()
# print(a)