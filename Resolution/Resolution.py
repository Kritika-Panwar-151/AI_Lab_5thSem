import re
from itertools import count

# ============================================================
# FIRST-ORDER LOGIC CNF CONVERTER + RESOLUTION PROVER
# Supports: predicates, constants, variables, function terms,
#           AND, OR, NOT, implication, biconditional,
#           forall, exists, unification and resolution.
# ============================================================

# --------------------------- TOKENIZER -----------------------

def tokenize(text):
    replacements = {
        "∀": " forall ", "∃": " exists ",
        "∧": " AND ", "∨": " OR ", "¬": " NOT ",
        "→": " -> ", "↔": " <-> ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    raw = re.findall(
        r"<->|->|[(),.&|~!:]|[A-Za-z_][A-Za-z_0-9]*",
        text
    )
    tokens = []
    for token in raw:
        upper = token.upper()
        if upper == "AND":
            tokens.append("&")
        elif upper == "OR" or token == "V":
            tokens.append("|")
        elif upper == "NOT":
            tokens.append("~")
        elif upper == "FORALL":
            tokens.append("forall")
        elif upper == "EXISTS":
            tokens.append("exists")
        else:
            tokens.append(token)
    return tokens


# ---------------------------- PARSER -------------------------

class Parser:
    def __init__(self, text):
        self.tokens = tokenize(text)
        self.pos = 0
        self.bound = set()

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of formula")
        self.pos += 1
        return token

    def accept(self, token):
        if self.peek() == token:
            self.take()
            return True
        return False

    def parse(self):
        if not self.tokens:
            raise ValueError("Formula cannot be empty")
        result = self.parse_iff()
        if self.peek() is not None:
            raise ValueError("Unexpected token: " + self.peek())
        return result

    # Precedence: NOT > AND > OR > IMPLIES > IFF
    def parse_iff(self):
        node = self.parse_imp()
        while self.accept("<->"):
            node = ("iff", node, self.parse_imp())
        return node

    def parse_imp(self):
        node = self.parse_or()
        if self.accept("->"):
            node = ("imp", node, self.parse_imp())
        return node

    def parse_or(self):
        node = self.parse_and()
        while self.accept("|"):
            node = ("or", node, self.parse_and())
        return node

    def parse_and(self):
        node = self.parse_unary()
        while self.accept("&"):
            node = ("and", node, self.parse_unary())
        return node

    def parse_unary(self):
        if self.accept("~"):
            return ("not", self.parse_unary())

        if self.peek() in ("forall", "exists"):
            quantifier = self.take()
            variable = self.take()
            if not re.fullmatch(r"[A-Za-z_]\w*", variable):
                raise ValueError("Invalid quantified variable: " + variable)
            self.accept(".") or self.accept(":")
            old_bound = self.bound.copy()
            self.bound.add(variable)
            body = self.parse_unary()
            self.bound = old_bound
            return (quantifier, variable, body)

        if self.accept("("):
            node = self.parse_iff()
            if not self.accept(")"):
                raise ValueError("Missing closing parenthesis")
            return node

        return self.parse_atom()

    def parse_term(self):
        name = self.take()
        if not re.fullmatch(r"[A-Za-z_]\w*", name):
            raise ValueError("Invalid term: " + name)

        if self.accept("("):
            args = []
            if not self.accept(")"):
                while True:
                    args.append(self.parse_term())
                    if self.accept(")"):
                        break
                    if not self.accept(","):
                        raise ValueError("Expected ',' in function arguments")
            return ("func", name, tuple(args))

        # Conventional notation: bound names and single lowercase letters
        # are variables; names such as John, Apple, Peanuts are constants.
        if name in self.bound or re.fullmatch(r"[a-z]", name):
            return "?" + name
        return name

    def parse_atom(self):
        predicate = self.take()
        if not re.fullmatch(r"[A-Za-z_]\w*", predicate):
            raise ValueError("Expected a predicate or proposition, got: " + predicate)

        args = []
        if self.accept("("):
            if not self.accept(")"):
                while True:
                    args.append(self.parse_term())
                    if self.accept(")"):
                        break
                    if not self.accept(","):
                        raise ValueError("Expected ',' between predicate arguments")
        return ("atom", predicate, tuple(args))


def parse(text):
    return Parser(text).parse()


# ------------------------ AST DISPLAY ------------------------

def is_var(term):
    return isinstance(term, str) and term.startswith("?")


def term_to_text(term):
    if isinstance(term, tuple) and term[0] == "func":
        return term[1] + "(" + ",".join(term_to_text(a) for a in term[2]) + ")"
    return term[1:] if is_var(term) else term


def formula_to_text(node):
    op = node[0]
    if op == "atom":
        if not node[2]:
            return node[1]
        return node[1] + "(" + ",".join(term_to_text(a) for a in node[2]) + ")"
    if op == "not":
        child = formula_to_text(node[1])
        return "¬" + ("(" + child + ")" if node[1][0] in ("and", "or", "imp", "iff") else child)
    if op in ("and", "or", "imp", "iff"):
        symbol = {"and": "∧", "or": "∨", "imp": "→", "iff": "↔"}[op]
        return "(" + formula_to_text(node[1]) + " " + symbol + " " + formula_to_text(node[2]) + ")"
    if op in ("forall", "exists"):
        symbol = "∀" if op == "forall" else "∃"
        return symbol + node[1] + " (" + formula_to_text(node[2]) + ")"
    return str(node)


def contains_op(node, operations):
    if not isinstance(node, tuple) or not node:
        return False
    op = node[0]
    if op in operations:
        return True
    if op == "not":
        return contains_op(node[1], operations)
    if op in ("and", "or", "imp", "iff"):
        return contains_op(node[1], operations) or contains_op(node[2], operations)
    if op in ("forall", "exists"):
        return contains_op(node[2], operations)
    return False


# ------------------- CNF TRANSFORMATION HELPERS --------------

def eliminate_implications(node):
    op = node[0]
    if op == "atom":
        return node
    if op == "not":
        return ("not", eliminate_implications(node[1]))
    if op == "imp":
        a = eliminate_implications(node[1])
        b = eliminate_implications(node[2])
        return ("or", ("not", a), b)
    if op == "iff":
        a = eliminate_implications(node[1])
        b = eliminate_implications(node[2])
        return ("and", ("or", ("not", a), b), ("or", ("not", b), a))
    if op in ("and", "or"):
        return (op, eliminate_implications(node[1]), eliminate_implications(node[2]))
    if op in ("forall", "exists"):
        return (op, node[1], eliminate_implications(node[2]))
    return node


def to_nnf(node, negated=False):
    op = node[0]
    if op == "atom":
        return ("not", node) if negated else node
    if op == "not":
        return to_nnf(node[1], not negated)
    if op in ("and", "or"):
        new_op = op if not negated else ("or" if op == "and" else "and")
        return (new_op, to_nnf(node[1], negated), to_nnf(node[2], negated))
    if op in ("forall", "exists"):
        new_op = op if not negated else ("exists" if op == "forall" else "forall")
        return (new_op, node[1], to_nnf(node[2], negated))
    raise ValueError("Implications must be eliminated before NNF")


standard_counter = count(1)
skolem_counter = count(1)


def replace_term(term, substitution):
    if is_var(term):
        if term in substitution:
            return replace_term(substitution[term], substitution)
        return term
    if isinstance(term, tuple) and term[0] == "func":
        return ("func", term[1], tuple(replace_term(a, substitution) for a in term[2]))
    return term


def substitute_ast(node, substitution):
    op = node[0]
    if op == "atom":
        return ("atom", node[1], tuple(replace_term(a, substitution) for a in node[2]))
    if op == "not":
        return ("not", substitute_ast(node[1], substitution))
    if op in ("and", "or"):
        return (op, substitute_ast(node[1], substitution), substitute_ast(node[2], substitution))
    if op in ("forall", "exists"):
        # Bound variables are standardized apart before Skolemization.
        return (op, node[1], substitute_ast(node[2], substitution))
    return node


def rename_term_for_standardization(term, mapping):
    if is_var(term):
        return mapping.get(term, term)
    if isinstance(term, tuple) and term[0] == "func":
        return ("func", term[1], tuple(rename_term_for_standardization(a, mapping) for a in term[2]))
    return term


def standardize_apart(node, mapping=None):
    if mapping is None:
        mapping = {}
    op = node[0]
    if op == "atom":
        return ("atom", node[1], tuple(rename_term_for_standardization(a, mapping) for a in node[2]))
    if op == "not":
        return ("not", standardize_apart(node[1], mapping))
    if op in ("and", "or"):
        return (op, standardize_apart(node[1], mapping), standardize_apart(node[2], mapping))
    if op in ("forall", "exists"):
        new_name = "?v" + str(next(standard_counter))
        new_mapping = mapping.copy()
        new_mapping["?" + node[1]] = new_name
        return (op, new_name[1:], standardize_apart(node[2], new_mapping))
    return node


def skolemize(node, universal_variables=None):
    if universal_variables is None:
        universal_variables = []
    op = node[0]
    if op in ("atom", "not"):
        return node
    if op in ("and", "or"):
        return (op, skolemize(node[1], universal_variables), skolemize(node[2], universal_variables))
    if op == "forall":
        return skolemize(node[2], universal_variables + ["?" + node[1]])
    if op == "exists":
        name = "SK" + str(next(skolem_counter))
        if universal_variables:
            skolem_term = ("func", name, tuple(universal_variables))
        else:
            skolem_term = name
        body = substitute_ast(node[2], {"?" + node[1]: skolem_term})
        return skolemize(body, universal_variables)
    return node


def drop_universal_quantifiers(node):
    op = node[0]
    if op == "forall":
        return drop_universal_quantifiers(node[2])
    if op in ("and", "or"):
        return (op, drop_universal_quantifiers(node[1]), drop_universal_quantifiers(node[2]))
    return node


def distribute_and_over_or(node):
    if node[0] not in ("and", "or"):
        return node
    left = distribute_and_over_or(node[1])
    right = distribute_and_over_or(node[2])
    if node[0] == "and":
        return ("and", left, right)
    if left[0] == "and":
        return ("and",
                distribute_and_over_or(("or", left[1], right)),
                distribute_and_over_or(("or", left[2], right)))
    if right[0] == "and":
        return ("and",
                distribute_and_over_or(("or", left, right[1])),
                distribute_and_over_or(("or", left, right[2])))
    return ("or", left, right)


def needs_distribution(node):
    if not isinstance(node, tuple) or not node:
        return False
    op = node[0]
    if op == "or":
        if node[1][0] == "and" or node[2][0] == "and":
            return True
        return needs_distribution(node[1]) or needs_distribution(node[2])
    if op == "and":
        return needs_distribution(node[1]) or needs_distribution(node[2])
    return False


# ------------------------- CLAUSE EXTRACTION -----------------

def get_literals(node):
    if node[0] == "or":
        return get_literals(node[1]) + get_literals(node[2])
    if node[0] == "not" and node[1][0] == "atom":
        atom = node[1]
        return [(False, atom[1], atom[2])]
    if node[0] == "atom":
        return [(True, node[1], node[2])]
    raise ValueError("Formula is not in CNF literal form: " + formula_to_text(node))


def get_clauses(node):
    if node[0] == "and":
        return get_clauses(node[1]) + get_clauses(node[2])
    # An OR-chain is one clause; a single literal is also one clause.
    return [get_literals(node)]


def literal_to_text(literal):
    positive, predicate, args = literal
    atom = predicate if not args else predicate + "(" + ",".join(term_to_text(a) for a in args) + ")"
    return atom if positive else "¬" + atom


def clause_to_text(clause):
    return "{}" if not clause else " ∨ ".join(literal_to_text(x) for x in clause)


def print_formula_set(title, formulas):
    print("\n" + title)
    for index, formula in enumerate(formulas, 1):
        print(f"{index}. {formula_to_text(formula)}")


def convert_formula_set_to_cnf(formulas, heading):
    """Convert a whole list together, displaying the complete list after each stage."""
    global standard_counter, skolem_counter
    standard_counter = count(1)
    skolem_counter = count(1)

    nodes = [parse(item) if isinstance(item, str) else item for item in formulas]

    print("\n" + "=" * 66)
    print(heading)
    print("=" * 66)
    print_formula_set("Input formulas:", nodes)

    # Step 1: eliminate implications and biconditionals only where present.
    if any(contains_op(node, {"imp", "iff"}) for node in nodes):
        nodes = [eliminate_implications(node) for node in nodes]
        print_formula_set("STEP 1 — Eliminate → and ↔:", nodes)
    else:
        print("\nSTEP 1 — Skipped: no implications or biconditionals.")
        print_formula_set("Current formula set:", nodes)

    # Step 2: move negations inward in every formula.
    updated = [to_nnf(node) for node in nodes]
    if updated != nodes:
        nodes = updated
        print_formula_set("STEP 2 — Move ¬ inwards (NNF):", nodes)
    else:
        nodes = updated
        print("\nSTEP 2 — Skipped: all formulas are already in NNF.")
        print_formula_set("Current formula set:", nodes)

    # Step 3: standardize quantified variables apart across the entire set.
    if any(contains_op(node, {"forall", "exists"}) for node in nodes):
        nodes = [standardize_apart(node) for node in nodes]
        print_formula_set("STEP 3 — Standardize variables apart:", nodes)
    else:
        print("\nSTEP 3 — Skipped: no quantified variables.")
        print_formula_set("Current formula set:", nodes)

    # Step 4: Skolemize formulas containing existential quantifiers.
    if any(contains_op(node, {"exists"}) for node in nodes):
        nodes = [skolemize(node) for node in nodes]
        print_formula_set("STEP 4 — Skolemization:", nodes)
    else:
        print("\nSTEP 4 — Skipped: no existential quantifiers.")
        print_formula_set("Current formula set:", nodes)

    # Step 5: remove universal quantifiers.
    if any(contains_op(node, {"forall"}) for node in nodes):
        nodes = [drop_universal_quantifiers(node) for node in nodes]
        print_formula_set("STEP 5 — Drop universal quantifiers:", nodes)
    else:
        print("\nSTEP 5 — Skipped: no universal quantifiers.")
        print_formula_set("Current formula set:", nodes)

    # Step 6: distribute AND over OR only if needed.
    if any(needs_distribution(node) for node in nodes):
        nodes = [distribute_and_over_or(node) for node in nodes]
        print_formula_set("STEP 6 — Distribute ∧ over ∨:", nodes)
    else:
        print("\nSTEP 6 — Skipped: all formulas are already in CNF.")
        print_formula_set("Current formula set:", nodes)

    all_clauses = []
    print("\nCNF clauses:")
    clause_number = 1
    for node in nodes:
        for clause in get_clauses(node):
            all_clauses.append(clause)
            print(f"{clause_number}. {clause_to_text(clause)}")
            clause_number += 1

    return all_clauses


# --------------------------- UNIFICATION ---------------------

def occurs(variable, term, substitution):
    term = replace_term(term, substitution)
    if variable == term:
        return True
    if isinstance(term, tuple) and term[0] == "func":
        return any(occurs(variable, arg, substitution) for arg in term[2])
    return False


def unify_terms(a, b, substitution):
    a = replace_term(a, substitution)
    b = replace_term(b, substitution)
    if a == b:
        return True
    if is_var(a):
        if occurs(a, b, substitution):
            return False
        substitution[a] = b
        return True
    if is_var(b):
        if occurs(b, a, substitution):
            return False
        substitution[b] = a
        return True
    if isinstance(a, tuple) and isinstance(b, tuple):
        if a[0] != "func" or b[0] != "func" or a[1] != b[1] or len(a[2]) != len(b[2]):
            return False
        return all(unify_terms(x, y, substitution) for x, y in zip(a[2], b[2]))
    return False


def unify_literals(a, b):
    if a[0] == b[0] or a[1] != b[1] or len(a[2]) != len(b[2]):
        return None
    substitution = {}
    for left, right in zip(a[2], b[2]):
        if not unify_terms(left, right, substitution):
            return None
    return substitution


def apply_substitution_to_literal(literal, substitution):
    positive, predicate, args = literal
    return (positive, predicate, tuple(replace_term(a, substitution) for a in args))


rename_counter = count(1)


def standardize_clause_apart(clause):
    mapping = {}

    def rename(term):
        if is_var(term):
            if term not in mapping:
                mapping[term] = "?r" + str(next(rename_counter))
            return mapping[term]
        if isinstance(term, tuple) and term[0] == "func":
            return ("func", term[1], tuple(rename(a) for a in term[2]))
        return term

    return [(s, p, tuple(rename(a) for a in args)) for s, p, args in clause]


def resolve_clauses(clause1, clause2):
    clause1 = standardize_clause_apart(clause1)
    clause2 = standardize_clause_apart(clause2)
    resolvents = []

    for i, literal1 in enumerate(clause1):
        for j, literal2 in enumerate(clause2):
            substitution = unify_literals(literal1, literal2)
            if substitution is None:
                continue

            remaining = clause1[:i] + clause1[i + 1:] + clause2[:j] + clause2[j + 1:]
            resolvent = [apply_substitution_to_literal(lit, substitution) for lit in remaining]

            # Remove duplicate literals.
            unique = []
            for lit in resolvent:
                if lit not in unique:
                    unique.append(lit)

            # Discard tautologies such as P(a) OR ¬P(a).
            tautology = any((not sign, pred, args) in unique for sign, pred, args in unique)
            if not tautology:
                resolvents.append((unique, substitution))

    return resolvents


# ---------------------- DUPLICATE CLAUSE CHECK ---------------

def canonical_clause_key(clause):
    # Rename variables consistently within a clause for duplicate detection.
    mapping = {}

    def normalize(term):
        if is_var(term):
            if term not in mapping:
                mapping[term] = "?v" + str(len(mapping) + 1)
            return mapping[term]
        if isinstance(term, tuple) and term[0] == "func":
            return ("func", term[1], tuple(normalize(a) for a in term[2]))
        return term

    normalized = [(s, p, tuple(normalize(a) for a in args)) for s, p, args in clause]
    return tuple(sorted(normalized, key=repr))


def substitution_to_text(substitution):
    if not substitution:
        return "{}"
    return "{" + ", ".join(k[1:] + "/" + term_to_text(v) for k, v in substitution.items()) + "}"


# -------------------------- RESOLUTION -----------------------

def resolution_proof(premises, goal, max_clauses=1500, max_steps=10000):
    global rename_counter
    rename_counter = count(1)

    print("\n" + "=" * 66)
    print("ALL PREMISES")
    print("=" * 66)
    for i, premise in enumerate(premises, 1):
        print(f"{i}. {formula_to_text(parse(premise))}")

    # Convert all premises as one set so every stage shows the full updated list.
    premise_clauses = convert_formula_set_to_cnf(
        premises, "CONVERT ALL PREMISES INTO CNF"
    )

    # Negate the goal, then convert that formula separately.
    goal_ast = parse(goal)
    negated_goal_ast = ("not", goal_ast)

    print("\n" + "=" * 66)
    print("NEGATION OF THE GOAL")
    print("=" * 66)
    print("Original goal:", formula_to_text(goal_ast))
    print("Negated goal:", formula_to_text(negated_goal_ast))

    goal_clauses = convert_formula_set_to_cnf(
        [negated_goal_ast], "CONVERT NEGATED GOAL INTO CNF"
    )

    # Combine premise clauses and negated-goal clauses.
    print("\n" + "=" * 66)
    print("FINAL CLAUSE DATABASE (PREMISES + NEGATED GOAL)")
    print("=" * 66)

    clauses = []
    seen = set()
    for clause in premise_clauses + goal_clauses:
        key = canonical_clause_key(clause)
        if key not in seen:
            seen.add(key)
            clauses.append(clause)

    for i, clause in enumerate(clauses, 1):
        print(f"{i}. {clause_to_text(clause)}")

    if any(len(clause) == 0 for clause in clauses):
        print("\nAn empty clause is already present. HENCE PROVED!")
        return True

    print("\n" + "=" * 66)
    print("RESOLUTION")
    print("=" * 66)
    print("New clauses are numbered after the initial clause database.")

    step = len(clauses) + 1
    changed = True

    while changed:
        changed = False
        pair_count = len(clauses)

        for i in range(pair_count):
            for j in range(i + 1, pair_count):
                for resolvent, substitution in resolve_clauses(clauses[i], clauses[j]):
                    key = canonical_clause_key(resolvent)
                    if key in seen:
                        continue

                    seen.add(key)
                    clauses.append(resolvent)
                    changed = True

                    print(
                        f"{step}. {clause_to_text(resolvent)} "
                        f"(Using {i + 1} and {j + 1}; "
                        f"MGU = {substitution_to_text(substitution)})"
                    )

                    if not resolvent:
                        print("\n{} (EMPTY CLAUSE) DERIVED")
                        print("HENCE PROVED!")
                        return True

                    step += 1
                    if len(clauses) >= max_clauses:
                        print("\nResource limit reached: clause limit exceeded.")
                        print("Result is inconclusive; this does NOT mean the goal is false.")
                        return None
                    if step > max_steps:
                        print("\nResource limit reached: resolution step limit exceeded.")
                        print("Result is inconclusive; this does NOT mean the goal is false.")
                        return None

    print("\nNo empty clause could be derived.")
    print("The goal was NOT proved by this resolution search.")
    print("This does not necessarily mean the goal is false.")
    return False


# ---------------------------- MAIN ---------------------------

def main():
    print("\n" + "=" * 62)
    print("          FIRST-ORDER LOGIC: CNF + RESOLUTION")
    print("=" * 62)
    print("\nLOGIC SYMBOLS (copy/paste if desired)")
    print("AND             : ∧   AND   &")
    print("OR              : ∨   OR    V   |")
    print("NOT             : ¬   NOT   ~")
    print("IMPLIES         : →   ->")
    print("BICONDITIONAL   : ↔   <->")
    print("FOR ALL         : ∀   forall")
    print("EXISTS          : ∃   exists")
    print("\nEXAMPLES")
    print("P ∨ Q")
    print("P -> Q")
    print("¬P")
    print("Food(Apple)")
    print("Likes(John,Peanuts)")
    print("∀x (Food(x) → Likes(John,x))")
    print("∃x (Food(x) ∧ Likes(John,x))")

    try:
        raw_n = input("\nEnter number of premises: ").strip()
        n = int(raw_n)
        if n < 0:
            raise ValueError("Number of premises cannot be negative")

        premises = []
        for i in range(n):
            premise = input(f"Enter premise {i + 1}: ").strip()
            if not premise:
                raise ValueError(f"Premise {i + 1} cannot be empty")
            premises.append(premise)

        goal = input("\nEnter statement to prove: ").strip()
        if not goal:
            raise ValueError("Goal cannot be empty")

        resolution_proof(premises, goal)

    except (ValueError, RecursionError) as error:
        print("\nINPUT / PROCESSING ERROR:", error)
    except KeyboardInterrupt:
        print("\nProgram cancelled by user.")


if __name__ == "__main__":
    main()
