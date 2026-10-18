
import random
import math

N = 8


def cost(board):
    conflicts = 0

    for i in range(N):
        for j in range(i + 1, N):
            if board[i] == board[j]:  # Same row
                conflicts += 1

            if abs(board[i] - board[j]) == abs(i - j):  # Diagonal
                conflicts += 1

    return conflicts


def generate_neighbors(board):
    neighbors = []

    for i in range(N):
        for j in range(i + 1, N):
            neighbor = board.copy()
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            neighbors.append(neighbor)

    return neighbors


def simulated_annealing(board):
    current = board.copy()
    T = 1000
    cooling_rate = 0.95
    iterations = 0

    print("\nInitial Configuration:", current)
    print("Initial Conflicts:", cost(current))

    print("\nIteration Details")
    print("-" * 115)
    print(f"{'Iteration':<10} {'Temperature':<13} "
          f"{'Current Cost':<14} {'Neighbor Cost':<15} "
          f"{'Delta E':<10} {'P':<12} {'Decision'}")
    print("-" * 115)

    while T > 0.1:
        if cost(current) == 0:
            break

        iterations += 1

        current_cost = cost(current)
        neighbors = generate_neighbors(current)
        next_board = random.choice(neighbors)
        next_cost = cost(next_board)

        deltaE = current_cost - next_cost

        if deltaE > 0:
            P = 1.0
            current = next_board
            decision = "Accepted"
        else:
            P = math.exp(deltaE / T)

            if random.random() < P:
                current = next_board
                decision = "Accepted"
            else:
                decision = "Rejected"

        # Display the first 3 iterations
        if iterations <= 3:
            print(f"{iterations:<10} {T:<13.4f} "
                  f"{current_cost:<14} {next_cost:<15} "
                  f"{deltaE:<10} {P:<12.6f} {decision}")

        T *= cooling_rate

    print("-" * 115)
    print("\n========== FINAL RESULT ==========")
    print("Initial Configuration :", board)
    print("Final Configuration   :", current)
    print("Number of Conflicts   :", cost(current))
    print("Total Iterations      :", iterations)

    if cost(current) == 0:
        print("Status                : Solution Found")
    else:
        print("Status                : Solution Not Found")

    print("\nFinal Chessboard:")
    for row in range(N):
        for col in range(N):
            if current[col] == row:
                print(" Q ", end="")
            else:
                print(" . ", end="")
        print()


# Main program
board = list(map(int, input(
    "Enter 8 row positions (0-7): "
).replace(",", " ").replace("[", "").replace("]", "").split()))

if len(board) != N or sorted(board) != list(range(N)):
    print("Invalid input! Enter each number from 0 to 7 exactly once.")
else:
    simulated_annealing(board)
