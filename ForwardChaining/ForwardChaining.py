import re


# -------------------- PARSING --------------------

def parse_literal(text):
    text = text.strip()
    negated = False

    if text.startswith("¬") or text.startswith("~"):
        negated = True
        text = text[1:].strip()
    elif re.match(r"(?i)^NOT\s+", text):
        negated = True
        text = re.sub(r"(?i)^NOT\s+", "", text).strip()

    match = re.fullmatch(r"([A-Za-z_]\w*)\s*\((.*?)\)", text)

    if not match:
        raise ValueError(f"Invalid predicate: {text}")

    name = match.group(1)
    args_text = match.group(2).strip()
    args = [arg.strip() for arg in args_text.split(",")] if args_text else []

    if any(not arg for arg in args):
        raise ValueError(f"Invalid arguments: {text}")

    return name, args, negated


def format_literal(literal):
    name, args, negated = literal
    prefix = "¬" if negated else ""
    return prefix + name + "(" + ",".join(args) + ")"


def parse_rule(text):
    parts = re.split(r"->|=>|⟹", text, maxsplit=1)

    if len(parts) != 2:
        raise ValueError("Rule must contain an implication.")

    body_text = parts[0].strip()
    head_text = parts[1].strip()

    # &, ^, ∧, /\, AND
    body_parts = re.split(
        r"\s*(?:&|\^|∧|/\\|(?i:AND))\s*",
        body_text
    )

    body = [parse_literal(p) for p in body_parts if p.strip()]
    head = parse_literal(head_text)

    if not body:
        raise ValueError("Rule body cannot be empty.")

    body_variables = {
        arg
        for literal in body
        for arg in literal[1]
        if is_variable(arg)
    }

    head_variables = {
        arg for arg in head[1] if is_variable(arg)
    }

    if not head_variables.issubset(body_variables):
        raise ValueError("Rule head contains unbound variables.")

    return body, head


# -------------------- VARIABLES --------------------

def is_variable(term):
    return bool(term) and term[0].islower()


# -------------------- UNIFICATION --------------------

def substitute_term(term, substitutions):
    while term in substitutions:
        new_term = substitutions[term]

        if new_term == term:
            break

        term = new_term

    return term


def unify_literals(literal1, literal2, substitutions):
    name1, args1, neg1 = literal1
    name2, args2, neg2 = literal2

    if name1 != name2 or neg1 != neg2:
        return None

    if len(args1) != len(args2):
        return None

    subs = substitutions.copy()

    for a, b in zip(args1, args2):
        a = substitute_term(a, subs)
        b = substitute_term(b, subs)

        if a == b:
            continue

        if is_variable(a):
            subs[a] = b
        elif is_variable(b):
            subs[b] = a
        else:
            return None

    return subs


def substitute_literal(literal, substitutions):
    name, args, negated = literal

    new_args = [
        substitute_term(arg, substitutions)
        for arg in args
    ]

    return name, new_args, negated


# -------------------- MATCHING PREMISES --------------------

def match_premises(premises, kb, substitutions=None):
    if substitutions is None:
        substitutions = {}

    if not premises:
        return [substitutions]

    first = premises[0]
    remaining = premises[1:]

    results = []

    first = substitute_literal(first, substitutions)

    for fact in kb:
        new_subs = unify_literals(first, fact, substitutions)

        if new_subs is not None:
            results.extend(
                match_premises(remaining, kb, new_subs)
            )

    return results


# -------------------- DISPLAY --------------------

def display_kb(kb, width=100):
    facts = [format_literal(fact) for fact in kb]

    lines = []
    current_line = ""

    for fact in facts:
        addition = fact if not current_line else ", " + fact

        if len(current_line) + len(addition) > width and current_line:
            lines.append(current_line + ",")
            current_line = "   " + fact
        else:
            current_line += addition

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)


def display_substitution(substitutions):
    if not substitutions:
        return "{}"

    items = sorted(substitutions.items())

    return "{" + ", ".join(
        f"{key} = {substitute_term(value, substitutions)}"
        for key, value in items
    ) + "}"


# -------------------- FORWARD CHAINING --------------------

def forward_chaining(rules, kb, query):

    round_number = 1

    while True:

        print(f"\n{round_number}) {display_kb(kb)}\n")

        new_facts = []
        successful_applications = []

        current_kb = list(kb)

        for rule_number, (body, head) in enumerate(rules, start=1):

            substitutions_list = match_premises(body, current_kb)

            seen_substitutions = set()

            for substitutions in substitutions_list:

                sub_key = tuple(sorted(
                    (k, substitute_term(v, substitutions))
                    for k, v in substitutions.items()
                ))

                if sub_key in seen_substitutions:
                    continue

                seen_substitutions.add(sub_key)

                inferred = substitute_literal(head, substitutions)

                # Only ground conclusions are accepted
                if any(is_variable(arg) for arg in inferred[1]):
                    continue

                if inferred not in current_kb and inferred not in new_facts:

                    new_facts.append(inferred)

                    successful_applications.append(
                        (rule_number, body, substitutions, inferred)
                    )

        # Display successful applications only
        for rule_number, body, substitutions, inferred in successful_applications:

            original_head = rules[rule_number - 1][1]

            original_rule = (
                " & ".join(format_literal(literal) for literal in body)
                + " -> "
                + format_literal(original_head)
            )

            matched_premises = ", ".join(
                format_literal(substitute_literal(literal, substitutions))
                for literal in body
            )

            print(
                f"   R{rule_number}) {original_rule}, "
                f"{display_substitution(substitutions)}"
            )

            print(
                f"       {matched_premises} -> "
                f"{format_literal(inferred)}"
            )

            print()

        if not new_facts:
            print("   No new facts derived.")
            break

        kb.extend(new_facts)
        round_number += 1

    # -------------------- QUERY --------------------

    print("\n==========================================")
    print("QUERY RESULT:")
    print(f"Query: {format_literal(query)}")

    proved = any(
        unify_literals(query, fact, {}) is not None
        for fact in kb
    )

    print("PROVED" if proved else "NOT PROVED")
    print("==========================================")


# -------------------- INPUT --------------------

print("==========================================")
print("FORWARD CHAINING")
print("==========================================")

print("\nEnter rules (DONE to finish):")

rules = []
rule_number = 1

while True:
    line = input(f"R{rule_number}) ").strip()

    if line.upper() == "DONE":
        break

    if not line:
        continue

    try:
        rules.append(parse_rule(line))
        rule_number += 1

    except ValueError as error:
        print(f"Invalid rule: {error}")


print("\nEnter facts (DONE to finish):")

kb = []

while True:
    line = input().strip()

    if line.upper() == "DONE":
        break

    if not line:
        continue

    try:
        fact = parse_literal(line)

        if fact not in kb:
            kb.append(fact)

    except ValueError as error:
        print(f"Invalid fact: {error}")


print("\nEnter query:")

query = parse_literal(input().strip())

forward_chaining(rules, kb, query)
