import json
from pathlib import Path
from models import Board
from players import HumanPlayer, BotPlayer, Player


class Game:
    """Контроллер игры (композиция: игроки и поля)."""

    SAVE_FILE = Path("save_game.json")

    def __init__(self, board_size: int = 6):
        self._human = HumanPlayer("Игрок", Board(board_size))
        self._bot = BotPlayer("Бот", Board(board_size))
        self._radar_charges = 2
        self._commands = {
            "help": (self.cmd_help, "Показать список команд"),
            "place": (self.cmd_place, "Расставить корабль: place <имя> <ряд> <кол> <длина 1..4> <h|v>"),
            "shot": (self.cmd_shot, "Выстрел по полю бота: shot <ряд> <кол>"),
            "scan": (self.cmd_scan, "Радар 2x2 по полю бота: scan <ряд> <кол>"),
            "board": (self.cmd_board, "Показать своё поле и поле бота"),
            "stats": (self.cmd_stats, "Статистика попаданий"),
            "reset": (self.cmd_reset, "Начать новую игру и удалить сохранение"),
            "exit": (self.cmd_exit, "Сохранить и выйти"),
        }
        self._load_state()
        if not self._bot.board.ships:
            self._setup_bot_ships()

    def _setup_bot_ships(self):
        presets = [
            ("Катер", (0, 0), 1, "h"),
            ("Эсминец", (2, 1), 2, "h"),
            ("Крейсер", (4, 3), 2, "v"),
        ]
        for name, start, length, orient in presets:
            try:
                self._bot.board.place_ship(name, start, length, orient)
            except ValueError:
                pass

    @staticmethod
    def _parse_coord(r_str: str, c_str: str) -> tuple[int, int]:
        try:
            return int(r_str), int(c_str)
        except ValueError as exc:
            raise ValueError("Координаты должны быть целыми числами.") from exc

    def cmd_help(self, args: list[str]):
        print("\n=== КОМАНДЫ ===")
        for name, (_, desc) in self._commands.items():
            print(f"  {name:<8} — {desc}")

    def cmd_place(self, args: list[str]):
        if len(args) != 5:
            raise ValueError("Формат: place <имя> <ряд> <кол> <длина> <h|v>")
        name, r_s, c_s, len_s, orient = args
        coord = self._parse_coord(r_s, c_s)
        try:
            length = int(len_s)
        except ValueError as exc:
            raise ValueError("Длина корабля должна быть числом.") from exc

        ship = self._human.board.place_ship(name, coord, length, orient)
        print(f"Поставлен: {ship}")

    def _polymorphic_turn(self, attacker: Player, defender_board: Board, target: tuple[int, int]):
        result = defender_board.receive_shot(target)
        is_hit = result in ("hit", "sunk")
        attacker.record_shot(is_hit)
        messages = {
            "miss": f"{attacker.name}: мимо по {target}.",
            "hit": f"{attacker.name}: ПОПАДАНИЕ по {target}!",
            "sunk": f"{attacker.name}: КОРАБЛЬ ПОТОПЛЕН на {target}!",
        }
        print(messages[result])

    def cmd_shot(self, args: list[str]):
        if len(args) != 2:
            raise ValueError("Формат: shot <ряд> <кол>")
        if not self._human.board.ships:
            raise ValueError("Сначала поставь хотя бы один свой корабль командой place.")

        target = self._parse_coord(args[0], args[1])
        self._polymorphic_turn(self._human, self._bot.board, target)

        if self._bot.board.all_sunk():
            print("Победа! Все корабли бота потоплены.")
            return

        bot_target = self._bot.choose_target(self._human.board)
        self._polymorphic_turn(self._bot, self._human.board, bot_target)

        if self._human.board.all_sunk():
            print("Поражение: бот потопил все твои корабли.")

    def cmd_scan(self, args: list[str]):
        if len(args) != 2:
            raise ValueError("Формат: scan <ряд> <кол>")
        if self._radar_charges <= 0:
            raise ValueError("Заряды радара закончились.")
        coord = self._parse_coord(args[0], args[1])
        found = self._bot.board.scan_area(coord)
        self._radar_charges -= 1
        print(f"Радар в квадрате 2x2 от {coord} нашёл палуб: {found} (осталось сканов: {self._radar_charges})")

    def cmd_board(self, args: list[str]):
        print("\n--- ТВОЁ ПОЛЕ ---")
        print(self._human.board.render(hide_ships=False))
        print("\n--- ПОЛЕ БОТА ---")
        print(self._bot.board.render(hide_ships=True))

    def cmd_stats(self, args: list[str]):
        print("\n--- СТАТИСТИКА ---")
        for p in (self._human, self._bot):
            print(p.info())

    def cmd_reset(self, args: list[str]):
        size = self._human.board.size
        self._human = HumanPlayer("Игрок", Board(size))
        self._bot = BotPlayer("Бот", Board(size))
        self._radar_charges = 2
        self._setup_bot_ships()
        if self.SAVE_FILE.exists():
            self.SAVE_FILE.unlink()
        print("Игра сброшена.")

    def cmd_exit(self, args: list[str]) -> bool:
        self._save_state()
        print(f"Состояние сохранено в {self.SAVE_FILE}. Выход.")
        return True

    def execute(self, raw_line: str) -> bool:
        parts = raw_line.strip().split()
        if not parts:
            return False
        cmd_name = parts[0].lower()
        args = parts[1:]
        if cmd_name not in self._commands:
            raise ValueError(f"Неизвестная команда '{cmd_name}'. Введите 'help'.")
        handler, _ = self._commands[cmd_name]
        res = handler(args)
        return bool(res)

    def _save_state(self):
        payload = {
            "radar_charges": self._radar_charges,
            "human": self._human.to_dict(),
            "bot": self._bot.to_dict(),
        }
        self.SAVE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_state(self):
        if not self.SAVE_FILE.exists():
            return
        try:
            data = json.loads(self.SAVE_FILE.read_text(encoding="utf-8"))
            self._radar_charges = data.get("radar_charges", 2)
            h = data["human"]
            b = data["bot"]
            self._human = HumanPlayer(h["name"], Board.from_dict(h["board"]))
            self._human._shots_fired = h.get("shots_fired", 0)
            self._human._hits_count = h.get("hits_count", 0)
            self._human._misses_count = h.get("misses_count", 0)

            self._bot = BotPlayer(b["name"], Board.from_dict(b["board"]))
            self._bot._shots_fired = b.get("shots_fired", 0)
            self._bot._hits_count = b.get("hits_count", 0)
            self._bot._misses_count = b.get("misses_count", 0)
            print(f"Загружено сохранение из {self.SAVE_FILE}.")
        except Exception as exc:
            print(f"Не удалось загрузить сохранение ({exc}), старт с чистого листа.")

    def __str__(self) -> str:
        return f"Game(радар={self._radar_charges}, {self._human}, {self._bot})"

    def run(self):
        print("=== МОРСКОЙ БОЙ ===")
        print("Введите 'help' для списка команд.")
        while True:
            try:
                line = input("\n> ")
                if self.execute(line):
                    break
            except ValueError as err:
                print(f"[Ошибка ввода/действия]: {err}")
            except Exception as err:
                print(f"[Непредвиденная ошибка]: {err}")