from snake.base.pos import Pos
from snake.solver.base import BaseSolver
from snake.solver.path import PathSolver
from snake.base import Direc
from numpy import sqrt
from random import randint

class astarcheck(BaseSolver):
    def __init__(self, snake):
        super().__init__(snake)
        self._path_solver = PathSolver(snake)
    def next_direc(self):
        # Create a virtual snake
        s_copy, m_copy = self.snake.copy()
        path_to_food = self.astar_alg()
        if path_to_food:
            # Step 2
            s_copy.move_path(path_to_food)
            if m_copy.is_full():
                return path_to_food[0]

            # Step 3
            self._path_solver.snake = s_copy
            path_to_tail = self._path_solver.longest_path_to_tail()
            if len(path_to_tail) > 1:
                return path_to_food[0]

        # Step 4
        self._path_solver.snake = self.snake
        path_to_tail = self._path_solver.longest_path_to_tail()
        if len(path_to_tail) > 1:
            return path_to_tail[0]

        # Step 5
        head = self.snake.head()
        direc, max_dist = self.snake.direc, -1
        for adj in head.all_adj():
            if self.map.is_safe(adj):
                dist = Pos.manhattan_dist(adj, self.map.food)
                if dist > max_dist:
                    max_dist = dist
                    direc = head.direc_to(adj)
        return direc
        
    def astar_alg(self):
        food1 = self.map.food
        openset = [self.snake.head()]
        closedset = []
        dir_array1 = []
        while 1:
            if(len(openset)==0):
                return 
            current1 = min(openset, key=lambda x: x.f)
            openset = [openset[i] for i in range(len(openset)) if not openset[i] == current1]
            closedset.append(current1)
            for neighbor in current1.all_adj():
                if neighbor not in closedset and self.map.is_safe(neighbor) and neighbor not in self.snake._bodies:
                    tempg = neighbor.g + 1
                    if neighbor in openset:
                        if tempg < neighbor.g:
                            neighbor.g = tempg
                    else:
                        neighbor.g = tempg
                        openset.append(neighbor)
                    neighbor.h = sqrt((neighbor.x - food1.x) ** 2 + (neighbor.y - food1.y) ** 2)
                    neighbor.f = neighbor.g + neighbor.h
                    neighbor.camefrom = current1
            if current1 == food1:
                break
        while current1.camefrom:
            if current1.x == current1.camefrom.x and current1.y < current1.camefrom.y:
                dir_array1.append(Direc.LEFT)
            elif current1.x == current1.camefrom.x and current1.y > current1.camefrom.y:
                dir_array1.append(Direc.RIGHT)
            elif current1.x < current1.camefrom.x and current1.y == current1.camefrom.y:
                dir_array1.append(Direc.UP)
            elif current1.x > current1.camefrom.x and current1.y == current1.camefrom.y:
                dir_array1.append(Direc.DOWN)
            current1 = current1.camefrom
            dir_array1 = dir_array1[::-1]
        return dir_array1