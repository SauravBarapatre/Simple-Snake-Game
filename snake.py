import curses
import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional

Coord = Tuple[int, int]


@dataclass
class GameState:
    width: int
    height: int
    rng: random.Random
    snake: List[Coord]
    direction: Coord
    food: Coord
    score: int
    alive: bool

    @classmethod
    def new(cls, width: int, height: int, seed: Optional[int] = None) -> "GameState":
        rng = random.Random(seed)
        start = (height // 2, width // 2)
        snake = [start, (start[0], start[1] - 1), (start[0], start[1] - 2)]
        direction = (0, 1)
        state = cls(width, height, rng, snake, direction, (0, 0), 0, True)
        state.food = state.spawn_food()
        return state

    def reset(self) -> None:
        start = (self.height // 2, self.width // 2)
        self.snake = [start, (start[0], start[1] - 1), (start[0], start[1] - 2)]
        self.direction = (0, 1)
        self.score = 0
        self.alive = True
        self.food = self.spawn_food()

    def change_direction(self, new_dir: Coord) -> None:
        if (new_dir[0] == -self.direction[0]) and (new_dir[1] == -self.direction[1]):
            return
        self.direction = new_dir

    def step(self) -> None:
        if not self.alive:
            return
        head_y, head_x = self.snake[0]
        dy, dx = self.direction
        new_head = (head_y + dy, head_x + dx)

        if (
            new_head[0] < 0
            or new_head[0] >= self.height
            or new_head[1] < 0
            or new_head[1] >= self.width
        ):
            self.alive = False
            return

        if new_head in self.snake:
            self.alive = False
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def spawn_food(self) -> Coord:
        free = [
            (y, x)
            for y in range(self.height)
            for x in range(self.width)
            if (y, x) not in self.snake
        ]
        if not free:
            self.alive = False
            return self.snake[0]
        return self.rng.choice(free)


def _draw(stdscr: "curses._CursesWindow", state: GameState, paused: bool) -> None:
    stdscr.erase()
    height, width = state.height, state.width

    for y in range(height + 2):
        stdscr.addch(y, 0, "#")
        stdscr.addch(y, width + 1, "#")
    for x in range(width + 2):
        stdscr.addch(0, x, "#")
        stdscr.addch(height + 1, x, "#")

    food_y, food_x = state.food
    stdscr.addch(food_y + 1, food_x + 1, "*")

    for idx, (y, x) in enumerate(state.snake):
        ch = "@" if idx == 0 else "o"
        stdscr.addch(y + 1, x + 1, ch)

    status = f"Score: {state.score}"
    if paused:
        status += "  [PAUSED]"
    if not state.alive:
        status += "  [GAME OVER] Press R to restart or Q to quit"
    stdscr.addstr(height + 3, 0, status[: width + 2])
    stdscr.refresh()


def _handle_key(key: int, state: GameState) -> Optional[str]:
    if key in (ord("q"), ord("Q")):
        return "quit"
    if key in (ord("r"), ord("R")):
        state.reset()
        return "restart"

    if key in (curses.KEY_UP, ord("w"), ord("W")):
        state.change_direction((-1, 0))
    elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
        state.change_direction((1, 0))
    elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
        state.change_direction((0, -1))
    elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
        state.change_direction((0, 1))

    return None


def run(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    height, width = 20, 30
    state = GameState.new(width, height)

    tick_seconds = 0.12
    last_tick = time.time()
    paused = False

    while True:
        now = time.time()
        key = stdscr.getch()
        if key != -1:
            if key in (ord("p"), ord("P"), ord(" ")):
                paused = not paused
            else:
                action = _handle_key(key, state)
                if action == "quit":
                    break

        if not paused and state.alive and (now - last_tick) >= tick_seconds:
            state.step()
            last_tick = now

        _draw(stdscr, state, paused)
        time.sleep(0.01)


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
