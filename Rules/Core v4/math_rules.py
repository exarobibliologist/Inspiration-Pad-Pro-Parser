import random
import re
import math
from statistics import mean 

# --- Internal Helper for Dice and Range ---

def _resolve_dice(text):
    """
    Handles standard dice ({XdY}) and range ({Min--Max}) expressions.
    """
    # Dice pattern: {XdY[+|-|*|/|Z]} - NOTE: '//' has been removed
    dice_pattern = r"\{(\d+)d(\d+)(?:([\+\-\*]|\/)\s*(\d+))?\}" 
    
    def replace_dice_match(match):
        count = int(match.group(1))
        sides = int(match.group(2))
        operator = match.group(3)
        value_str = match.group(4)
        
        total = sum(random.randint(1, sides) for _ in range(count)) 
        
        if operator and value_str:
            try:
                value = int(value_str)
            except ValueError: return "[Err]"
            
            if operator == '+': total += value
            elif operator == '-': total -= value
            elif operator == '*': total *= value
            # The standard division operator '/' now produces a float result if used
            elif operator == '/': 
                return f"{(float(total) / value):.2f}" if value != 0 else "[Err: DivByZero]"
        
        return str(total)
    
    text = re.sub(dice_pattern, replace_dice_match, text)
    
    # Random Range pattern: {Min--Max}
    range_pattern = r"\{(\d+)--(\d+)\}"
    def replace_range_match(match):
        mn = int(match.group(1))
        mx = int(match.group(2))
        if mn > mx:
            mn, mx = mx, mn
        return str(random.randint(mn, mx))
        
    text = re.sub(range_pattern, replace_range_match, text)
    return text

def _resolve_arithmetic(text):
    """
    Resolves general arithmetic expressions (e.g., {42+69} or {100-25}).
    """
    arithmetic_pattern = r"\{(.*?)\}"

    def replace_arithmetic_match(match):
        expression = match.group(1).strip()
        
        # Sanity check: ensure expression looks like math 
        if re.match(r'^[\d\s\.\+\-\*/\(\)]+$', expression.replace('//', '').replace('--', '')):
            try:
                # Safely evaluate the arithmetic expression
                result = eval(expression, {"__builtins__": None}, {})
                
                if result == int(result):
                    return str(int(result))
                # Max 8 decimal places for float results, strip trailing zeros/dot
                return f"{result:.8f}".rstrip('0').rstrip('.')
                
            except Exception:
                return match.group(0) 
                
        return match.group(0)

    return re.sub(arithmetic_pattern, replace_arithmetic_match, text)


def _resolve_simple_math_only(text):
    """
    Performs the final resolution steps: Dice/Range, then simple Arithmetic.
    """
    text = _resolve_dice(text)
    text = _resolve_arithmetic(text)
    return text


# --- Public Function for Math Evaluation (Updated) ---

def math_evaluator(text, tables, helpers):
    """
    Evaluates advanced math expressions, including nested table rolls,
    general arithmetic, and resolves variable assignment/recall.
    """
    resolve_tags_func = helpers.get('resolve_table_tags')
    
    # 0. Get or initialize variables storage (set in run_generation)
    variables = helpers.get('variables', {})

    # --- A. Resolve Variable Assignments and Recalls (Loop until stable) ---
    while True:
        found_var_action = False

        # 1. Assignment: {$var_name = "value or dice expression"}
        assign_match = re.search(r'\{\$(\w+)\s*=\s*"(.*?)"\}', text)
        if assign_match:
            full_tag = assign_match.group(0)
            var_name = assign_match.group(1)
            raw_value_exp = assign_match.group(2)
            
            # Resolve the expression using simple math resolution (Dice/Arithmetic)
            resolved_value = _resolve_simple_math_only(raw_value_exp)
            
            # Try to store as a number for later math operations
            try:
                # Convert the resolved string back to a float/int
                number_value = float(resolved_value) 
                
                # Store the string representation (which is cleaner for output)
                variables[var_name] = resolved_value
                
                # Replace the tag with the resolved value (as requested for immediate output)
                text = text.replace(full_tag, resolved_value, 1)
                found_var_action = True
                continue
            except ValueError:
                # If it's not a number (e.g., "[Err]"), store the error string.
                variables[var_name] = resolved_value
                text = text.replace(full_tag, resolved_value, 1)
                found_var_action = True
                continue

        # 2. Recall: {$var_name}
        recall_match = re.search(r'\{\$(\w+)\}', text)
        if recall_match:
            full_tag = recall_match.group(0)
            var_name = recall_match.group(1)
            
            if var_name in variables:
                text = text.replace(full_tag, variables[var_name], 1)
            else:
                text = text.replace(full_tag, f"[Error: Variable '{var_name}' not defined]", 1)
            
            found_var_action = True
            continue
            
        if not found_var_action:
            break

    # If the recursive tag resolver is missing (shouldn't happen in a full IPP run)
    if not resolve_tags_func:
        return _resolve_dice_and_arithmetic(text)


    FUNCTIONS = ["max", "min", "avg", "sqrt", "abs", "round", "floor", "ceil", "sign"]
    
    # Regex to capture the entire function call: {func(contents)}
    math_pattern = r"\{(" + "|".join(FUNCTIONS) + r")\s*\((.*?)\)\}"

    # --- B. Resolve Complex Math Functions ---
    def replace_math_match(match):
        func_name = match.group(1).lower()
        contents = match.group(2).strip()
        
        # A. FIRST PASS: Resolve any nested tags or simple dice/range rolls.
        resolved_contents = resolve_tags_func(contents, tables, helpers)
        
        if resolved_contents.startswith("[Error"):
             return resolved_contents

        # B. RECURSIVE CHECK (For nested math functions like {round(sqrt(...))})
        unbraced_pattern = r"^(" + "|".join(FUNCTIONS) + r")\s*\((.*)\)$"
        
        while re.match(unbraced_pattern, resolved_contents, re.IGNORECASE):
            rebraced_expression = "{" + resolved_contents + "}"
            new_resolved_contents = resolve_tags_func(rebraced_expression, tables, helpers)
            
            if new_resolved_contents.startswith("[Error"): 
                resolved_contents = new_resolved_contents
                break
                
            if new_resolved_contents.startswith('{') and new_resolved_contents.endswith('}'):
                 new_resolved_contents = new_resolved_contents[1:-1]
                 
            if new_resolved_contents == resolved_contents:
                 break
            
            resolved_contents = new_resolved_contents


        # C. Parse the resolved contents into a list of numbers
        numbers = []
        try:
            if func_name in ["sqrt", "abs", "round", "floor", "ceil", "sign"]:
                numbers = [float(resolved_contents)]
            else:
                numbers = [float(n.strip()) for n in resolved_contents.split(',') if n.strip()]
        except ValueError:
            return f"[Math Error: Invalid number in {func_name} contents: {resolved_contents}]"
        
        if not numbers:
             return f"[Math Error: No numbers found for {func_name}]"
             
        # D. Apply the function
        try:
            n = numbers[0]

            if func_name == "max":
                result = max(numbers)
            elif func_name == "min":
                result = min(numbers)
            elif func_name == "avg":
                result = sum(numbers) / len(numbers)
            elif func_name == "sqrt":
                result = math.sqrt(n)
            elif func_name == "abs":
                result = abs(n)
            elif func_name == "round":
                result = round(n)
            elif func_name == "floor":
                result = math.floor(n)
            elif func_name == "ceil":
                result = math.ceil(n)
            elif func_name == "sign":
                result = 1 if n > 0 else (-1 if n < 0 else 0)
            else:
                return f"[Math Error: Unknown function {func_name}]"

            if result == int(result):
                return str(int(result))
            return f"{result:.8f}".rstrip('0').rstrip('.')
            
        except Exception as e:
            return f"[Math Execution Error: {e}]"

    # 1. Loop until no complex math functions are left in the text.
    while re.search(math_pattern, text, re.IGNORECASE):
        text = re.sub(math_pattern, replace_math_match, text, flags=re.IGNORECASE)
        
    # 2. Resolve final simple math (Dice/Range and Arithmetic)
    text = _resolve_simple_math_only(text)

    return text