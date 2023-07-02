#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0111

from snake.base.pos import Pos
from snake.solver.base import BaseSolver
from snake.solver.path import PathSolver
from numpy import sqrt

class astar(BaseSolver):

    def __init__(self, snake):
        super().__init__(snake)
        self._path_solver = PathSolver(snake)

    def next_direc(self):
        
