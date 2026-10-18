def dfs(state, goal, visited, cost):

    if state == goal:
        return cost

    visited.append(state)

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

            if new_state not in visited:

                result = dfs(new_state, goal, visited, cost + 1)

                if result is not None:
                    return result

    return None


print("Enter Initial State (3x3, 0 for blank):")

start = []
for i in range(3):
    start = start + list(map(int, input().split()))


print("Enter Goal State (3x3, 0 for blank):")

goal = []
for i in range(3):
    goal = goal + list(map(int, input().split()))


visited = []

cost = dfs(start, goal, visited, 0)

print("\nStates visited:", len(visited))
print("Cost:", cost)
print("Time Complexity: O(b^d)")
print("Space Complexity: O(bd)")
