import sys

from .base import Base

# The Greedy algorithm
class Greedy(Base):

    # Init routine
    def __init__(self, path: str, ) -> None:
        Base.__init__(self=self, path=path)
        
        # Init by default
        self.v = []
        self.l = []
        self.solution = []
        
        # Avoid OOB issues
        self.solution = [0 for _ in range(self.matrixSize)]

    # Entry point of the algorithm
    def run(self) -> None:

        # v/y = sum(row_i) 
        for i in range(self.matrixSize):
            self.v.append(sum(self.firstMatrix[i]))
            self.l.append(sum(self.secondMatrix[i]))


        # Get the maximum from v and the minimum from l and go backwards
        for i in range(self.matrixSize):
            maxV = max(self.v)
            minY = min(self.l)
            maxIndexV = self.v.index(maxV)
            minIndexL = self.l.index(minY)

            # f: indexV -> indexL
            self.solution[maxIndexV] = minIndexL
            self.l[minIndexL] = sys.maxsize
            self.v[maxIndexV] = -sys.maxsize

    # Just return self.solution and its associated cost
    def getSolution(self) -> (list, int):
        cost = 0

        # Calculates the associated cost with the found solution
        for i in range(self.matrixSize):
            for j in range(self.matrixSize):
                cost += self.firstMatrix[i][j] * self.secondMatrix[self.solution[i]][self.solution[j]]
    
        return self.solution, cost
    