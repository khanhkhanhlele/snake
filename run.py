#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111

import argparse

from snake.game import Game, GameConf, GameMode

dict_solver = {
    "greedy": "GreedySolver",
    "hamilton": "HamiltonSolver",
    "dqn": "DQNSolver",
    "human": "Userplayer",
    "BFS": "BFS",
    "hamiltonBase": "hamiltonBase",
    "DFS": "DFS",
    "astar": "astar"
}

dict_mode = {
    "normal": GameMode.NORMAL,
    "bcmk": GameMode.BENCHMARK,
    "train_dqn": GameMode.TRAIN_DQN,
    "train_dqn_gui": GameMode.TRAIN_DQN_GUI,
    
}

parser = argparse.ArgumentParser(description="Run snake game agent.")
parser.add_argument("-s", default="hamilton", choices=dict_solver.keys(),
                    help="name of the solver to direct the snake (default: hamilton)")
parser.add_argument("-m", default="normal", choices=dict_mode.keys(),
                    help="game mode (default: normal)")
parser.add_argument('-map', type=str, default=8,
                    help="map size (default: 8x8)")
args = parser.parse_args()

conf = GameConf()
conf.solver_name = dict_solver[args.s]
conf.mode = dict_mode[args.m]
conf.map_rows = conf.map_cols = int(args.map)
print("Solver: %s    Mode: %s   Map Size: %sx%s" % (conf.solver_name, conf.mode, conf.map_rows, conf.map_cols))

Game(conf).run()
