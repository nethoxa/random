import random
import time

from copy import deepcopy

class Differential:
    # average init
    def __init__(
            self, 
            cities,
            poblation_size: int,
            greedy_size: int,
            share_random: int,
            stop: int,
            _time: int,
            is_EDA: bool,
            kBest: int,
            elite: int,
            seed: int,
            file: str
        ) -> None:

        self.cities = cities
        self.n = len(cities)
        self.poblation_size = poblation_size
        self.greedy_size = greedy_size
        self.share_random = share_random
        self.stop = stop
        self.time = _time
        self.kBest = kBest
        self.elite = elite
        self.seed = seed
        self.file = file
        self.solution = []

        poblation = self.initialize_poblation()
        self.poblation = poblation
        self.is_EDA = is_EDA

    def calculate_distance(self, path: list) -> float:
        total_distance = 0

        for i in range(self.n - 1):
            total_distance += self.cities[path[i]][path[i + 1]]

        total_distance += self.cities[path[-1]][path[0]]

        return total_distance
    
    # initialize
    def initialize_poblation(self) -> list:
        poblation = []
        local_cities = [_ for _ in range(self.n)]

        for _ in range(self.poblation_size):
            local = deepcopy(local_cities)

            if random.random() < self.share_random:
                random.shuffle(local)
                poblation.append(local)

            else:
                start = random.choice(local)
                local.remove(start)
                current = start
                solution = [start]

                while local:
                    candidates = []

                    for city in local:
                        distance = self.cities[current][city]
                        candidates.append((city, distance))

                    candidates.sort(key=lambda x: x[1])

                    aux = random.choice(candidates[:self.greedy_size])[0]
                    solution.append(aux)
                    local.remove(aux)
                    current = aux

                poblation.append(solution)

            del local
                
        return poblation

    # operator ox2
    def operator_OX2(self, parent1: list, parent2: list) -> list:
        k = random.randint(0, len(parent1) - 1)
        sample = random.sample(parent2, k)
        child = deepcopy(parent1)

        for i in parent1:
            if i in sample:
                child[child.index(i)] = None
 
        cont = 0
        for i in range(len(parent1)):
            if parent1[i] in sample:
                child[i] = sample[cont]
                cont += 1

        return child
        
    # swap operator 2-opt
    def operator_2OPT(self, seq: list, i: int, j: int) -> list:
        seq_aux = deepcopy(seq)
        aux = seq_aux[i]
        seq_aux[i] = seq_aux[j]
        seq_aux[j] = aux

        return seq_aux
    
    # Torneos
    def tournament_selection(self, poblation: list, mode_best: bool) -> list:
        selected = random.sample(poblation, self.kBest)
        size = len(poblation)

        for _ in range(size):
            # Seleccionar kBest individuos al azar
            participants = random.sample(poblation, self.kBest)

            for i in range(len(selected)):
                for j in range(len(participants)):

                    # Looking for the lowest path cost
                    if mode_best:

                        # Swap if the selected has a higher cost
                        if self.calculate_distance(selected[i]) > self.calculate_distance(participants[j]) and participants[j] not in selected:
                            selected[i] = participants[j]

                    # Highest path cost, as it is a tournament between the worst ones
                    else:

                        # Swap if the selected has a lower cost
                        if self.calculate_distance(selected[i]) < self.calculate_distance(participants[j]) and participants[j] not in selected:
                            selected[i] = participants[j]

        # If looking for the lowest cost, return the lowest from the lowest
        if mode_best:
            return min(selected, key=lambda x: self.calculate_distance(x))
        
        # Idem for the highest
        else:
            return max(selected, key=lambda x: self.calculate_distance(x))
    
    
    def ternarySwap(self, parent: list) -> list:
        children = []
        banned = [parent]
        target = self.tournament_selection(self.poblation, True)
        banned.append(target)

        al1, al2 = None, None
        participants = [participant for participant in self.poblation if participant not in banned]
        
        # if we are in EDA, we choose them at random
        if self.is_EDA:    
            al1 = random.choice(participants)
            participants.remove(al1)
            al2 = random.choice(participants)
            participants.remove(al2)

        # otherwise via tournament
        else:
            al1 = self.tournament_selection(participants, True)
            participants.remove(al1)
            al2 = self.tournament_selection(participants, True)
            participants.remove(al2)

        cut = random.randint(0, self.poblation_size - 1)

        p = al1.index(parent[cut + 1])
        children = self.operator_2OPT(al1, p, al1.index(parent[p]))

        p = al2.index(parent[cut])
        children = self.operator_2OPT(children, p, children.index(parent[cut]))

        children = self.operator_OX2(children, target)

        return children

    # Run
    def run(self) -> None:
        with open(f"logs/Differential-FILE={self.file}=SEED={self.seed}-POBLATION_SIZE={self.poblation_size}-ELITE={self.elite}-KBEST={self.kBest}-STOP={self.stop}-IS_EDA={self.is_EDA}.txt", "w") as f:
            
            f.write(f"Poblation initialised, running...\n")
            f.write(f"\n")
            f.write(f"\n")
        
            tick = 0
            cont = 0
            best = None
            init = time.time()

            while tick < self.stop and time.time() - init < self.time:
                f.write(f"Doing ternary swap with {self.poblation[cont]}\n")
                children = self.ternarySwap(self.poblation[cont])
                f.write(f"Got {children} after ternary swap")
                cont += 1

                if cont == self.poblation_size:
                    f.write(f"Got {cont}=={self.poblation_size}\n")
                    # Just a check for the first iteration
                    if best:
                        for besty in best:
                            if besty not in self.poblation:

                                # Change the worst with the best from the previous poblation
                                parent_to_change = self.tournament_selection(self.poblation, False)
                                self.poblation[self.poblation.index(parent_to_change)] = besty
                                f.write(f"Changed the worst of children {parent_to_change} with the best from the previous one {besty}\n")

                    # Pick the best from the children poblation
                    aux = deepcopy(self.poblation)
                    aux.sort(key=lambda x: self.calculate_distance(x))

                    # Swap
                    best = aux[0:self.elite + 1]
                    f.write(f"Best is {best}\n")

                    cont = 0

                else:
                    if self.calculate_distance(children) < self.calculate_distance(self.poblation[cont]):
                        self.poblation[cont] = children
                        f.write(f"Changed {self.poblation[cont]} with {children} s\n")
                
                tick += 1

            try:
                self.solution = min(best, key=lambda x: self.calculate_distance(x))

                f.write(f"\n")
                f.write(f"\n")
                f.write(f"Final one is {self.solution} with cost {self.calculate_distance(self.solution)}\n")

            except:
                self.solution = min(self.poblation, key=lambda x: self.calculate_distance(x))

                f.write(f"\n")
                f.write(f"\n")
                f.write(f"This one did last more than what we needed to find a best. Final one is {self.solution} with cost {self.calculate_distance(self.solution)} taken from the poblation\n")

        print("FINISH")


    # Getter
    def getSolution(self) -> list:
        return self.solution
