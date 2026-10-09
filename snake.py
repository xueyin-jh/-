"""
贪吃蛇 (Snake) —— 学习 Git / GitHub 用的示例项目

运行方式:
    pip install pygame
    python snake.py

操作:
    方向键 / WASD  控制方向
    ESC            退出游戏
"""

import random
import sys

import pygame

# ---------- 基础配置 ----------
CELL = 20                     # 每个格子的像素大小
COLS, ROWS = 30, 24           # 游戏区域 30 列 x 24 行
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL

BLACK = (18, 18, 24)
DARK = (32, 34, 44)
GREEN = (80, 220, 120)
DARK_GREEN = (46, 160, 88)
RED = (235, 80, 80)
WHITE = (240, 240, 240)

# 四个方向: (x 变化, y 变化)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class SnakeGame:
    """贪吃蛇游戏主逻辑。"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("贪吃蛇 Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.reset()

    def reset(self):
        """把游戏恢复到初始状态。"""
        center = (COLS // 2, ROWS // 2)
        self.snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        """在空的格子里随机放一个食物。"""
        empty = [
            (x, y)
            for x in range(COLS)
            for y in range(ROWS)
            if (x, y) not in self.snake
        ]
        return random.choice(empty)

    # ---------- 逻辑更新 ----------
    def step(self):
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # 撞墙
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self.game_over = True
            return

        # 撞到自己(尾巴即将移开的格子不算)
        if new_head in self.snake[:-1]:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    # ---------- 绘制 ----------
    def draw_cell(self, pos, color):
        rect = pygame.Rect(pos[0] * CELL, pos[1] * CELL, CELL, CELL)
        pygame.draw.rect(self.screen, color, rect)

    def draw(self):
        self.screen.fill(BLACK)

        self.draw_cell(self.food, RED)

        for index, segment in enumerate(self.snake):
            color = GREEN if index == 0 else DARK_GREEN
            self.draw_cell(segment, color)

        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 8))

        if self.game_over:
            over = self.big_font.render("GAME OVER", True, RED)
            self.screen.blit(
                over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            )
            tip = self.font.render("按 R 重新开始 / ESC 退出", True, WHITE)
            self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        pygame.display.flip()

    # ---------- 主循环 ----------
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

            if not self.game_over:
                self.step()

            self.draw()
            self.clock.tick(10)   # 每秒 10 帧 = 速度

    def handle_key(self, key):
        keys = {
            pygame.K_UP: UP, pygame.K_w: UP,
            pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
            pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
            pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
        }
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if key == pygame.K_r and self.game_over:
            self.reset()
            return
        if key in keys:
            new_dir = keys[key]
            # 不能 180 度掉头
            if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
                self.next_direction = new_dir


if __name__ == "__main__":
    SnakeGame().run()
