from abc import ABC, abstractmethod


class Entity(ABC):
    """Абстрактный базовый класс для сущностей на поле."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def info(self) -> str:
        pass


class Ship(Entity):
    """Корабль с проверкой размера и координат через @property."""

    def __init__(self, name: str, cells: list[tuple[int, int]]):
        super().__init__(name)
        self.cells = cells  # пойдёт через сеттер @cells.setter
        self._hits: set[tuple[int, int]] = set()

    @property
    def cells(self) -> list[tuple[int, int]]:
        return self._cells

    @cells.setter
    def cells(self, value: list[tuple[int, int]]):
        if not value or not isinstance(value, list):
            raise ValueError("Корабль должен занимать хотя бы одну клетку.")
        if len(value) > 4:
            raise ValueError("Размер корабля не может превышать 4 клетки.")
        self._cells = value

    @property
    def is_sunk(self) -> bool:
        return len(self._hits) >= len(self._cells)

    def register_hit(self, coord: tuple[int, int]) -> str:
        if coord in self._cells:
            self._hits.add(coord)
            return "sunk" if self.is_sunk else "hit"
        return "miss"

    def info(self) -> str:
        status = "потоплен" if self.is_sunk else f"ранен ({len(self._hits)}/{len(self._cells)})"
        return f"Корабль '{self._name}' [{status}]"

    def __str__(self) -> str:
        return self.info()

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "cells": [list(c) for c in self._cells],
            "hits": [list(h) for h in self._hits],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Ship":
        ship = cls(data["name"], [tuple(c) for c in data["cells"]])
        ship._hits = {tuple(h) for h in data.get("hits", [])}
        return ship


class Board:
    """Игровое поле (композиция: хранит список объектов Ship)."""

    def __init__(self, size: int = 6):
        self.size = size
        self._ships: list[Ship] = []
        self._shots: dict[tuple[int, int], str] = {}  # (r, c) -> 'hit' | 'miss'

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int):
        if not (4 <= value <= 10):
            raise ValueError("Размер поля должен быть от 4 до 10.")
        self._size = value

    @property
    def ships(self) -> list[Ship]:
        return self._ships

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self._size and 0 <= c < self._size

    def place_ship(self, name: str, start: tuple[int, int], length: int, orientation: str) -> Ship:
        if length < 1 or length > 4:
            raise ValueError("Длина корабля должна быть от 1 до 4.")
        orientation = orientation.lower()
        if orientation not in ("h", "v"):
            raise ValueError("Направление должно быть 'h' (горизонтально) или 'v' (вертикально).")

        r0, c0 = start
        cells = []
        for i in range(length):
            r = r0 + (i if orientation == "v" else 0)
            c = c0 + (i if orientation == "h" else 0)
            if not self._in_bounds(r, c):
                raise ValueError("Корабль выходит за пределы поля.")
            cells.append((r, c))

        occupied = {cell for ship in self._ships for cell in ship.cells}
        if any(cell in occupied for cell in cells):
            raise ValueError("Клетки уже заняты другим кораблём.")

        ship = Ship(name, cells)
        self._ships.append(ship)
        return ship

    def receive_shot(self, coord: tuple[int, int]) -> str:
        r, c = coord
        if not self._in_bounds(r, c):
            raise ValueError("Координата вне поля.")
        if coord in self._shots:
            raise ValueError("В эту клетку уже стреляли.")

        for ship in self._ships:
            if coord in ship.cells:
                res = ship.register_hit(coord)
                self._shots[coord] = "hit"
                return res

        self._shots[coord] = "miss"
        return "miss"

    def scan_area(self, top_left: tuple[int, int]) -> int:
        """Своя фича: радар проверяет квадрат 2x2 и возвращает число палуб."""
        r0, c0 = top_left
        if not self._in_bounds(r0, c0):
            raise ValueError("Координата радара вне поля.")
        ship_cells = {cell for ship in self._ships for cell in ship.cells}
        count = 0
        for dr in range(2):
            for dc in range(2):
                cell = (r0 + dr, c0 + dc)
                if self._in_bounds(*cell) and cell in ship_cells:
                    count += 1
        return count

    def all_sunk(self) -> bool:
        return len(self._ships) > 0 and all(ship.is_sunk for ship in self._ships)

    def render(self, hide_ships: bool = False) -> str:
        hit_cells = {ship_cell for ship in self._ships for ship_cell in ship._hits}
        all_ship_cells = {cell for ship in self._ships for cell in ship.cells}

        header = "   " + " ".join(str(c) for c in range(self._size))
        lines = [header]
        for r in range(self._size):
            row_chars = [str(r)]
            for c in range(self._size):
                coord = (r, c)
                if coord in hit_cells:
                    row_chars.append("X")
                elif coord in self._shots:
                    row_chars.append("o")
                elif not hide_ships and coord in all_ship_cells:
                    row_chars.append("S")
                else:
                    row_chars.append(".")
            lines.append("  " + " ".join(row_chars))
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.render(hide_ships=False)

    def to_dict(self) -> dict:
        return {
            "size": self._size,
            "ships": [s.to_dict() for s in self._ships],
            "shots": [[r, c, status] for (r, c), status in self._shots.items()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Board":
        board = cls(size=data.get("size", 6))
        board._ships = [Ship.from_dict(s) for s in data.get("ships", [])]
        board._shots = {(item[0], item[1]): item[2] for item in data.get("shots", [])}
        return board