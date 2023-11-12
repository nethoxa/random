import random
import time

from copy import deepcopy

class TSP:
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
            _time: int
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

        self.solution = []

        poblation = self.initialize_poblation()
        self.poblation = poblation

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
    def tournament_selection(self) -> list:
        selected = []
        size = len(self.poblation)

        for _ in range(size):
            # Seleccionar kBest individuos al azar
            participants = random.sample(self.poblation, self.kBest)

            # Elegir el mejor de los participantes basándose en la función objetivo
            winner = min(participants, key=lambda x: self.calculate_distance(x))
            
            selected.append(winner)

        return selected
    
    # Run
    def run(self) -> None:
        tick = 0
        best = None
        init = time.time()

        while tick < self.stop and len(self.poblation) > 1 and time.time() - init < self.time:
            selected = self.tournament_selection()
            children = []

            for i in range(0, len(selected) - 1, 2):
                parent1, parent2 = selected[i], selected[i + 1]

                if random.random() < self.share_mix:
                    child1 = self.operator_OX2(parent1, parent2)
                    child2 = self.operator_OX2(parent2, parent1)
                    child1, child2 = self.operator_MOC(child1, child2)

                else:
                    child1 = deepcopy(parent1)
                    child2 = deepcopy(parent2)
                    

                if random.random() < self.share_mutation:
                    child1 = self.operator_2OPT(child1, random.choice(list(range(len(child1)))), random.choice(list(range(len(child1)))))
                    child2 = self.operator_2OPT(child2, random.choice(list(range(len(child2)))), random.choice(list(range(len(child2)))))

                children.append(child1)
                children.append(child2)

            self.poblation = children
            aux = min(self.poblation, key=lambda x: self.calculate_distance(x))

            best = aux
            tick += 1

        self.solution = best


    # Getter
    def getSolution(self) -> list:
        return self.solution
