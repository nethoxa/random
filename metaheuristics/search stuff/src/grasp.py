import random
import sys

from .base import Base
from .stuff import Permutation
from .tabu import TabuSearch

class Grasp(Base):
    def __init__(self, path: str, max_iterations_grasp: int, maxIt: int, seed: int, tabu_tenure: int, share: int, bound: int) -> None:
        Base.__init__(self=self, path=path)

        self.path = path
        self.max_iterations = max_iterations_grasp
        self.maxIt = maxIt
        self.seed = seed
        self.tabu_tenure = tabu_tenure
        self.share = share
        self.best_solution = None
        self.best_solution_cost = sys.maxsize
        self.bound = bound

    def run(self) -> None:
        random.seed(self.seed)
        for _ in range(self.max_iterations):
            
            # Init randomized seed via stated super.self.seed
            tabu_search = TabuSearch(self.path, self.maxIt, int(random.randrange(self.bound)), self.tabu_tenure, self.share)

            # *run*
            tabu_search.run(True, self.seed, _)

            solution, cost = tabu_search.getSolution()

            if cost < self.best_solution_cost:
                self.best_solution_cost = cost # TODO +=
                self.best_solution = solution
        

    def getSolution(self) -> (list, int):
        return self.best_solution, self.best_solution_cost
        