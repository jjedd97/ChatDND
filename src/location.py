from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class Location:
    def __init__(self, description, length, width, occupied, player_location=(0, 0)):
        self.description = description
        self.width = width
        self.length = length
        self.occupied = occupied
        self.player_location = player_location

    def print_grid(self):
        for i in range(self.length):
            for j in range(self.width):
                for x, y, symbol in self.occupied:
                    if (i, j) == (x, y):
                        print(symbol, end=' ')
                        break
                else:
                    if (i, j) == self.player_location:
                        print('P', end=' ')  # Represent player with 'P'
                    else:
                        print('.', end=' ')
            print()

    def move(self, direction):
        # TODO diagonal
        x, y = self.player_location

        if direction == 'up':
            new_location = (x - 1, y)
        elif direction == 'down':
            new_location = (x + 1, y)
        elif direction == 'left':
            new_location = (x, y - 1)
        elif direction == 'right':
            new_location = (x, y + 1)
        else:
            print("Invalid direction.")
            return
        # TODO this will never be true
        if new_location not in self.occupied:
            self.player_location = new_location
        else:
            print("Cannot move to an occupied square.")
            return

    def move_player(self, num_moves, target_coords):
        grid = [[1 for _ in range(self.width+1)] for _ in range(self.length+1)]
        for coord in self.occupied:
            grid[coord[0]][coord[1]] = 0
        grid = Grid(matrix=grid)
        start = grid.node(*self.player_location)
        end = grid.node(*target_coords)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)

        if 0 < len(path) <= num_moves:
            self.player_location = target_coords
            return target_coords
        else:
            return self.player_location

    def move_object(self, num_moves, starting_cords, target_cords) -> bool:
        grid = [[1 for _ in range(self.width)] for _ in range(self.length)]
        for coord in self.occupied:
            grid[coord[0]][coord[1]] = 0
        grid = Grid(matrix=grid)
        start = grid.node(*starting_cords)
        end = grid.node(*target_cords)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)

        if 0 < len(path) <= num_moves:
            for i in range(len(self.occupied)):
                if self.occupied[i][0] == starting_cords[0] and self.occupied[i][1] == starting_cords[1]:
                    self.occupied[i] = (target_cords[0], target_cords[1], self.occupied[i][2])
            return True
        else:
            return False

    def get_valid_neighbors(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the current position

                new_x, new_y = x + dx, y + dy

                if 0 <= new_x <= self.width and 0 <= new_y <= self.length:
                    neighbors.append((new_x, new_y))
        return neighbors

    def update_object_char(self, x, y, new_char):
        for i in range(len(self.occupied)):
            if self.occupied[i][0] == x and self.occupied[i][1] == y:
                self.occupied[i] = (x, y, new_char)
