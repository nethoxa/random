import random

from copy import deepcopy

from .base import Base
from .stuff import find_non_overlapping_min, find_non_overlapping_max, Permutation

# The TabuSearch algorithm
class TabuSearch(Base):

    # Init routine
    def __init__(self, path: str, maxIt: int, seed: int, tabu_tenure: int, share: float) -> None:
        Base.__init__(self=self, path=path)
        random.seed(seed)
        self.seed = seed
        self.path = path.split("/")[1]
        
        self.permutation = Permutation(self.matrixSize)
        self.dlb = [False for _ in range(self.matrixSize)]
        self.improve = True
        self.tabu_list = []  # Tabu list to store recent moves
        self.tabu_tenure = tabu_tenure
        self.maxIt = int(maxIt)
        self.share = share
        self.LM = [[0 for _ in range(self.matrixSize)] for _ in range(self.matrixSize)]
        self.mejorPeor = Permutation(self.matrixSize)

        # Get the total cost
        for i in range(self.matrixSize):
            for j in range(self.matrixSize):
                self.permutation.cost += self.firstMatrix[i][j] * self.secondMatrix[self.permutation.perm[i]][self.permutation.perm[j]]

        # Get the total cost
        for i in range(self.matrixSize):
            for j in range(self.matrixSize):
                self.mejorPeor.cost += self.firstMatrix[i][j] * self.secondMatrix[self.mejorPeor.perm[i]][self.mejorPeor.perm[j]]

    # Get the cost of the given permutation
    def getCost(self, i: int, j: int) -> int:
        cost = 0
        copy = deepcopy(self.permutation)
        copy.swap(i, j)
        
        """for k in range(self.matrixSize):
            if k != i and k != j:
                cost += self.firstMatrix[i][k] * (self.secondMatrix[copy.perm[j]][copy.perm[k]] - self.secondMatrix[copy.perm[i]][copy.perm[k]])
                cost += self.firstMatrix[j][k] * (self.secondMatrix[copy.perm[i]][copy.perm[k]] - self.secondMatrix[copy.perm[j]][copy.perm[k]])
        """

        for i in range(self.matrixSize):
            for j in range(self.matrixSize):
                cost += self.firstMatrix[i][j] * self.secondMatrix[copy.perm[i]][copy.perm[j]]

        del copy
        return cost
    
    # Add a move to the tabu list
    def add_to_tabu_list(self, move: int) -> None:
        self.tabu_list.append(move)
        if len(self.tabu_list) > self.tabu_tenure:
            self.tabu_list.pop(0)


    # Check if a move is in the tabu list
    def is_tabu(self, move: int) -> bool:
        return move in self.tabu_list
    
    # Whatever
    def reInit(self) -> None:
        value = random.choice([False, True])
        if value:
            self.intensify()
        else:
            self.diversify()

    # Diversify
    def diversify(self) -> None:
        minimums = find_non_overlapping_min(self.LM)
        self.permutation.perm = minimums
        self.permutation.cost = 0

        # Get the total cost
        for i in range(self.matrixSize):
            for j in range(self.matrixSize):
                self.permutation.cost += self.firstMatrix[i][j] * self.secondMatrix[self.permutation.perm[i]][self.permutation.perm[j]]

    # Intensify
    def intensify(self):
        maximums = find_non_overlapping_max(self.LM)
        self.permutation.perm = maximums
        self.permutation.cost = 0

        # Get the total cost
        for i in range(self.matrixSize):
            for j in range(self.matrixSize):
                self.permutation.cost += self.firstMatrix[i][j] * self.secondMatrix[self.permutation.perm[i]][self.permutation.perm[j]]


    # Entry point of the algorithm
    def run(self, is_grasp: bool, upper_seed: int, aux: int) -> None:
        count = 0
        if is_grasp:
            url = f"logs/grasp-{upper_seed}-{self.seed}-{aux}-{self.path.split('.')[0]}.log"
        else:
            url = f"logs/tabu-{self.seed}-{self.path.split('.')[0]}.log"

        with open(url, "x") as _:
            pass

        with open(url, "w") as f:
            # Try until max iterations
            for _ in range(self.maxIt):

                # If % of the total is wrong, reinit
                if count % int(self.maxIt * self.share) == 0 and count != 0:
                    self.reInit()

                # No improvement, reinit and set the best worst
                if not 0 in self.dlb:
                    del self.permutation
                    self.permutation = deepcopy(self.mejorPeor)
                    self.dlb = [random.choice([False, True] for _ in range(self.matrixSize))]

                i = random.randrange(self.matrixSize)
                
                # Pick random, go up sequentially
                while i < self.matrixSize:
                    if not self.dlb[i]:
                        self.improve = False

                        for j in range(self.matrixSize):
                            if i != j:
                                move = (i, j)
                                if not self.is_tabu(move):
                                    newCost = self.getCost(i, j)

                                    # A better move
                                    if newCost < self.permutation.cost:
                                        self.permutation.swap(i, j)
                                        self.permutation.cost = newCost # TODO +=
                                        self.dlb[i] = self.dlb[j] = False
                                        self.improve = True
                                        self.add_to_tabu_list(move)
                                        self.LM[i][self.permutation.perm[i]] += 1 # update 
                                        f.write(f"Permutation changed to {self.permutation.perm} with cost {self.permutation.cost}\n")

                                    else:
                                        if newCost < self.mejorPeor.cost:
                                            self.mejorPeor.swap(i, j)
                                            self.mejorPeor.cost = newCost # TODO +=
                                            f.write(f"The best worst permutation changed to {self.mejorPeor.perm} with cost {self.mejorPeor.cost}\n")
                        
                        # No move found, do not repeat
                        if not self.improve:
                            self.dlb[i] = True

                    i += 1

                # Iteration did not improve anything, break
                if not self.improve:
                    break

    # Get the final solution
    def getSolution(self) -> (list, int):
        return (self.permutation.perm, self.permutation.cost)
    