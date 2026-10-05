def dfs(state, goal, path, level, limit, visited):

    # Goal found
    if state == goal:
        visited.append(state)
        return True, level

    # Depth limit reached
    if level == limit:
        visited.append(state)
        return False, level

    visited.append(state)
    path.append(state)

    zero = state.index(0)
    row = zero // 3
    col = zero % 3

    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

    for dr, dc in directions:

        new_row = row + dr
        new_col = col + dc

        if 0 <= new_row < 3 and 0 <= new_col < 3:

            new_zero = new_row * 3 + new_col

            new_state = state.copy()

            new_state[zero], new_state[new_zero] = \
                new_state[new_zero], new_state[zero]

            # Don't visit a state already in current path
            if new_state not in path:

                found, cost = dfs(
                    new_state,
                    goal,
                    path,
                    level + 1,
                    limit,
                    visited
                )

                if found:
                    return True, cost

    # Backtrack
    path.pop()

    return False, level


# ---------------- INPUT ----------------

print("Enter Initial State (3x3, 0 for blank):")

start = []

for i in range(3):
    start = start + list(map(int, input().split()))


print("Enter Goal State (3x3, 0 for blank):")

goal = []

for i in range(3):
    goal = goal + list(map(int, input().split()))


limit = int(input("Enter depth limit: "))


# ---------------- DFS ----------------

path = []
visited = []

found, cost = dfs(start, goal, path, 0, limit, visited)


# ---------------- OUTPUT ----------------

if found:
    print("\nResult: FOUND")
    print("Cost:", cost)
else:
    print("\nResult: LIMIT EXCEEDED")

print("States visited:", len(visited))
print("Time Complexity: O(b^l)")
print("Space Complexity: O(bl)")
