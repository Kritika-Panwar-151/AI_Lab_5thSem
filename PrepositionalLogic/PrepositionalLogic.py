
import re
from itertools import product


# ---------- PARSER ----------

class Parser:
    def __init__(self, text):
        pattern = (
            r'<->|<=>|->|=>|'
            r'[()~!&^|]|'
            r'\b(?:and|or|not|v)\b|'
            r'[A-Za-z][A-Za-z0-9_]*'
        )

        self.tokens = re.findall(pattern, text)

        # Reject invalid characters
        remaining = re.sub(pattern, '', text)
        if remaining.strip():
            raise ValueError(f"Invalid character(s): {remaining}")

        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, expected=None):
        token = self.peek()

        if token is None:
            raise ValueError("Unexpected end of expression")

        if expected is not None and token != expected:
            raise ValueError(f"Expected '{expected}'")

        self.pos += 1
        return token

    def parse(self):
        if not self.tokens:
            raise ValueError("Empty expression")

        node = self.parse_iff()

        if self.peek() is not None:
            raise ValueError(f"Unexpected token: {self.peek()}")

        return node

    def parse_iff(self):
        node = self.parse_implies()

        while self.peek() in ("<->", "<=>"):
            self.eat()
            node = ("iff", node, self.parse_implies())

        return node

    def parse_implies(self):
        node = self.parse_or()

        if self.peek() in ("->", "=>"):
            self.eat()
            node = ("implies", node, self.parse_implies())

        return node

    def parse_or(self):
        node = self.parse_and()

        while self.peek() in ("|", "v", "or"):
            self.eat()
            node = ("or", node, self.parse_and())

        return node

    def parse_and(self):
        node = self.parse_not()

        while self.peek() in ("&", "^", "and"):
            self.eat()
            node = ("and", node, self.parse_not())

        return node

    def parse_not(self):
        if self.peek() in ("~", "!", "not"):
            self.eat()
            return ("not", self.parse_not())

        return self.parse_atom()

    def parse_atom(self):
        token = self.peek()

        if token == "(":
            self.eat("(")
            node = self.parse_iff()
            self.eat(")")
            return node

        if token is None:
            raise ValueError("Missing proposition")

        if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', token):
            self.eat()
            return ("var", token)

        raise ValueError(f"Unexpected token: {token}")


# ---------- GET PROPOSITIONS ----------

def get_symbols(node):
    if node[0] == "var":
        return {node[1]}

    if node[0] == "not":
        return get_symbols(node[1])

    return get_symbols(node[1]) | get_symbols(node[2])


# ---------- EVALUATE ----------

def evaluate(node, model):
    op = node[0]

    if op == "var":
        return model[node[1]]

    if op == "not":
        return not evaluate(node[1], model)

    left = evaluate(node[1], model)
    right = evaluate(node[2], model)

    if op == "and":
        return left and right

    if op == "or":
        return left or right

    if op == "implies":
        return (not left) or right

    if op == "iff":
        return left == right


# ---------- MAIN PROGRAM ----------

def main():

    print("PROPOSITIONAL LOGIC KB CHECKER")
    print("Operators: ~ NOT, & or ^ AND, | OR, -> IMPLIES, <-> IFF")

    # Input KB
    kb_input = input(
        "\nEnter KB sentences separated by commas:\n"
    )

    sentences = [
        s.strip() for s in kb_input.split(",") if s.strip()
    ]

    if not sentences:
        print("Knowledge Base cannot be empty.")
        return

    try:
        kb = [Parser(sentence).parse() for sentence in sentences]

    except ValueError as e:
        print("Invalid KB:", e)
        return

    # Get propositions
    symbols = sorted(
        set().union(*(get_symbols(s) for s in kb))
    )

    # ---------- TRUTH TABLE ----------

    print("\nTRUTH TABLE\n")

    headers = symbols + sentences + ["KB"]

    print(" | ".join(headers))
    print("-" * len(" | ".join(headers)))

    table_rows = []

    for values in product([False, True], repeat=len(symbols)):

        model = dict(zip(symbols, values))

        sentence_values = [
            evaluate(sentence, model)
            for sentence in kb
        ]

        kb_value = all(sentence_values)

        table_rows.append((model, sentence_values, kb_value))

        row = (
            [model[s] for s in symbols]
            + sentence_values
            + [kb_value]
        )

        print(" | ".join(
            "T" if value else "F"
            for value in row
        ))

    # ---------- QUERY LOOP ----------

    while True:

        query_input = input(
            "\nEnter query (or n to stop): "
        ).strip()

        if query_input.lower() == "n":
            print("Program terminated.")
            break

        try:
            query = Parser(query_input).parse()

        except ValueError as e:
            print("Invalid query:", e)
            continue

        # Include query propositions too
        all_symbols = sorted(
            set(symbols) | get_symbols(query)
        )

        counterexample = None
        counterexample_row = None

        # Check all possible models
        for row_number, values in enumerate(
            product([False, True], repeat=len(all_symbols)),
            start=1
        ):

            model = dict(zip(all_symbols, values))

            kb_true = all(
                evaluate(sentence, model)
                for sentence in kb
            )

            query_true = evaluate(query, model)

            # KB true but query false
            if kb_true and not query_true:

                counterexample = model
                counterexample_row = row_number
                break

        # ---------- RESULT ----------

        if counterexample is None:

            print(f"\nYES, KB entails {query_input}.")

            print(
                "Reason: The query is true in every model\n"
                "where KB is true."
            )

        else:

            print(f"\nNO, KB does not entail {query_input}.")

            print(
                f"\nReason: In row {counterexample_row}, "
                "KB is true but the query is false."
            )

            print("\nCounterexample:")

            for symbol in all_symbols:
                value = counterexample[symbol]
                print(f"{symbol} = {'T' if value else 'F'}")


# ---------- RUN ----------

if __name__ == "__main__":
    main()
