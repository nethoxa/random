import os
import math

from dotenv import load_dotenv

from src.tsp import TSP

def main():
    load_dotenv()

    files = os.getenv("FILES").split()
    poblation_size = [int(_) for _ in os.getenv("POBLATION_SIZE").split()]
    greedy_size= int(os.getenv("GREEDY_SIZE")[0])
    share_random = float(os.getenv("SHARE_RANDOM")[0])
    elite = [int(_) for _ in os.getenv("ELITE").split()]
    kBest = [int(_) for _ in os.getenv("KBEST").split()]
    kWorst = int(os.getenv("KWORST")[0])
    share_mix = float(os.getenv("SHARE_MIX"))
    share_mutation = float(os.getenv("SHARE_MUTATION"))
    stop = [int(_) for _ in os.getenv("STOP").split()]
    _time = int(os.getenv("TIME")[0])

    for file in files:

        with open(file) as f:
            data = f.readlines()[6:-1]
        
        # build matrix of distances, although it is symetric, we calculate it fully
        matrix = [[j for j in range(len(data))] for _ in range(len(data))]

        for i in range(len(data)):
            rowA = data[i].split()[1:]
            for j in range(len(data)):
                rowB = data[j].split()[1:]

                # d = raiz_cuadrada((x2 - x1)² + (y2 -y1)²)
                matrix[i][j] = math.sqrt(
                    math.pow(float(rowB[0]) - float(rowA[0]), 2) +
                    math.pow(float(rowB[1]) - float(rowA[1]), 2)
                )
            
        # @todo no se que de 5 semillas de la practica anterior
        testy = TSP(
            matrix,
            poblation_size[0],
            greedy_size,
            share_random,
            elite[0],
            kBest[0],
            kWorst,
            share_mix,
            share_mutation,
            stop[0],
            _time
        )

        testy.run()
        print(testy.getSolution())
        print(testy.calculate_distance(testy.getSolution()))

        return



if __name__ == "__main__":
    main()