from snake.base.pos import Pos
from snake.solver.base import BaseSolver
from snake.solver.path import PathSolver
from snake.base import Direc

class DFS(BaseSolver):

    def __init__(self, snake):
        super().__init__(snake)
        self._path_solver = PathSolver(snake)

    def next_direc(self):
        self._path_solver.snake = self.snake
        path_to_food = self._path_solver.shortest_path_to_food_dfs()
        if path_to_food:
            return path_to_food[0]
        
        head = self.snake.head()
        direc, max_dist = self.snake.direc, -1
        for adj in head.all_adj():
            if self.map.is_safe(adj):
                dist = Pos.manhattan_dist(adj, self.map.food)
                if dist > max_dist:
                    max_dist = dist
                    direc = head.direc_to(adj)
        return direc
