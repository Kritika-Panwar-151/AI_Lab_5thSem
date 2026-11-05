def count_conflicts(state):
    conflicts = 0
    n = len(state)

    for i in range(n):
        for j in range(i + 1, n):
            if abs(state[i] - state[j]) == abs(i - j):
                conflicts += 1

    return conflicts


def generate_neighbours(state):
    neighbours = []
    n = len(state)

    for i in range(n):
        for j in range(i + 1, n):
            neighbour = state.copy()
            neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
            neighbours.append(neighbour)

    return neighbours


def hill_climbing():
    n = 4

    current = list(map(
        int,
        input("Enter initial state (e.g. 2 3 1 4): ").split()
    ))

    if len(current) != n or sorted(current) != [1, 2, 3, 4]:
        print("Invalid state! Enter a permutation of 1, 2, 3, 4.")
        return

    current_conflicts = count_conflicts(current)
    iteration = 0

    print(f"\nInitial State = {current}")
    print(f"Conflicts = {current_conflicts}")

    while True:
        iteration += 1

        print(f"\n{iteration})")
        print(f"Current State = {current}")
        print(f"Current Conflicts = {current_conflicts}")

        neighbours = generate_neighbours(current)
        results = []

        print("\nNeighbour Conflicts:")

        for neighbour in neighbours:
            conflicts = count_conflicts(neighbour)
            results.append((conflicts, neighbour))
            print(f"{neighbour} -> {conflicts}")

        best_conflicts, best_neighbour = min(
            results, key=lambda x: x[0]
        )

        print("\nBest Neighbour =", best_neighbour)
        print("Lowest Conflicts =", best_conflicts)

        if best_conflicts < current_conflicts:
            print(
                f"{current_conflicts} > {best_conflicts}"
                " -> UPDATE"
            )

            current = best_neighbour
            current_conflicts = best_conflicts

            print("Updated State =", current)
            print("Updated Conflicts =", current_conflicts)

            if current_conflicts == 0:
                print("\nFINAL RESULT: Solution Found")
                print("Final State =", current)
                print("Final Conflicts = 0")
                print("Total Iterations =", iteration)
                return

        else:
            print(
                f"{current_conflicts} <= {best_conflicts}"
                " -> NO BETTER NEIGHBOUR"
            )
            print("\nFINAL RESULT: Stopped at local minimum")
            print("Final State =", current)
            print("Final Conflicts =", current_conflicts)
            print("Total Iterations =", iteration)
            return


hill_climbing()
