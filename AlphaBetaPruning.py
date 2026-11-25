def build_tree():
    root = {
        "type": "MAX",
        "id": "1.1",
        "children": []
    }

    current_level = [root]
    level = 1

    while current_level:
        next_level = []
        child_position = 1

        for node in current_level:
            n = int(input(f"{node['type']} Node {node['id']}: "))

            if n == 0:
                node["type"] = "LEAF"
                node["value"] = int(input(f"Leaf value for {node['id']}: "))
                continue

            next_type = "MIN" if node["type"] == "MAX" else "MAX"

            for i in range(n):
                child = {
                    "type": next_type,
                    "id": f"{level + 1}.{child_position}",
                    "children": []
                }

                node["children"].append(child)
                next_level.append(child)
                child_position += 1

        current_level = next_level
        level += 1

    return root


def print_tree(node, prefix="", is_last=True):
    if node["type"] == "LEAF":
        print(prefix + ("└── " if is_last else "├── ")
              + f"Leaf {node['id']} = {node['value']}")
        return

    print(prefix + ("└── " if is_last else "├── ")
          + f"{node['type']} Node {node['id']}")

    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, child in enumerate(node["children"]):
        print_tree(child, new_prefix, i == len(node["children"]) - 1)


step = 0


def next_step():
    global step
    step += 1
    return step


def alpha_beta(node, alpha, beta):

    if node["type"] == "LEAF":
        print(f"\n        -Leaf {node['id']} = {node['value']}")
        return node["value"]

    s = next_step()
    print(f"\n{s}: Enter {node['type']} Node {node['id']}")
    print(f"        Alpha = {alpha}, Beta = {beta}")

    if node["type"] == "MAX":
        value = float("-inf")

        for i, child in enumerate(node["children"]):
            child_value = alpha_beta(child, alpha, beta)

            value = max(value, child_value)
            alpha = max(alpha, value)

            print(f"        Value = {value}, Alpha = {alpha}, Beta = {beta}")

            if alpha >= beta:
                print(f"        Pruning at MAX Node {node['id']}")

                for pruned in node["children"][i + 1:]:
                    print(f"        Pruned subtree: {pruned['type']} Node {pruned['id']}")

                break

        print(f"        MAX Node {node['id']} returns {value}")
        return value

    else:
        value = float("inf")

        for i, child in enumerate(node["children"]):
            child_value = alpha_beta(child, alpha, beta)

            value = min(value, child_value)
            beta = min(beta, value)

            print(f"        Value = {value}, Alpha = {alpha}, Beta = {beta}")

            if beta <= alpha:
                print(f"        Pruning at MIN Node {node['id']}")

                for pruned in node["children"][i + 1:]:
                    print(f"        Pruned subtree: {pruned['type']} Node {pruned['id']}")

                break

        print(f"        MIN Node {node['id']} returns {value}")
        return value


# Main program
print("Enter number of children for each node.")
print("Enter 0 if the node is a leaf.\n")

root = build_tree()

print("\n========== TREE STRUCTURE ==========")
print_tree(root)

print("\n========== ALPHA-BETA SEARCH ==========")

step = 0
result = alpha_beta(root, float("-inf"), float("inf"))

print("\n========== FINAL RESULT ==========")
print("Optimal value returned by root:", result)
