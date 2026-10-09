# Snake Game (贪吃蛇)

一个用 Python + pygame 写的贪吃蛇小游戏，同时作为学习 **Git / GitHub** 的练习项目。

## 功能

- 方向键或 WASD 控制移动，不能 180 度掉头
- 吃到食物变长并加分
- 撞墙或撞到自己游戏结束，按 `R` 重新开始，`ESC` 退出

## 运行

```bash
pip install -r requirements.txt
python snake.py
```

## 项目结构

```
SnakeGame/
├── snake.py          # 游戏主程序
├── requirements.txt  # 依赖
└── README.md
```

## 后续计划

- [ ] 保存最高分
- [ ] 暂停功能
- [ ] 难度 / 速度选择
