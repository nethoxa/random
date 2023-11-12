import random

from copy import deepcopy

from .base import Base


# Just an abstraction
class Permutation:

    # Init routine
    def __init__(self, length: int) -> None:
        self.cost = 0
        self.perm = [_ for _ in range(length)]
        random.shuffle(self.perm)

    # Swap
    def swap(self, i: int, j: int) -> None:
        aux = self.perm[i]
        self.perm[i] = self.perm[j]
        self.perm[j] = aux


# The LocalSearch algorithm
class LocalSearch(Base):

    # Init routine
    def __init__(self, path: str, maxIt: int, seed: int) -> None:
        Base.__init__(self=self, path=path)
        random.seed(seed)
        self.seed = seed
        self.path = path.split("/")[1]
        
        self.permutation = Permutation(self.matrixSize)
        self.dlb = [False for _ in range(self.matrixSize)]
        self.improve = True

        # Get the total cost
        for i in range(self.matrixSize):
            for j in range(self.matrixSize):
                self.permutation.cost += self.firstMatrix[i][j] * self.secondMatrix[self.permutation.perm[i]][self.permutation.perm[j]]

        self.maxIt = int(maxIt)
        

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
    
    
    # Entry point of the algorithm
    def run(self) -> None:
        
        with open(f"logs/PMDLBrandom-{self.seed}-{self.path.split('.')[0]}.log", "x") as _:
            pass

        with open(f"logs/PMDLBrandom-{self.seed}-{self.path.split('.')[0]}.log", "w") as f:

            # Try until max iterations
            for _ in range(self.maxIt):
                i = random.randrange(self.matrixSize)
                
                # Pick random, go up sequentially
                while i < self.matrixSize:
                    if not self.dlb[i]:
                        self.improve = False

                        for j in range(self.matrixSize):
                            if i != j:
                                newCost = self.getCost(i, j)

                                # A better move
                                if newCost < self.permutation.cost:
                                    self.permutation.swap(i, j)
                                    self.permutation.cost = newCost # TODO +=

                                    self.dlb[i] = self.dlb[j] = False
                                    self.improve = True
                                    f.write(f"Permutation changed to {self.permutation.perm} with cost {self.permutation.cost}\n")
                        
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
    