from snake.base.pos import Pos
from snake.solver.base import BaseSolver
from snake.solver.path import PathSolver
from snake.base import Direc
from numpy import sqrt
from random import randint

class astar(BaseSolver):
    def __init__(self, snake):
        super().__init__(snake)

    def next_direc(self):
        food1 = self.map.food
        openset = [self.snake.head()]
        closedset = []
        dir_array1 = []
        while 1:
            if(len(openset)==0):
                if (randint(1, 3) < 2):
                    return Direc.RIGHT
                else:
                    return Direc.LEFT
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
        return dir_array1[-1]