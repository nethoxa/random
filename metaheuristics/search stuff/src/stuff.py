import random

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

def find_non_overlapping_max(matrix):
    if not matrix:
        return []

    num_rows = len(matrix)
    num_cols = len(matrix[0])

    # Initialize lists to keep track of selected maxima and excluded columns
    selected_maxima = []
    excluded_columns = set()

    for row in range(num_rows):
        max_value = None
        max_col = None

        # Find the maximum value in the current row, excluding the columns in excluded_columns
        for col in range(num_cols):
            if col not in excluded_columns:
                value = matrix[row][col]
                if max_value is None or value > max_value:
                    max_value = value
                    max_col = col

        if max_value is not None:
            selected_maxima.append(max_col)
            excluded_columns.add(max_col)

    return selected_maxima

def find_non_overlapping_min(matrix):
    if not matrix:
        return []

    num_rows = len(matrix)
    num_cols = len(matrix[0])

    # Initialize lists to keep track of selected minima and excluded columns
    selected_minima = []
    excluded_columns = set()

    for row in range(num_rows):
        min_value = None
        min_col = None

        # Find the minimum value in the current row, excluding the columns in excluded_columns
        for col in range(num_cols):
            if col not in excluded_columns:
                value = matrix[row][col]
                if min_value is None or value < min_value:
                    min_value = value
                    min_col = col

        if min_value is not None:
            selected_minima.append(min_col)
            excluded_columns.add(min_col)

    return selected_minima

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