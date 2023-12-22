import os
import sys
import time
import platform

import numpy as np

from dotenv import load_dotenv
from termcolor import colored

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
                                          
""", "cyan")



def main():

    # clear stuff
    if platform.system() == "Windows":
        os.system("cls")
    elif platform.system() == "Linux":
        os.system("clear")
    else:
        print("\n\n" + ERROR + " You are using MAC, I won't run in MAC (-_-)")
        sys.exit()

    print(HEADER)

    # load .env variables
    load_dotenv()

    files = os.getenv("FILES").split()
    iterations = int(os.getenv("ITERATIONS"))
    secs = int(os.getenv("SECS"))
    size = int(os.getenv("SIZE"))
    alfa = [int(x) for x in os.getenv("ALFA").split()]
    beta = [int(x) for x in os.getenv("BETA").split()]
    q0 = float(os.getenv("Q0"))
    p = float(os.getenv("P"))
    o = float(os.getenv("O"))

    # clean stuff from previous runs
    os.makedirs("logs", exist_ok=True)
    for log in os.listdir("logs"):
        os.remove("logs/" + log)

    # main loop
    
    for _beta in beta:
        for _alfa in alfa:
            
            for file in files:
                with open(file) as f:
                    lines = f.readlines()[6:-1]

                with open("logs/" + file + "-" + _alfa + "-" + _beta + ".txt", "x"):
                    pass
                
                # parse nodes from files
                nodes = []
                for line in lines:
                    x, y = line.strip().split()[1:]
                    nodes.append([float(x), float(y)])

                nodes = np.array(nodes)

                # calculate distances
                distances = np.zeros((nodes.shape[0], nodes.shape[0]))
                for index, point in enumerate(nodes):
                    distances[index] = np.sqrt(((nodes - point) ** 2).sum(axis = 1))

                # calculate inverses
                with np.errstate(all = "ignore"):
                    distances = 1 / distances

                # substitute with 0 to avoid errors
                distances[distances == np.inf] = 0
                distances = distances ** _beta

                # init pheromones trail
                pheromones = np.zeros((nodes.shape[0], nodes.shape[0]))

                # init variables
                min_distance = 0
                min_path = 0
                cont = 0
                start = time.time()
                
                with open("logs/" + file + "-" + _alfa + "-" + _beta + ".txt", "a") as f:

                    while cont < iterations and time.time() < start + secs:
                        
                        # init ants at random
                        positions = np.random.randint(nodes.shape[0], size = size)

                        # move ants
                        paths = np.zeros((nodes.shape[0], positions.shape[0]), dtype = int) - 1
                        paths[0] = positions

                        # for nodes after start to end
                        for node in range(1, nodes.shape[0]):
                            
                            # for each ant
                            for ant in range(positions.shape[0]):

                                next_location_probability = (distances[positions[ant]] ** _alfa + pheromones[positions[ant]] ** _beta / distances[positions[ant]].sum() ** _alfa + pheromones[positions[ant]].sum() ** _beta)

                                next_position = np.argwhere(next_location_probability == np.amax(next_location_probability))[0][0]
                                f.write(f"next_position={next_position}")

                                # check it's new
                                while next_position in paths[:, ant]:
                                    next_location_probability[next_position] = 0.0

                                    next_position = np.argwhere(next_location_probability == np.amax(next_location_probability))[0][0]

                                # add node to path
                                paths[node, ant] = next_position
                                f.write(f"Added next_position={next_position} by ant={ant} to paths")

                                # update pheromones
                                pheromones[node, next_position] = pheromones[node, next_position] + o
                                f.write(f"Updated pheromones in next_position={next_position} to {pheromones[node, next_position]}")

                        # paths taken by ants
                        paths = np.swapaxes(paths, 0, 1)

                        # evaporate pheromones
                        pheromones *= (1 - p)

                        for path in paths:
                            distance = 0

                            for node in range(1, path.shape[0]):

                                # calculate distance to the last node
                                distance += np.sqrt(((nodes[path[node]] - nodes[path[node - 1]]) ** 2).sum())

                            # update minimum distance and path if less nor non existent
                            if not min_distance or distance < min_distance:
                                f.write(f"Changed min_distance={min_distance} and min_path={min_path} to distance={distance} and path={path}")
                                min_distance = distance
                                min_path = path

                    # copy and append first node to the end to form a closed loop
                    min_path = np.append(min_path, min_path[0])

            
if __name__ == "__main__":
    main()