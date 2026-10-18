import heapq

def astar(adj, h, start, goal):
    n = len(adj)
    start -= 1
    goal -= 1

    g = [float('inf')] * n
    parent = [None] * n
    frontier = []
    expanded = set()

    g[start] = 0
    heapq.heappush(frontier, (h[start], start))

    iteration = 1

    while frontier:
        # Remove the node with the lowest f value
        f_value, current = heapq.heappop(frontier)

        if current in expanded:
            continue

        print(f"\n{iteration})")

        # Show frontier before expanding the selected node
        frontier_nodes = sorted({
            node for _, node in frontier
            if node not in expanded
        } | {current})

        print("Frontier =", {
            chr(node + 65) for node in frontier_nodes
        })

        print("Node Expanded =", chr(current + 65))

        # Goal reached
        if current == goal:
            path = []
            node = goal

            while node is not None:
                path.append(node)
                node = parent[node]

            path.reverse()

            print("\nFinal Path =", " -> ".join(
                chr(node + 65) for node in path
            ))
            print("Total Cost =", g[goal])
            return

        expanded.add(current)

        # Calculate costs for successors
        for neighbor in range(n):
            edge_cost = adj[current][neighbor]

            if edge_cost == 0 or neighbor in expanded:
                continue

            new_g = g[current] + edge_cost
            new_f = new_g + h[neighbor]

            print(
                f"f({chr(neighbor + 65)}) = "
                f"g({chr(neighbor + 65)}) + "
                f"h({chr(neighbor + 65)}) = "
                f"{new_g} + {h[neighbor]} = {new_f}"
            )

            if new_g < g[neighbor]:
                g[neighbor] = new_g
                parent[neighbor] = current
                heapq.heappush(frontier, (new_f, neighbor))

        # Show updated frontier
        frontier_nodes = sorted({
            node for _, node in frontier
            if node not in expanded
        })

        print("Frontier =", {
            chr(node + 65) for node in frontier_nodes
        })
        print("Node Expanded =", {
            chr(node + 65) for node in expanded
        })

        iteration += 1

    print("\nFAILURE: Goal not reachable")


# Input
n = int(input("Enter number of nodes: "))

print("Enter adjacency matrix (0 means no edge):")
adj = [list(map(int, input().split())) for _ in range(n)]

h = list(map(int, input("Enter heuristic values: ").split()))

start = input("Enter start node (A, B, C, ...): ").upper()
goal = input("Enter goal node (A, B, C, ...): ").upper()

start = ord(start) - 65 + 1
goal = ord(goal) - 65 + 1

if (len(h) != n or any(len(row) != n for row in adj)
        or not (1 <= start <= n) or not (1 <= goal <= n)):
    print("Invalid input")
else:
    astar(adj, h, start, goal)
