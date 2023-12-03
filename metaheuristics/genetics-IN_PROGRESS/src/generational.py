import random
import time

from copy import deepcopy

class Generational:
    # average init
    def __init__(
            self, 
            cities,
            poblation_size: int,
            greedy_size: int,
            share_random: float,
            elite: int,
            kBest: int,
            kWorst: int,
            share_mix: float,
            share_mutation: float,
            stop: int,
            _time: int,
            is_OX2: bool,
            seed: int,
            file
        ) -> None:

        self.cities = cities
        self.n = len(cities)
        self.poblation_size = poblation_size
        self.greedy_size = greedy_size
        self.share_random = share_random
        self.elite = elite
        self.kBest = kBest
        self.kWorst = kWorst
        self.share_mix = share_mix
        self.share_mutation = share_mutation
        self.stop = stop
        self.time = _time
        self.seed = seed
        self.file = file

        self.solution = []

        poblation = self.initialize_poblation()
        self.poblation = poblation
        self.is_OX2 = is_OX2

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
        
    
    # operator moc
    def operator_MOC(self, parent1: list, parent2: list) -> list:
        size = len(parent1)

        # Randomly choose the crossover point
        crossover_point = random.randint(0, size - 1)

        # Select the right substrings of the parents
        right_substring_parent1 = parent1[crossover_point:]
        right_substring_parent2 = parent2[crossover_point:]

        # Initialize children with the selected substrings
        child1 = deepcopy(parent1)
        for i in child1:
            if i in right_substring_parent2:
                child1[child1.index(i)] = None
        
        child2 = deepcopy(parent2)
        for i in child2:
            if i in right_substring_parent1:
                child2[child2.index(i)] = None

        cont = 0
        for i in child1:
            if i == None:
                child1[child1.index(i)] = right_substring_parent2[cont]
                cont += 1

        cont = 0
        for i in child2:
            if i == None:
                child2[child2.index(i)] = right_substring_parent1[cont]
                cont += 1

        return child1, child2
        

    # swap operator 2-opt
    def operator_2OPT(self, seq: list, i: int, j: int) -> list:
        seq_aux = deepcopy(seq)
        aux = seq_aux[i]
        seq_aux[i] = seq_aux[j]
        seq_aux[j] = aux

        return seq_aux
    
    # Torneos
    def tournament_selection(self, poblation: list, mode_best: bool) -> int:
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
    
    # Run
    def run(self) -> None:
        with open(f"logs/Generational-FILE={self.file}-SEED={self.seed}-POBLATION_SIZE={self.poblation_size}-ELITE={self.elite}-KBEST={self.kBest}-STOP={self.stop}-IS_OX2={self.is_OX2}.txt", "w") as f:
            
            f.write(f"Poblation initialised, running...\n")
            f.write(f"\n")
            f.write(f"\n")
            
            tick = 0
            best = None
            init = time.time()

            while tick < self.stop and time.time() - init < self.time:
                children = []

                for _ in range(0, self.poblation_size - 1, 2):
                    parent1 = self.tournament_selection(self.poblation, True)
                    parent2 = self.tournament_selection(self.poblation, True)
                    f.write(f"Best binary tournament selected {parent1} and {parent2}\n")

                    # Apply operators
                    if random.random() < self.share_mix:
                        if self.is_OX2:
                            child1 = self.operator_OX2(parent1, parent2)
                            child2 = self.operator_OX2(parent2, parent1)
                            f.write(f"Applied OX2 to {parent1} and {parent2} and got {child1} and {child2}\n")
                        
                        else:
                            child1, child2 = self.operator_MOC(parent1, parent2)
                            f.write(f"Applied MOC to {parent1} and {parent2} and got {child1} and {child2}\n")

                    # Maintain parents
                    else:
                        child1 = deepcopy(parent1)
                        child2 = deepcopy(parent2)
                        
                    # Apply 2OPT
                    if random.random() < self.share_mutation:
                        child1 = self.operator_2OPT(child1, random.choice(list(range(len(child1)))), random.choice(list(range(len(child1)))))
                        child2 = self.operator_2OPT(child2, random.choice(list(range(len(child2)))), random.choice(list(range(len(child2)))))
                        f.write(f"Applied 2OPT to {parent1} and {parent2} and got {child1} and {child2}\n")

                    children.append(child1)
                    children.append(child2)

                # Just a check for the first iteration
                if best:
                    for besty in best:
                        if besty not in children:

                            # Change the worst with the best from the previous poblation
                            parent_to_change = self.tournament_selection(children, False)
                            children[children.index(parent_to_change)] = besty
                            f.write(f"Changed the worst of children {parent_to_change} with the best from the previous one {besty}\n")

                # Pick the best from the children poblation
                aux = deepcopy(children)
                aux.sort(key=lambda x: self.calculate_distance(x))

                # Swap
                best = aux[0:self.elite]
                f.write(f"Best is {best}\n")
                self.poblation = children

                tick += 1

            self.solution = min(best, key=lambda x: self.calculate_distance(x))

            f.write(f"\n")
            f.write(f"\n")
            f.write(f"Final one is {self.solution} with cost {self.calculate_distance(self.solution)}\n")

        print("FINISH")

    # Getter
    def getSolution(self):
        return self.solution[0], self.calculate_distance(self.solution[0])
