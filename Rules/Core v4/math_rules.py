import random
import re
import math
from statistics import mean 

# --- Internal Helper for Dice and Range ---

def _resolve_dice(text):
    """
    Handles standard dice ({XdY}) and range ({Min--Max}) expressions.
    """
    # Dice pattern: {XdY[+|-|*|/|Z]}
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
    Resolves general arithmetic expressions.
    """
    arithmetic_pattern = r"\{(.*?)\}"

    def replace_arithmetic_match(match):
        expression = match.group(1).strip()
        
        if re.match(r'^[\d\s\.\+\-\*/\(\)]+$', expression.replace('//', '').replace('--', '')):
            try:
                result = eval(expression, {"__builtins__": None}, {})
                if result == int(result):
                    return str(int(result))
                return f"{result:.8f}".rstrip('0').rstrip('.')
            except Exception:
                return match.group(0) 
        return match.group(0)

    return re.sub(arithmetic_pattern, replace_arithmetic_match, text)


def _resolve_simple_math_only(text):
    text = _resolve_dice(text)
    text = _resolve_arithmetic(text)
    return text


# --- Public Function for Math Evaluation ---

def math_evaluator(text, tables, helpers):
    """
    Evaluates math, dice, and variable assignment/recall.
    """
    resolve_tags_func = helpers.get('resolve_table_tags')
    variables = helpers.get('variables', {})

    # --- A. Resolve Variable Assignments and Recalls ---
    while True:
        found_var_action = False

        # 1. Assignment: {$var = "val"} OR {$var = 'val'}
        # Regex explanation:
        # (["\']) matches either " or '
        # (.*?) matches the content inside
        # \2 matches whatever quote was captured in group 2 (ensures matching quotes)
        assign_match = re.search(r'\{\$(\w+)\s*=\s*(["\'])(.*?)\2\}', text)
        
        if assign_match:
            full_tag = assign_match.group(0)
            var_name = assign_match.group(1)
            raw_value_exp = assign_match.group(3)
            
            resolved_value = _resolve_simple_math_only(raw_value_exp)
            
            try:
                float(resolved_value) 
                variables[var_name] = resolved_value
                text = text.replace(full_tag, resolved_value, 1)
                found_var_action = True
                continue
            except ValueError:
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
                text = text.replace(full_tag, str(variables[var_name]), 1)
            else:
                text = text.replace(full_tag, f"[Error: Variable '{var_name}' not defined]", 1)
            
            found_var_action = True
            continue
            
        if not found_var_action:
            break

    if not resolve_tags_func:
        return _resolve_simple_math_only(text)

    FUNCTIONS = ["max", "min", "avg", "sqrt", "abs", "round", "floor", "ceil", "sign"]
    math_pattern = r"\{(" + "|".join(FUNCTIONS) + r")\s*\((.*?)\)\}"

    def replace_math_match(match):
        func_name = match.group(1).lower()
        contents = match.group(2).strip()
        
        resolved_contents = resolve_tags_func(contents, tables, helpers)
        if resolved_contents.startswith("[Error"): return resolved_contents

        # Recursive check for nested functions
        unbraced_pattern = r"^(" + "|".join(FUNCTIONS) + r")\s*\((.*)\)$"
        while re.match(unbraced_pattern, resolved_contents, re.IGNORECASE):
            rebraced = "{" + resolved_contents + "}"
            new_res = resolve_tags_func(rebraced, tables, helpers)
            if new_res.startswith("[Error"): 
                resolved_contents = new_res
                break
            if new_res.startswith('{') and new_res.endswith('}'):
                 new_res = new_res[1:-1]
            if new_res == resolved_contents: break
            resolved_contents = new_res

        numbers = []
        try:
            if func_name in ["sqrt", "abs", "round", "floor", "ceil", "sign"]:
                numbers = [float(resolved_contents)]
            else:
                numbers = [float(n.strip()) for n in resolved_contents.split(',') if n.strip()]
        except ValueError:
            return f"[Math Error: Invalid number in {func_name}: {resolved_contents}]"
        
        if not numbers: return f"[Math Error: No numbers for {func_name}]"
             
        try:
            n = numbers[0]
            if func_name == "max": result = max(numbers)
            elif func_name == "min": result = min(numbers)
            elif func_name == "avg": result = sum(numbers) / len(numbers)
            elif func_name == "sqrt": result = math.sqrt(n)
            elif func_name == "abs": result = abs(n)
            elif func_name == "round": result = round(n)
            elif func_name == "floor": result = math.floor(n)
            elif func_name == "ceil": result = math.ceil(n)
            elif func_name == "sign": result = 1 if n > 0 else (-1 if n < 0 else 0)
            else: return f"[Math Error: Unknown function {func_name}]"

            if result == int(result): return str(int(result))
            return f"{result:.8f}".rstrip('0').rstrip('.')
            
        except Exception as e:
            return f"[Math Execution Error: {e}]"

    while re.search(math_pattern, text, re.IGNORECASE):
        text = re.sub(math_pattern, replace_math_match, text, flags=re.IGNORECASE)
        
    text = _resolve_simple_math_only(text)
    return text