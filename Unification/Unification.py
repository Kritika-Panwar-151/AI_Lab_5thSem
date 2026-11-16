import re

def parse_input(expr_str):
    """
    Parses a string expression like 'F(G(x), H(y))' into nested list structures.
    e.g., 'F(G(x), H(y))' -> ['F', ['G', 'x'], ['H', 'y']]
    """
    expr_str = expr_str.replace(" ", "")  # Strip whitespace
    if '(' not in expr_str:
        return expr_str
    
    # Match the outermost function name and its argument string context
    match = re.match(r"^([^\(]+)\((.*)\)$", expr_str)
    if not match:
        return expr_str
    
    name = match.group(1)
    args_str = match.group(2)
    
    args = []
    current_arg = []
    paren_depth = 0
    
    # Safely split arguments by commas, ignoring commas nested inside inner parentheses
    for char in args_str:
        if char == ',' and paren_depth == 0:
            args.append(parse_input("".join(current_arg)))
            current_arg = []
        else:
            if char == '(': paren_depth += 1
            if char == ')': paren_depth -= 1
            current_arg.append(char)
            
    if current_arg:
        args.append(parse_input("".join(current_arg)))
        
    return [name] + args

def is_variable(x):
    """Variables start with a lowercase letter."""
    return isinstance(x, str) and len(x) > 0 and x[0].islower()

def occurs_in(var, expr):
    """Checks if variable 'var' occurs inside expression 'expr' (Occur Check)."""
    if var == expr:
        return True
    if isinstance(expr, list):
        return any(occurs_in(var, arg) for arg in expr[1:])
    return False

def apply_substitution(theta, expr):
    """Applies the current substitution dictionary rules to an expression."""
    if is_variable(expr):
        return theta.get(expr, expr)
    if isinstance(expr, list):
        return [expr[0]] + [apply_substitution(theta, arg) for arg in expr[1:]]
    return expr

def format_theta(theta):
    """Formats theta dictionary to standard logic output notation."""
    if not theta:
        return "theta={}"
    return "theta={ " + ", ".join([f"{k}/{format_expr(v)}" for k, v in theta.items()]) + " }"

def format_expr(expr):
    """Formats internal lists back into standard predicate notation strings."""
    if isinstance(expr, list):
        return f"{expr[0]}({', '.join([format_expr(arg) for arg in expr[1:]])})"
    return str(expr)

def unify(psi1, psi2, theta, trace_steps, original_expr1, original_expr2):
    """
    Recursively unifies sub-terms and updates the central substitution dictionary (theta).
    Tracks intermediate state prints directly to the trace list.
    """
    # Apply latest substitutions to current working terms
    psi1 = apply_substitution(theta, psi1)
    psi2 = apply_substitution(theta, psi2)

    if psi1 == psi2:
        return True

    # Case 1: First item is a variable
    if is_variable(psi1):
        if occurs_in(psi1, psi2):
            return False
        new_rule = {psi1: psi2}
        for k, v in theta.items():
            theta[k] = apply_substitution(new_rule, v)
        theta[psi1] = psi2
        
        # Log the state change
        step_num = len(trace_steps) + 1
        curr1 = apply_substitution(theta, original_expr1)
        curr2 = apply_substitution(theta, original_expr2)
        trace_steps.append((f"S{step_num}={{{format_expr(curr1)}, {format_expr(curr2)}}}", format_theta(theta.copy())))
        return True

    # Case 2: Second item is a variable
    if is_variable(psi2):
        if occurs_in(psi2, psi1):
            return False
        new_rule = {psi2: psi1}
        for k, v in theta.items():
            theta[k] = apply_substitution(new_rule, v)
        theta[psi2] = psi1
        
        # Log the state change
        step_num = len(trace_steps) + 1
        curr1 = apply_substitution(theta, original_expr1)
        curr2 = apply_substitution(theta, original_expr2)
        trace_steps.append((f"S{step_num}={{{format_expr(curr1)}, {format_expr(curr2)}}}", format_theta(theta.copy())))
        return True

    # Case 3: Both are compound functional structures
    if isinstance(psi1, list) and isinstance(psi2, list):
        if psi1[0] != psi2[0] or len(psi1) != len(psi2):
            return False
        
        # Recursively unify components/arguments step-by-step
        for i in range(1, len(psi1)):
            if not unify(psi1[i], psi2[i], theta, trace_steps, original_expr1, original_expr2):
                return False
        return True

    return False

def run_unification_trace(expr1, expr2):
    print(f"\ninput 1: {format_expr(expr1)}")
    print(f"input 2: {format_expr(expr2)}")
    
    theta = {}
    trace_steps = []
    
    # S0 Initial State Setup
    print(f"S0={{{format_expr(expr1)}, {format_expr(expr2)}}}")
    print(format_theta(theta))
    
    # Run structural check and execute recursive algorithm
    if not isinstance(expr1, list) or not isinstance(expr2, list) or expr1[0] != expr2[0] or len(expr1) != len(expr2):
        print("FAILURE")
        return

    success = unify(expr1, expr2, theta, trace_steps, expr1, expr2)
    
    # Print out step sequence logs
    for s_label, t_label in trace_steps:
        print(s_label)
        print(t_label)
        
    if success:
        print("SUCCESS")
    else:
        print("FAILURE")

# --- Interactive Entry ---
if __name__ == "__main__":
    print("--- First-Order Logic Unification (Nested Functions Supported) ---")
    
    raw_input1 = input("Enter Input 1 (e.g., F(G(x),H(y))): ")
    raw_input2 = input("Enter Input 2 (e.g., F(z,H(Apple))): ")
    
    parsed_f1 = parse_input(raw_input1)
    parsed_f2 = parse_input(raw_input2)
    
    run_unification_trace(parsed_f1, parsed_f2)
