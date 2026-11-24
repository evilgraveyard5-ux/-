import random
from models import Entity, Board


class Player(Entity):
    """Базовый класс игрока со статистикой попаданий."""

    def __init__(self, name: str, board: Board):
        super().__init__(name)
        self._board = board
        self._shots_fired = 0
        self._hits_count = 0
        self._misses_count = 0

    @property
    def board(self) -> Board:
        return self._board

    def record_shot(self, is_hit: bool):
        self._shots_fired += 1
        if is_hit:
            self._hits_count += 1
        else:
            self._misses_count += 1

    def stats(self) -> str:
        accuracy = (self._hits_count / self._shots_fired * 100) if self._shots_fired else 0.0
        return (
            f"{self._name}: выстрелов={self._shots_fired}, "
            f"попаданий={self._hits_count}, промахов={self._misses_count}, "
            f"точность={accuracy:.1f}%"
        )

    def info(self) -> str:
        return self.stats()

    def choose_target(self, enemy_board: Board) -> tuple[int, int]:
        raise NotImplementedError("Подкласс должен реализовать choose_target.")

    def __str__(self) -> str:
        return f"Игрок '{self._name}'"

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "name": self._name,
            "shots_fired": self._shots_fired,
            "hits_count": self._hits_count,
            "misses_count": self._misses_count,
            "board": self._board.to_dict(),
        }


class HumanPlayer(Player):
    def choose_target(self, enemy_board: Board) -> tuple[int, int]:
        raise RuntimeError("Для человека цель задаётся командой shot.")


class BotPlayer(Player):
    def choose_target(self, enemy_board: Board) -> tuple[int, int]:
        candidates = [
            (r, c)
            for r in range(enemy_board.size)
            for c in range(enemy_board.size)
            if (r, c) not in enemy_board._shots
        ]
        if not candidates:
            raise ValueError("Нет доступных клеток для выстрела.")
        return random.choice(candidates)