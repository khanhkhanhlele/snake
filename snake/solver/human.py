from snake.solver.base import BaseSolver
from snake.solver.path import PathSolver

from snake.base import Direc, Map, PointType, Pos, Snake
import tkinter as tk

class Userplayer(BaseSolver):

    def __init__(self, snake):
        super().__init__(snake)
        self._path_solver = PathSolver(snake)

    def next_direc(self):
        return Direc.RIGHT


