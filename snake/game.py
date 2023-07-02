#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111,W0201,W0703

import errno
import os
import traceback
import datetime
from enum import Enum, unique
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.colors as mcolors

from snake.base import Direc, Map, PointType, Pos, Snake
from snake.gui import GameWindow
from snake.solver import DQNSolver, GreedySolver, HamiltonSolver, Userplayer, BFS, hamiltonBase, DFS


@unique
class GameMode(Enum):
    NORMAL = 0  # AI with GUI
    BENCHMARK = 1  # Run benchmarks without GUI
    TRAIN_DQN = 2  # Train DQNSolver without GUI
    TRAIN_DQN_GUI = 3  # Train DQNSolver with GUI


class GameConf:
    def __init__(self):
        """Initialize a default configuration."""

        # Game mode
        self.mode = GameMode.NORMAL

        # Solver
        self.solver_name = "HamiltonSolver"  # Class name of the solver

        # Size
        self.map_rows = 10
        self.map_cols = self.map_rows
        self.map_width = 400  # pixels
        self.map_height = self.map_width
        self.info_panel_width = 155  # pixels
        self.window_width = self.map_width + self.info_panel_width
        self.window_height = self.map_height
        self.grid_pad_ratio = 0.25

        # Switch
        self.show_grid_line = True
        self.show_info_panel = True

        # Delay
        self.interval_draw = 50  # ms
        self.interval_draw_max = 2000  # ms

        # Color
        self.color_bg = "#000000"
        self.color_txt = "#F5F5F5"
        self.color_line = "#424242"
        self.color_wall = "#F5F5F5"
        self.color_food = "#FFF59D"
        self.color_head = "red"
        self.color_body = "#F5F5F5"

        # Initial snake
        self.init_direc = Direc.RIGHT
        self.init_bodies = [Pos(1, 4), Pos(1, 3), Pos(1, 2), Pos(1, 1)]
        self.init_types = [PointType.HEAD_R] + [PointType.BODY_HOR] * 3

        # Font
        self.font_info = ("Arial", 9)

        # Info
        self.info_str = (
            "<w/a/s/d>: snake direction\n"
            "<u/l/d/r>: snake direction\n"
            "<space>: pause/resume\n"
            "<r>: restart    <esc>: exit\n"
            "-----------------------------------\n"
            "status: %s\n"
            "episode: %d   step: %d\n"
            "length: %d/%d (%dx%d)\n"
            "-----------------------------------"
        )
        self.info_status = ["eating", "dead", "full"]


class Game:
    def __init__(self, conf: GameConf):
        self._conf = conf
        self._map = Map(conf.map_rows + 2, conf.map_cols + 2)
        # self._map.point(Pos(1, 6)).type = PointType.WALL
        self._snake = Snake(
            self._map, conf.init_direc, conf.init_bodies, conf.init_types
        )
        self._pause = False
        self._solver = globals()[self._conf.solver_name](self._snake)
        self._episode = 1
        self._init_log_file()
        if self._conf.solver_name == "Userplayer":
            self._pause = True

    @property
    def snake(self):
        return self._snake

    @property
    def episode(self):
        return self._episode

    def run(self):
        if self._conf.mode == GameMode.BENCHMARK:
            self._run_benchmarks()
        elif self._conf.mode == GameMode.TRAIN_DQN:
            self._run_dqn_train()
            self._plot_history()
        else:
            window = GameWindow(
                "Snake",
                self._conf,
                self._map,
                self,
                self._on_exit,
                (
                    ("<w>", lambda e: self._update_direc(Direc.UP)),
                    ("<a>", lambda e: self._update_direc(Direc.LEFT)),
                    ("<s>", lambda e: self._update_direc(Direc.DOWN)),
                    ("<d>", lambda e: self._update_direc(Direc.RIGHT)),
                    ("<Up>", lambda e: self._update_direc(Direc.UP)),
                    ("<Left>", lambda e: self._update_direc(Direc.LEFT)),
                    ("<Down>", lambda e: self._update_direc(Direc.DOWN)),
                    ("<Right>", lambda e: self._update_direc(Direc.RIGHT)),
                    ("<r>", lambda e: self._reset()),
                    ("<space>", lambda e: self._toggle_pause()),
                ),
            )
            if self._conf.mode == GameMode.NORMAL:
                window.show(self._game_main_normal)
            elif self._conf.mode == GameMode.TRAIN_DQN_GUI:
                window.show(self._game_main_dqn_train)
                self._plot_history()

    def _run_benchmarks(self):
        STEPS_LIMIT = 5000
        NUM_EPISODES = int(input("Please input the number of episodes: "))

        print("\nMap size: %dx%d" % (self._conf.map_rows, self._conf.map_cols))
        print("Solver: %s\n" % self._conf.solver_name[:-6].lower())

        tot_len, tot_steps = 0, 0
        now = datetime.datetime.now()
        name = now.strftime(f"bcmk_{self._conf.solver_name}_%d-%m-%y-%H-%M-%S.txt")
        f = open("logs/benchmarks/" + name, "a")
        for i in range(NUM_EPISODES):
            print("Episode %d - " % self._episode, end="")
            while True:
                self._game_main_normal()
                if self._map.is_full():
                    print(
                        "FULL (len: %d | steps: %d)"
                        % (self._snake.len(), self._snake.steps)
                    )
                    break
                elif self._snake.dead:
                    print(
                        "DEAD (len: %d | steps: %d)"
                        % (self._snake.len(), self._snake.steps)
                    )
                    break
                elif self._snake.steps >= STEPS_LIMIT:
                    print(
                        "STEP LIMIT (len: %d | steps: %d)"
                        % (self._snake.len(), self._snake.steps)
                    )
                    self._write_logs()  # Write the last step
                    break
            f.write(f"{i},{self._snake.len()},{self._snake.steps}\n")
            tot_len += self._snake.len()
            tot_steps += self._snake.steps

            self._reset()
        f.close()
        avg_len = tot_len / NUM_EPISODES
        avg_steps = tot_steps / NUM_EPISODES
        print(
            "\n[Summary]\nAverage Length: %.2f\nAverage Steps: %.2f\n"
            % (avg_len, avg_steps)
        )
        with open("logs/benchmarks/" + name, "r") as f:
            lines = f.readlines()
        x_data = []
        y1_data = []
        y2_data = []

        for line in lines:
            columns = line.strip().split(",")
            x_data.append(int(columns[0]) + 1)
            y1_data.append(int(columns[1]))
            y2_data.append(int(columns[2]))

        fig, ax1 = plt.subplots()
        ax1.plot(x_data, y1_data, color=mcolors.to_rgb("#0958ad"), label="y1")
        ax1.set_ylabel("Length", color=mcolors.to_rgb("#0958ad"))
        ax1.tick_params("y", colors=mcolors.to_rgb("#0958ad"))
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax2 = ax1.twinx()
        ax2.plot(x_data, y2_data, color=mcolors.to_rgb("#a30707"), label="y2")
        ax2.set_ylabel("Steps", color=mcolors.to_rgb("#a30707"))
        ax2.tick_params("y", colors=mcolors.to_rgb("#a30707"))
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="best")
        plt.title(f"Using {self._conf.solver_name}")
        plt.xlabel("Number of runs")
        fig.savefig(f"logs/figure/img_{name}.png")
        plt.show()

        self._on_exit()

    def _run_dqn_train(self):
        try:
            while not self._game_main_dqn_train():
                pass
        except KeyboardInterrupt:
            pass
        except Exception:
            traceback.print_exc()
        finally:
            self._on_exit()

    def _game_main_dqn_train(self):
        if not self._map.has_food():
            self._map.create_rand_food()

        if self._pause:
            return

        episode_end, learn_end = self._solver.train()

        if episode_end:
            self._reset()

        return learn_end

    def _game_main_normal(self):
        if not self._map.has_food():
            self._map.create_rand_food()

        if self._pause or self._is_episode_end():
            return

        self._update_direc(self._solver.next_direc())

        if self._conf.mode == GameMode.NORMAL and self._snake.direc_next != Direc.NONE:
            self._write_logs()

        self._snake.move()

        if self._is_episode_end():
            self._write_logs()  # Write the last step

    def _plot_history(self):
        self._solver.plot()

    def _update_direc(self, new_direc):
        self._snake.direc_next = new_direc
        if self._pause:
            self._snake.move()

    def _toggle_pause(self):
        self._pause = not self._pause

    def _is_episode_end(self):
        return self._snake.dead or self._map.is_full()

    def _reset(self):
        self._snake.reset()
        self._episode += 1

    def _on_exit(self):
        if self._log_file:
            self._log_file.close()
        if self._solver:
            self._solver.close()

    def _init_log_file(self):
        try:
            os.makedirs("logs")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        try:
            self._log_file = None
            self._log_file = open("logs/snake.log", "w")
        except FileNotFoundError:
            if self._log_file:
                self._log_file.close()

    def _write_logs(self):
        self._log_file.write(
            "[ Episode %d / Step %d ]\n" % (self._episode, self._snake.steps)
        )
        for i in range(self._map.num_rows):
            for j in range(self._map.num_cols):
                pos = Pos(i, j)
                t = self._map.point(pos).type
                if t == PointType.EMPTY:
                    self._log_file.write("  ")
                elif t == PointType.WALL:
                    self._log_file.write("# ")
                elif t == PointType.FOOD:
                    self._log_file.write("F ")
                elif (
                    t == PointType.HEAD_L
                    or t == PointType.HEAD_U
                    or t == PointType.HEAD_R
                    or t == PointType.HEAD_D
                ):
                    self._log_file.write("H ")
                elif pos == self._snake.tail():
                    self._log_file.write("T ")
                else:
                    self._log_file.write("B ")
            self._log_file.write("\n")
        self._log_file.write(
            "[ last/next direc: %s/%s ]\n" % (self._snake.direc, self._snake.direc_next)
        )
        self._log_file.write("\n")
