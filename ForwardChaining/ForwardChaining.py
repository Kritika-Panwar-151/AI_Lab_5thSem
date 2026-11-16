# Forward Chaining for First-Order Logic

# Facts in the Knowledge Base
KB = {
    ("American", "Robert"),
    ("Missile", "T1"),
    ("Owns", "A", "T1"),
    ("Enemy", "A", "America")
}

# Rules: (premises, conclusion)
rules = [
    (
        [
            ("American", "?p"),
            ("Weapon", "?q"),
            ("Sells", "?p", "?q", "?r"),
            ("Hostile", "?r")
        ],
        ("Criminal", "?p")
    ),
    (
        [
            ("Missile", "?x"),
            ("Owns", "A", "?x")
        ],
        ("Sells", "Robert", "?x", "A")
    ),
    (
        [("Missile", "?x")],
        ("Weapon", "?x")
    ),
    (
        [("Enemy", "?x", "America")],
        ("Hostile", "?x")
    )
]


# Check whether a term is a variable
def is_variable(term):
    return term.startswith("?")


# Unify two predicates using substitutions
def unify(pattern, fact, substitution):
    if pattern[0] != fact[0] or len(pattern) != len(fact):
        return None

    substitution = substitution.copy()

    for p, f in zip(pattern[1:], fact[1:]):

        # Replace variable if it already has a substitution
        if is_variable(p):
            if p in substitution:
                if substitution[p] != f:
                    return None
            else:
                substitution[p] = f

        elif p != f:
            return None

    return substitution


# Apply substitutions to a predicate
def substitute(predicate, substitution):
    return tuple(
        substitution.get(term, term)
        for term in predicate
    )


# Match all premises of a rule with facts in KB
def match_premises(premises, facts):
    substitutions = [{}]

    for premise in premises:
        new_substitutions = []

        for substitution in substitutions:
            for fact in facts:
                result = unify(premise, fact, substitution)

                if result is not None:
                    new_substitutions.append(result)

        substitutions = new_substitutions

        if not substitutions:
            break

    return substitutions


# Forward Chaining Algorithm
def forward_chaining(KB, rules, query):

    KB = set(KB)
    iteration = 1

    print("Initial Facts:")
    for fact in sorted(KB):
        print(fact)

    while True:
        new_facts = set()

        print(f"\nIteration {iteration}:")

        for premises, conclusion in rules:

            substitutions = match_premises(premises, KB)

            for substitution in substitutions:

                derived_fact = substitute(conclusion, substitution)

                # Add only facts not already present in KB
                if derived_fact not in KB:
                    new_facts.add(derived_fact)

                    print("Matched:", [
                        substitute(p, substitution)
                        for p in premises
                    ])

                    print("Derived:", derived_fact)

        # Stop when no new facts can be inferred
        if not new_facts:
            break

        KB.update(new_facts)
        iteration += 1

    print("\nFinal Knowledge Base:")
    for fact in sorted(KB):
        print(fact)

    if query in KB:
        print("\nQuery:", query)
        print("Result: TRUE")
        print("Robert is a criminal.")
    else:
        print("\nQuery:", query)
        print("Result: FALSE")
        print("Could not prove that Robert is a criminal.")


# Query
query = ("Criminal", "Robert")

forward_chaining(KB, rules, query)
