"""Игра «Змейка»."""

import sys
from random import choice

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (93, 216, 228)

BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = LIGHT_BLUE
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

SPEED = 20

KEY_TO_DIRECTION = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
}

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для объектов, расположенных на игровом поле."""

    def __init__(self, position=SCREEN_CENTER, body_color=None):
        """Задать позицию и цвет объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовать объект. Должен быть переопределён в наследниках."""
        raise NotImplementedError(
            f'В классе {self.__class__.__name__} не определён метод draw'
        )

    def draw_cell(self, position, color=None, border_color=BORDER_COLOR):
        """Отрисовать одну ячейку поля по заданным координатам."""
        if color is None:
            color = self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border_color is not None:
            pg.draw.rect(screen, border_color, rect, 1)


class Apple(GameObject):
    """Яблоко, размещаемое в свободной клетке игрового поля."""

    def __init__(self, body_color=APPLE_COLOR):
        """Создать яблоко в случайной клетке."""
        super().__init__(body_color=body_color)
        self.randomize_position()

    def randomize_position(self, occupied_positions=()):
        """Поместить яблоко в случайную клетку, свободную от змейки.

        Args:
            occupied_positions: Координаты занятых клеток.

        Raises:
            ValueError: Если на поле не осталось свободных клеток.
        """
        occupied = set(occupied_positions)
        free_cells = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied
        ]
        if not free_cells:
            raise ValueError('На игровом поле не осталось свободных клеток')
        self.position = choice(free_cells)

    def draw(self):
        """Отрисовать яблоко."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка: движение, рост, изменение направления и сброс состояния."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Инициализировать змейку длиной в одну клетку."""
        super().__init__(body_color=body_color)
        self.reset()

    def update_direction(self):
        """Применить отложенное изменение направления движения."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Передвинуть змейку на одну клетку с переходом через границы."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Отрисовать голову змейки и стереть след хвоста."""
        if self.last is not None:
            self.draw_cell(
                self.last,
                BOARD_BACKGROUND_COLOR,
                BOARD_BACKGROUND_COLOR,
            )
        self.draw_cell(self.get_head_position())

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Вернуть змейку к начальному состоянию в центре поля."""
        self.length = 1
        self.positions = [SCREEN_CENTER]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать закрытие окна и допустимые повороты змейки."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        if event.type == pg.KEYDOWN and event.key in KEY_TO_DIRECTION:
            proposed = KEY_TO_DIRECTION[event.key]
            current = game_object.direction
            opposite = (-current[0], -current[1])
            if proposed != opposite and game_object.next_direction is None:
                game_object.next_direction = proposed


def main():
    """Запустить игровой цикл, обрабатывать движение, яблоки и столкновения."""
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() == apple.position:
            snake.length += 1
            try:
                apple.randomize_position(snake.positions)
            except ValueError:
                snake.reset()
                screen.fill(BOARD_BACKGROUND_COLOR)
                apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
