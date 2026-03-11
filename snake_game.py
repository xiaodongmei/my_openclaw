#!/usr/bin/env python3
"""
贪吃蛇游戏 - 终端版
使用方向键控制蛇的移动，吃食物得分，撞墙或撞自己则游戏结束。
"""

import curses
import random
import time


def main(stdscr):
    # ---------- 初始化 curses ----------
    curses.curs_set(0)          # 隐藏光标
    stdscr.nodelay(True)        # 非阻塞输入
    stdscr.timeout(100)         # 刷新间隔(ms)，控制蛇速度

    # 初始化颜色
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # 蛇身
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # 食物
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # 边框/分数
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)    # 标题

    # ---------- 游戏区域 ----------
    sh, sw = stdscr.getmaxyx()
    # 最小终端大小检查
    if sh < 15 or sw < 40:
        stdscr.addstr(0, 0, "终端太小，请调整到至少 40x15")
        stdscr.refresh()
        stdscr.timeout(-1)
        stdscr.getch()
        return

    # 游戏边框 (留出顶部 2 行给标题和分数)
    box_top = 2
    box_left = 1
    box_h = sh - 3       # 高度
    box_w = sw - 2        # 宽度

    # 创建游戏窗口
    win = curses.newwin(box_h, box_w, box_top, box_left)
    win.keypad(True)
    win.timeout(100)

    def show_start_screen():
        """显示开始界面"""
        stdscr.clear()
        mid_y = sh // 2
        mid_x = sw // 2

        title = "🐍  贪 吃 蛇  🐍"
        stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(mid_y - 4, max(0, mid_x - len(title) // 2), title)
        stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)

        instructions = [
            "方向键 / WASD  控制移动",
            "吃掉 ★ 得分，蛇身变长",
            "撞墙或撞自己 → 游戏结束",
            "",
            "按任意键开始...",
        ]
        for i, line in enumerate(instructions):
            stdscr.addstr(mid_y - 1 + i, max(0, mid_x - len(line) // 2), line)

        stdscr.refresh()
        stdscr.timeout(-1)    # 阻塞等待
        stdscr.getch()
        stdscr.timeout(100)

    def place_food(snake_body):
        """随机放置食物，不与蛇身重叠"""
        while True:
            fy = random.randint(1, box_h - 2)
            fx = random.randint(1, box_w - 2)
            if (fy, fx) not in snake_body:
                return (fy, fx)

    def draw_border():
        """绘制边框"""
        win.attron(curses.color_pair(3))
        win.border()
        win.attroff(curses.color_pair(3))

    def draw_score(score, high_score):
        """绘制顶部信息栏"""
        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
        header = f"  得分: {score}    最高分: {high_score}    按 Q 退出  "
        stdscr.addstr(0, 2, header)
        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
        stdscr.refresh()

    def game_over_screen(score, high_score):
        """游戏结束界面"""
        win.clear()
        draw_border()
        mid_y = box_h // 2
        mid_x = box_w // 2

        msg1 = "GAME OVER!"
        msg2 = f"得分: {score}"
        msg3 = f"最高分: {high_score}"
        msg4 = "R = 重来  Q = 退出"

        win.attron(curses.color_pair(2) | curses.A_BOLD)
        win.addstr(mid_y - 2, max(1, mid_x - len(msg1) // 2), msg1)
        win.attroff(curses.color_pair(2) | curses.A_BOLD)

        win.addstr(mid_y, max(1, mid_x - len(msg2) // 2), msg2)
        win.addstr(mid_y + 1, max(1, mid_x - len(msg3) // 2), msg3)

        win.attron(curses.color_pair(4))
        win.addstr(mid_y + 3, max(1, mid_x - len(msg4) // 2), msg4)
        win.attroff(curses.color_pair(4))

        win.refresh()

        # 等待玩家选择
        win.timeout(-1)
        while True:
            k = win.getch()
            if k in (ord('r'), ord('R')):
                win.timeout(100)
                return True   # 重新开始
            if k in (ord('q'), ord('Q'), 27):  # q / ESC
                return False  # 退出

    # ---------- 主循环 ----------
    show_start_screen()
    high_score = 0

    while True:
        # --- 初始化每一局 ---
        score = 0
        speed = 100  # ms

        # 蛇初始位置 (窗口中央，长度 3)
        start_y = box_h // 2
        start_x = box_w // 2
        snake = [
            (start_y, start_x),
            (start_y, start_x - 1),
            (start_y, start_x - 2),
        ]

        direction = curses.KEY_RIGHT
        food = place_food(set(snake))

        win.clear()
        draw_border()
        draw_score(score, high_score)

        # 方向映射：键 → (dy, dx)
        dir_map = {
            curses.KEY_UP:    (-1, 0),
            curses.KEY_DOWN:  (1,  0),
            curses.KEY_LEFT:  (0, -1),
            curses.KEY_RIGHT: (0,  1),
        }
        # WASD 支持
        wasd_map = {
            ord('w'): curses.KEY_UP,
            ord('W'): curses.KEY_UP,
            ord('s'): curses.KEY_DOWN,
            ord('S'): curses.KEY_DOWN,
            ord('a'): curses.KEY_LEFT,
            ord('A'): curses.KEY_LEFT,
            ord('d'): curses.KEY_RIGHT,
            ord('D'): curses.KEY_RIGHT,
        }
        # 反方向（防止 180° 掉头）
        opposite = {
            curses.KEY_UP:    curses.KEY_DOWN,
            curses.KEY_DOWN:  curses.KEY_UP,
            curses.KEY_LEFT:  curses.KEY_RIGHT,
            curses.KEY_RIGHT: curses.KEY_LEFT,
        }

        # --- 游戏循环 ---
        alive = True
        while alive:
            key = win.getch()

            # WASD → 方向键
            if key in wasd_map:
                key = wasd_map[key]

            # 退出
            if key in (ord('q'), ord('Q'), 27):
                return

            # 更新方向（忽略反向）
            if key in dir_map and key != opposite.get(direction):
                direction = key

            # 计算新头部位置
            dy, dx = dir_map[direction]
            head_y, head_x = snake[0]
            new_head = (head_y + dy, head_x + dx)

            # --- 碰撞检测 ---
            ny, nx = new_head
            # 撞墙
            if ny <= 0 or ny >= box_h - 1 or nx <= 0 or nx >= box_w - 1:
                alive = False
                break
            # 撞自己
            if new_head in snake:
                alive = False
                break

            # --- 移动蛇 ---
            snake.insert(0, new_head)

            if new_head == food:
                # 吃到食物
                score += 10
                if score > high_score:
                    high_score = score
                food = place_food(set(snake))
                # 加速（最快 50ms）
                speed = max(50, 100 - (score // 50) * 10)
                win.timeout(speed)
            else:
                # 没吃到就去掉尾巴
                tail = snake.pop()
                win.addch(tail[0], tail[1], ' ')

            # --- 绘制 ---
            draw_score(score, high_score)

            # 绘制蛇头
            win.attron(curses.color_pair(1) | curses.A_BOLD)
            win.addch(snake[0][0], snake[0][1], '@')
            win.attroff(curses.color_pair(1) | curses.A_BOLD)

            # 绘制蛇身 (第二节开始)
            if len(snake) > 1:
                win.attron(curses.color_pair(1))
                win.addch(snake[1][0], snake[1][1], 'o')
                win.attroff(curses.color_pair(1))

            # 绘制食物
            win.attron(curses.color_pair(2) | curses.A_BOLD)
            win.addch(food[0], food[1], '*')
            win.attroff(curses.color_pair(2) | curses.A_BOLD)

            draw_border()
            win.refresh()

        # --- 本局结束 ---
        if not game_over_screen(score, high_score):
            break  # 玩家选择退出


if __name__ == "__main__":
    curses.wrapper(main)
