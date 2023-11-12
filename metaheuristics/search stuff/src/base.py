# A base class for all algorithms
class Base:
    def __init__(self, path: str) -> None:
        try:
            with open(path, "r") as f:
                lines = f.readlines()
                self.matrixSize =  int(lines[0])
                self.firstMatrix = []
                self.secondMatrix = []

                for i in range(self.matrixSize):
                    self.firstMatrix.append([int(x) for x in lines[2 + i].split()])

                for j in range(self.matrixSize):
                    self.secondMatrix.append([int(x) for x in lines[i + 4 + j].split()])



        except:
            print("Error trying to parse the file ", path)
            raise Exception()