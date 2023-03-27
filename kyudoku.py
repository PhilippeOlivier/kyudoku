"""Kyudoku solver using CP-SAT."""


from ortools.sat.python import cp_model


def kyudoku():
    """Solve the problem."""
    board, position = input_tiles()
    model = build_model(board, position)

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    assert solver.StatusName(status) in ("FEASIBLE", "OPTIMAL")

    solution = [[solver.Value(model.x[i][j]) for j in range(6)] for i in range(6)]
    print_solution(board, solution)


def input_tiles():
    """Ask the user to input tiles and return the board.

    Returns:
      A matrix of the board, and a tuple indicating the position of the preselected tile.
    """
    print("Input the tiles row by row, and put the preselected tile in parenthesis.")
    rows = []
    position = None
    for i in range(6):
        row = input(f"Row {i + 1}: ")
        row = [x for x in list(row) if x != ' ']
        if len(row) == 6:
            rows.append([int(x) for x in row])
            continue
        position = (i, row.index('('))
        rows.append(tuple(int(x) for x in row if x not in "()"))

    return tuple(rows), position


def build_model(board, position):
    """Build and return the model.

    Args:
      board: The tiles.
      position: Position of the predetermined tile.
    """
    model = cp_model.CpModel()

    # x[i][j] indicates if the tile at position (i, j) is selected in the solution
    model.x = [[model.NewBoolVar(f"x_{i}_{j}") for i in range(6)]
               for j in range(6)]

    # The preselected tile is already fixed
    model.Add(model.x[position[0]][position[1]] == 1)

    # The sum of the rows and the columns must be <= 9
    for i in range(6):
        model.Add(cp_model.LinearExpr.WeightedSum(model.x[i], board[i]) <= 9)
        model.Add(cp_model.LinearExpr.WeightedSum([model.x[j][i] for j in range(6)],
                                                  [board[j][i] for j in range(6)]) <= 9)

    # Each number can only be used once
    # unique[j][k] indicates that number i is found at position (j, k)
    for i in range(1, 10):
        unique = [[model.NewBoolVar(f"unique_{i}_{j}_{k}") for j in range(6)]
                  for k in range(6)]
        model.Add(cp_model.LinearExpr.Sum([cp_model.LinearExpr.Sum(unique[j])
                                           for j in range(6)])
                  == 1)
        for j in range(6):
            for k in range(6):
                model.Add(board[j][k] * model.x[j][k] == i).OnlyEnforceIf(unique[j][k])

    return model


def print_solution(board, solution):
    """Print the solution."""
    for i in range(6):
        for j in range(6):
            if solution[i][j] == 1:
                print("\u001b[47;1m\u001b[30m" + str(board[i][j]) + "\u001b[0m", end=" ")
            else:
                print(str(board[i][j]), end=" ")
        print()


if __name__ == "__main__":
    kyudoku()
