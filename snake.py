"""
贪吃蛇 (Snake) —— 学习 Git / GitHub 用的示例项目

运行方式:
    pip install pygame
    python snake.py

操作:
    方向键 / WASD  控制方向
    空格           暂停 / 继续
    R              游戏结束后重新开始
    ESC            退出游戏
"""

import json
import random
import sys
from pathlib import Path

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
YELLOW = (240, 200, 80)
WHITE = (240, 240, 240)
GREY = (150, 150, 160)

HIGHSCORE_FILE = Path(__file__).with_name("highscore.json")

# 四个方向: (x 变化, y 变化)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def load_highscore():
    """读取本地保存的最高分，文件不存在或损坏时返回 0。"""
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as fp:
            return int(json.load(fp).get("highscore", 0))
    except (OSError, ValueError, TypeError):
        return 0


def save_highscore(score):
    """把最高分写入本地文件。"""
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as fp:
            json.dump({"highscore": int(score)}, fp, ensure_ascii=False)
    except OSError:
        pass  # 没有写权限时静默忽略，不影响游戏


class SnakeGame:
    """贪吃蛇游戏主逻辑。"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("贪吃蛇 Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 18)
        self.big_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.highscore = load_highscore()
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
        self.paused = False

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
            self.end_game()
            return

        # 撞到自己(尾巴即将移开的格子不算)
        if new_head in self.snake[:-1]:
            self.end_game()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def end_game(self):
        """结束游戏，并顺手更新最高分。"""
        self.game_over = True
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    # ---------- 绘制 ----------
    def draw_cell(self, pos, color):
        rect = pygame.Rect(pos[0] * CELL, pos[1] * CELL, CELL, CELL)
        pygame.draw.rect(self.screen, color, rect)

    def draw_hud(self):
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 8))

        best_text = self.small_font.render(f"最高分: {self.highscore}", True, YELLOW)
        self.screen.blit(best_text, (WIDTH - best_text.get_width() - 10, 12))

    def draw_center_text(self, lines, color=WHITE):
        """在屏幕中间画几行文字。"""
        total = len(lines)
        for index, (text, font) in enumerate(lines):
            surface = font.render(text, True, color if index == 0 else WHITE)
            y = HEIGHT // 2 - (total * 30) // 2 + index * 44
            self.screen.blit(surface, surface.get_rect(center=(WIDTH // 2, y)))

    def draw(self):
        self.screen.fill(BLACK)

        self.draw_cell(self.food, RED)

        for index, segment in enumerate(self.snake):
            color = GREEN if index == 0 else DARK_GREEN
            self.draw_cell(segment, color)

        self.draw_hud()

        if self.game_over:
            self.draw_center_text(
                [("GAME OVER", self.big_font)],
                color=RED,
            )
            tip = self.font.render("按 R 重新开始 / ESC 退出", True, WHITE)
            self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
        elif self.paused:
            self.draw_center_text([("已暂停", self.big_font)], color=YELLOW)
            tip = self.font.render("按空格继续", True, WHITE)
            self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        pygame.display.flip()

    # ---------- 主循环 ----------
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

            if not self.game_over and not self.paused:
                self.step()

            self.draw()
            self.clock.tick(12)   # 每秒 12 帧 = 速度

    def handle_key(self, key):
        keys = {
            pygame.K_UP: UP, pygame.K_w: UP,
            pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
            pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
            pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
        }
        if key == pygame.K_ESCAPE:
            self.quit()
        if key == pygame.K_SPACE and not self.game_over:
            self.paused = not self.paused
            return
        if key == pygame.K_r and self.game_over:
            self.reset()
            return
        if key in keys:
            new_dir = keys[key]
            # 不能 180 度掉头
            if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
                self.next_direction = new_dir

    def quit(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    SnakeGame().run()
