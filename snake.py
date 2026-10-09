"""
贪吃蛇 (Snake) —— 学习 Git / GitHub 用的示例项目

运行方式:
    pip install pygame
    python snake.py

操作:
    1 / 2 / 3      开始界面选择难度(简单 / 普通 / 困难)
    方向键 / WASD  控制方向
    空格           暂停 / 继续
    R              游戏结束后重新开始
    M              回到开始界面(重新选难度)
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

BACKGROUND = (18, 18, 24)
GRID_LIGHT = (26, 27, 34)
GRID_DARK = (22, 23, 30)
GREEN = (80, 220, 120)
DARK_GREEN = (46, 160, 88)
RED = (235, 80, 80)
YELLOW = (240, 200, 80)
WHITE = (240, 240, 240)
GREY = (140, 142, 155)

HIGHSCORE_FILE = Path(__file__).with_name("highscore.json")

# 四个方向: (x 变化, y 变化)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 难度: 名称 -> (起始速度, 每分加速)
LEVELS = {
    1: ("简单", 8.0, 0.30),
    2: ("普通", 12.0, 0.55),
    3: ("困难", 18.0, 0.90),
}
MAX_SPEED = 30.0

# 键盘上的 1 / 2 / 3 -> 难度编号
LEVEL_KEYS = {pygame.K_1: 1, pygame.K_KP1: 1,
              pygame.K_2: 2, pygame.K_KP2: 2,
              pygame.K_3: 3, pygame.K_KP3: 3}


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
        self.level = 2
        self.state = "menu"       # menu / playing / paused / over
        self.reset()

    def reset(self):
        """把游戏恢复到初始状态(开始界面的默认状态)。"""
        center = (COLS // 2, ROWS // 2)
        self.snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food = self.spawn_food()
        self.score = 0
        self.state = "menu"

    def start(self, level):
        """按选定的难度开始新的一局。"""
        self.level = level
        center = (COLS // 2, ROWS // 2)
        self.snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food = self.spawn_food()
        self.score = 0
        self.state = "playing"

    @property
    def level_name(self):
        return LEVELS[self.level][0]

    @property
    def speed(self):
        """当前速度(每秒走多少格)：随分数逐渐变快。"""
        base, accel = LEVELS[self.level][1], LEVELS[self.level][2]
        return min(base + self.score * accel, MAX_SPEED)

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
        self.state = "over"
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    # ---------- 绘制 ----------
    def draw_background(self):
        """棋盘格背景，让移动看起来更清楚。"""
        self.screen.fill(BACKGROUND)
        for x in range(COLS):
            for y in range(ROWS):
                if (x + y) % 2 == 0:
                    rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
                    pygame.draw.rect(self.screen, GRID_LIGHT, rect)

    def draw_cell(self, pos, color, inset=1):
        rect = pygame.Rect(
            pos[0] * CELL + inset, pos[1] * CELL + inset, CELL - inset * 2, CELL - inset * 2
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=3)

    def draw_hud(self):
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 8))

        best_text = self.small_font.render(f"最高分: {self.highscore}", True, YELLOW)
        self.screen.blit(best_text, (WIDTH - best_text.get_width() - 10, 12))

        info = self.small_font.render(
            f"难度: {self.level_name}  速度: {self.speed:.1f}", True, GREY
        )
        self.screen.blit(info, info.get_rect(center=(WIDTH // 2, 18)))

    def draw_center_text(self, lines, color=WHITE):
        """在屏幕中间画几行文字。"""
        total = len(lines)
        for index, (text, font) in enumerate(lines):
            surface = font.render(text, True, color if index == 0 else WHITE)
            y = HEIGHT // 2 - (total * 30) // 2 + index * 44
            self.screen.blit(surface, surface.get_rect(center=(WIDTH // 2, y)))

    def draw_menu(self):
        self.screen.fill(BACKGROUND)
        title = self.big_font.render("SNAKE 贪吃蛇", True, GREEN)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90)))

        for index, (key, (name, speed, accel)) in enumerate(LEVELS.items()):
            text = f"{key}. {name}   起始速度 {speed:.0f}"
            color = YELLOW if key == self.level else WHITE
            surface = self.font.render(text, True, color)
            self.screen.blit(
                surface, surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 10 + index * 40))
            )

        tip = self.small_font.render("按 1 / 2 / 3 选择难度并开始   ESC 退出", True, GREY)
        self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130)))
        best = self.small_font.render(f"历史最高分: {self.highscore}", True, YELLOW)
        self.screen.blit(best, best.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 165)))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
            pygame.display.flip()
            return

        self.draw_background()
        self.draw_cell(self.food, RED)

        for index, segment in enumerate(self.snake):
            color = GREEN if index == 0 else DARK_GREEN
            self.draw_cell(segment, color)

        self.draw_hud()

        if self.state == "over":
            self.draw_center_text([("GAME OVER", self.big_font)], color=RED)
            tip = self.font.render(
                f"本局 {self.score} 分 · R 重来 / M 选难度 / ESC 退出", True, WHITE
            )
            self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 44)))
        elif self.state == "paused":
            self.draw_center_text([("已暂停", self.big_font)], color=YELLOW)
            tip = self.font.render("按空格继续 / M 回到开始界面", True, WHITE)
            self.screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 44)))

        pygame.display.flip()

    # ---------- 主循环 ----------
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)

            if self.state == "playing":
                self.step()

            self.draw()
            self.clock.tick(self.speed if self.state == "playing" else 30)

    def handle_key(self, key):
        keys = {
            pygame.K_UP: UP, pygame.K_w: UP,
            pygame.K_DOWN: DOWN, pygame.K_s: DOWN,
            pygame.K_LEFT: LEFT, pygame.K_a: LEFT,
            pygame.K_RIGHT: RIGHT, pygame.K_d: RIGHT,
        }

        if key == pygame.K_ESCAPE:
            self.quit()

        if self.state == "menu":
            if key in LEVEL_KEYS:
                self.start(LEVEL_KEYS[key])
            return

        if key == pygame.K_m:
            self.reset()
            return

        if key == pygame.K_SPACE and self.state in ("playing", "paused"):
            self.state = "paused" if self.state == "playing" else "playing"
            return

        if key == pygame.K_r and self.state == "over":
            self.start(self.level)
            return

        if key in keys and self.state == "playing":
            new_dir = keys[key]
            # 不能 180 度掉头
            if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
                self.next_direction = new_dir

    def quit(self):
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    SnakeGame().run()
