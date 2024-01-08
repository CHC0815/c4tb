import pickle
import sqlite3
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFont


class GameState:
    def __init__(self, draw: bool, win: bool, winner: int | None):
        self.draw = False
        self.win = False
        self.winner = None


class ConnectFour:
    def __init__(self, id: int):
        self.db: sqlite3.Connection = sqlite3.connect("connectfourbot.db")
        self.id = id
        self.board = [0 for _ in range(42)]

    def save(self):
        self.db.execute(
            "INSERT OR REPLACE INTO games (id, board) VALUES (?, ?)",
            (self.id, pickle.dumps(self)),
        )
        self.db.commit()

    def render(self) -> BytesIO:
        w, h = 400, 400
        img = Image.new("RGB", (w, h), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle(((20, 20), (380, 380)), fill="#000000", outline="red")
        bio = BytesIO()
        img.save(bio, "JPEG")
        bio.seek(0)
        return bio

    def step(self, action: int) -> GameState:
        state = self._half_step(action, 0)
        if state.draw or state.win:
            return state

        state = self._half_step(action, 1)
        if state.draw or state.win:
            return state

        return GameState(False, False, None)

    def _half_step(self, action: int, player: int) -> GameState:
        valid_moves = self._get_valid_moves()
        if -1 in valid_moves:
            return GameState(True, False, None)

        if action not in valid_moves:
            return GameState(False, False, (player + 1) % 2)

        self._drop_piece(action, player)
        if self._check_win_board(player):
            return GameState(False, True, player)

        return GameState(False, False, None)

    @staticmethod
    def load(id: int) -> "ConnectFour":
        return ConnectFour(id)

    def _get_valid_moves(self) -> list[int]:
        valid_moves = [col for col in range(7) if self.board[col] == 0]
        if len(valid_moves) == 0:
            return [-1]  # draw
        return valid_moves

    def _drop_piece(self, col: int, piece: int):
        grid: np.ndarray = np.array(self.board).reshape((6, 7))
        for row in range(6 - 1, -1, -1):
            if grid[row][col] == 0:
                break
        grid[row][col] = piece  # type:ignore
        self.board = grid.flatten().tolist()

    def _check_win_board(self, piece: int) -> bool:
        rows = 6
        columns = 7
        inarow = 4
        grid: np.ndarray = np.array(self.board).reshape((rows, columns))
        # horizontal
        for row in range(rows):
            for col in range(columns - (inarow - 1)):
                window = list(grid[row, col : col + inarow])
                if window.count(piece) == inarow:
                    return True
        # vertical
        for row in range(rows - (inarow - 1)):
            for col in range(columns):
                window = list(grid[row : row + inarow, col])
                if window.count(piece) == inarow:
                    return True
        # positive diagonal
        for row in range(rows - (inarow - 1)):
            for col in range(columns - (inarow - 1)):
                window = list(grid[range(row, row + inarow), range(col, col + inarow)])
                if window.count(piece) == inarow:
                    return True
        # negative diagonal
        for row in range(inarow - 1, rows):
            for col in range(columns - (inarow - 1)):
                window = list(grid[range(row, row - inarow, -1), range(col, col + inarow)])
                if window.count(piece) == inarow:
                    return True
        return False

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["db"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.db = sqlite3.connect("connectfourbot.db")
