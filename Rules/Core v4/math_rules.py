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

# --- Public Function for Math Evaluation ---

def math_evaluator(text, tables, helpers):
    """
    Evaluates advanced math expressions, including nested table rolls,
    general arithmetic, and then resolves standard dice/range rolls.
    """
    resolve_tags_func = helpers.get('resolve_table_tags')
    
    if not resolve_tags_func:
        return _resolve_dice(text)

    FUNCTIONS = ["max", "min", "avg", "sqrt", "abs", "round", "floor", "ceil", "sign"]
    
    # Regex to capture the entire function call: {func(contents)}
    math_pattern = r"\{(" + "|".join(FUNCTIONS) + r")\s*\((.*?)\)\}"

    # --- Inner Replacement Function for Complex Math ---
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
            return f"{result:.8f}"
            
        except Exception as e:
            return f"[Math Execution Error: {e}]"

    # 1. Loop until no complex math functions are left in the text.
    while re.search(math_pattern, text, re.IGNORECASE):
        text = re.sub(math_pattern, replace_math_match, text, flags=re.IGNORECASE)
        
    # 2. Resolve Simple Expressions, Dice, and Ranges (Uses the new {min--max} syntax)
    text = _resolve_dice(text)

    # 3. Resolve General Arithmetic Expressions (e.g., {42+69} or {100-25})
    arithmetic_pattern = r"\{(.*?)\}"

    def replace_arithmetic_match(match):
        expression = match.group(1).strip()
        
        # Sanity check: ensure expression looks like math and doesn't contain the old floor division symbol.
        if re.match(r'^[\d\s\.\+\-\*/\(\)]+$', expression.replace('//', '').replace('--', '')):
            try:
                # Safely evaluate the arithmetic expression
                # Note: Python's standard division (/) results in a float.
                result = eval(expression, {"__builtins__": None}, {})
                
                if result == int(result):
                    return str(int(result))
                return f"{result:.8f}"
                
            except Exception:
                return match.group(0) 
                
        return match.group(0)

    text = re.sub(arithmetic_pattern, replace_arithmetic_match, text)

    return text