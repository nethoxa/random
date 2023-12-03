import os
import sys
import math
import random
import platform
import concurrent.futures

from dotenv import load_dotenv
from termcolor import colored

from src.generational import Generational
from src.differential import Differential

ERROR = colored("[-]", "red")
SUCCESS = colored("[+]", "green")

HEADER = colored("""
                 

 /$$      /$$ /$$$$$$$$ /$$$$$$$$ /$$$$$$ 
| $$$    /$$$| $$_____/|__  $$__//$$__  $$
| $$$$  /$$$$| $$         | $$  | $$  \ $$
| $$ $$/$$ $$| $$$$$      | $$  | $$$$$$$$
| $$  $$$| $$| $$__/      | $$  | $$__  $$
| $$\  $ | $$| $$         | $$  | $$  | $$
| $$ \/  | $$| $$$$$$$$   | $$  | $$  | $$
|__/     |__/|________/   |__/  |__/  |__/
                                          
""", "cyan") + """

            Sergio Moleón Peñas
           Andrés Jiménez Láinez

"""

def launch_generational(
        matrix: list,
        _poblation_size: int,
        greedy_size: int,
        share_random: int,
        _elite: int,
        _kBest: int,
        kWorst: int,
        share_mix: float,
        share_mutation: float,
        _stop: int,
        _time: int,
        mode: str,
        seed: int,
        file: str
):
    generational = Generational(
        matrix,
        _poblation_size,
        greedy_size,
        share_random,
        _elite,
        _kBest,
        kWorst,
        share_mix,
        share_mutation,
        _stop,
        _time,
        True if mode == "True" else False,
        seed,
        file
    )
    
    generational.run()

def launch_differential(
        matrix: list,
        _poblation_size: int,
        greedy_size: int,
        share_random: int,
        _elite: int,
        _kBest: int,
        _stop: int,
        _time: int,
        mode: str,
        seed: int,
        file: str
):
    differential = Differential(
        matrix,
        _poblation_size,
        greedy_size,
        share_random,
        _stop,
        _time,
        True if mode == "True" else False,
        _kBest,
        _elite,
        seed,
        file
    )

    differential.run()

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
    poblation_size = [int(_) for _ in os.getenv("POBLATION_SIZE").split()]
    greedy_size = int(os.getenv("GREEDY_SIZE")[0])
    share_random = float(os.getenv("SHARE_RANDOM"))
    elite = [int(_) for _ in os.getenv("ELITE").split()]
    kBest = [int(_) for _ in os.getenv("KBEST").split()]
    kWorst = int(os.getenv("KWORST")[0])
    share_mix = float(os.getenv("SHARE_MIX"))
    share_mutation = float(os.getenv("SHARE_MUTATION"))
    stop = int(os.getenv("STOP"))
    _time = int(os.getenv("TIME"))
    is_OX2 = os.getenv("IS_OX2").split()
    is_EDA = is_OX2
    seeds = os.getenv("SEEDS").split()

    os.makedirs("logs", exist_ok=True)
    for log in os.listdir("logs"):
        os.remove("logs/" + log)

    futures = []

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

        file = file.split("/")[1]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for seed in seeds:
                random.seed(int(seed))

                for _poblation_size in poblation_size:
                    for _elite in elite:
                        for _kbest in kBest:
                            for _is_ox2 in is_OX2:
                                with open(f"logs/Generational-FILE={file}-SEED={seed}-POBLATION_SIZE={_poblation_size}-ELITE={_elite}-KBEST={_kbest}-STOP={stop}-IS_OX2={_is_ox2}.txt", "x") as f:
                                    pass

                                futures.append(executor.submit(launch_generational,
                                    matrix,
                                    _poblation_size,
                                    greedy_size,
                                    share_random,
                                    _elite,
                                    _kbest,
                                    kWorst,
                                    share_mix,
                                    share_mutation,
                                    stop,
                                    _time,
                                    _is_ox2,
                                    seed,
                                    file
                                ))
            
            for future in concurrent.futures.as_completed(futures):
                future.result()
        
        futures = []
            
        with concurrent.futures.ThreadPoolExecutor() as executor2:
            for seed in seeds:
                random.seed(int(seed))

                for _poblation_size in poblation_size:
                    for _elite in elite:
                        for _kbest in kBest:
                            for _is_EDA in is_EDA:
                                with open(f"logs/Differential-FILE={file}-SEED={seed}-POBLATION_SIZE={_poblation_size}-ELITE={_elite}-KBEST={_kbest}-STOP={stop}-IS_EDA={_is_EDA}.txt", "x") as f:
                                    pass
                                
                                futures.append(executor2.submit(launch_differential,
                                    matrix,
                                    _poblation_size,
                                    greedy_size,
                                    share_random,
                                    _elite,
                                    _kbest,
                                    stop,
                                    _time,
                                    _is_EDA,
                                    seed,
                                    file
                                ))
            
            for future in concurrent.futures.as_completed(futures):
                future.result()
  

if __name__ == "__main__":
    main()