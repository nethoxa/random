import os
import sys
import time
import platform

from dotenv import load_dotenv
from termcolor import colored

from src.greedy import Greedy
from src.local import LocalSearch
from src.tabu import TabuSearch
from src.grasp import Grasp
from src.stuff import *

def main():
    if platform.system() == "Windows":
        os.system("cls")
    elif platform.system() == "Linux":
        os.system("clear")
    else:
        print("\n\n" + ERROR + " You are using MAC, I won't run in MAC (-_-)")
        sys.exit()

    print(HEADER)

    load_dotenv()

    files = os.getenv("FILES").split()
    seeds = os.getenv("SEEDS").split()
    iterations = os.getenv("ITERATIONS").split()
    tabu_tenure = os.getenv("TABU_TENURE").split()
    share = os.getenv("SHARE").split()
    max_it_grasp = os.getenv("MAX_IT_GRASP").split()
    bound = os.getenv("BOUND").split()

    os.makedirs("logs", exist_ok=True)
    for log in os.listdir("logs"):
        os.remove("logs/" + log)

    try:
        for seed in seeds:     

            for file in files:
                    
                print(f"----------- Greedy solution for {file.split('/')[1]} with seed {colored(seed, 'yellow')} -----------")
                greedy = Greedy(file)
                
                before = time.time()
                greedy.run()
                after = time.time()

                (solutionGreedy, cost) = greedy.getSolution()
                print(SUCCESS + "Final solution = " + "[" + ", ".join([str(x) for x in solutionGreedy]) + "]")
                print(SUCCESS + " Final cost = ", colored(cost, "red"))
                print(SUCCESS + " Time " + colored(str(after - before).replace(".", ","), "red"))
                print("\n")     


                print(f"----------- Local search solution for {file.split('/')[1]} with seed {colored(seed, 'yellow')} -----------")
                local_search = LocalSearch(file, iterations[0], int(seed))
                
                before = time.time()
                local_search.run()
                after = time.time()

                (solutionLocalSearch, cost) = local_search.getSolution()
                print(SUCCESS + " Final permutation = ", solutionLocalSearch)
                print(SUCCESS + " Final cost = ", colored(cost, "red"))
                print(SUCCESS + " Time " + colored(str(after - before).replace(".", ","), "red"))
                print("\n")


                print(f"----------- Tabu search solution for {file.split('/')[1]} with seed {colored(seed, 'yellow')} -----------")
                tabu_search = TabuSearch(file, iterations[0], int(seed), int(tabu_tenure[0]), float(share[0]))
                
                before = time.time()
                tabu_search.run(False, 0, 0)
                after = time.time()

                (solutionTabuSearch, cost) = tabu_search.getSolution()
                print(SUCCESS + " Final permutation = ", solutionTabuSearch)
                print(SUCCESS + " Final cost = ", colored(cost, "red"))
                print(SUCCESS + " Time " + colored(str(after - before).replace(".", ","), "red"))
                print("\n")


                print(f"----------- GRASP solution for {file.split('/')[1]} with seed {colored(seed, 'yellow')} -----------")
                grasp = Grasp(file, int(max_it_grasp[0]), iterations[0], int(seed), int(tabu_tenure[0]), float(share[0]), int(bound[0]))
                
                before = time.time()
                grasp.run()
                after = time.time()

                (solutionGrasp, cost) = grasp.getSolution()
                print(SUCCESS + " Final permutation = ", solutionGrasp)
                print(SUCCESS + " Final cost = ", colored(cost, "red"))
                print(SUCCESS + " Time " + colored(str(after - before).replace(".", ","), "red"))
                print("\n\n\n")

    except:
        for log in os.listdir("logs"):
            os.remove("logs/" + log)
        

if __name__ == "__main__":
    main()