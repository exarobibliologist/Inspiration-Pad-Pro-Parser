import random
import re

# --- 1. CORE ENGINE: Table Definition Parsing ---

def parse_tables(script_content):
    """Parses the script content to extract tables."""
    tables = {}
    current_table_name = None
    lines = script_content.splitlines()
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if line.lower().startswith("table:"):
            parts = line.split(":", 1)
            if len(parts) > 1:
                current_table_name = parts[1].strip()
                tables[current_table_name] = []
            continue
            
        if current_table_name:
            weight = 1
            text_content = line
            
            if ":" in line:
                parts = line.split(":", 1)
                potential_weight = parts[0].strip()
                if potential_weight.isdigit():
                    weight = int(potential_weight)
                    text_content = parts[1].strip()
                    
            tables[current_table_name].append({"text": text_content, "weight": weight})
            
    return tables

# --- 2. CORE ENGINE: Logic Helper ---

def evaluate_custom_condition(condition_str):
    """
    Evaluates comparison logic for the [if] and [ifnot] tags.
    Supported Operators: > (GT), < (LT), = (EQ), =/= (NEQ)
    """
    # Check for the multi-character operator first to avoid partial matching with '='
    if "=/=" in condition_str:
        parts = condition_str.split("=/=")
        op = "!="
    elif "=" in condition_str:
        parts = condition_str.split("=")
        op = "=="
    elif ">" in condition_str:
        parts = condition_str.split(">")
        op = ">"
    elif "<" in condition_str:
        parts = condition_str.split("<")
        op = "<"
    else:
        return False

    if len(parts) != 2:
        return False
    
    val1_raw = parts[0].strip()
    val2_raw = parts[1].strip()

    # Attempt numeric comparison
    try:
        v1 = float(val1_raw)
        v2 = float(val2_raw)
        if op == "==": return v1 == v2
        if op == "!=": return v1 != v2
        if op == ">": return v1 > v2
        if op == "<": return v1 < v2
    except ValueError:
        # Fallback to string comparison
        if op == "==": return val1_raw == val2_raw
        if op == "!=": return val1_raw != val2_raw
        if op == ">": return val1_raw > val2_raw
        if op == "<": return val1_raw < val2_raw
        
    return False

# --- 3. CORE ENGINE: Single Roll Function ---

def roll_on_table(table_name, tables):
    """Rolls a single time on the specified table, respecting weights."""
    if table_name not in tables: 
        return f"[Error: Table '{table_name}' not found]"
        
    entries = tables[table_name]
    if not entries: 
        return "[Error: Table is empty]"
        
    population = [e['text'] for e in entries]
    weights = [e['weight'] for e in entries]
    
    return random.choices(population, weights=weights, k=1)[0]

# --- 4. CORE ENGINE: Central Recursive Tag Resolver ---

def resolve_table_tags(text, tables, helpers, recursion_depth=0):
    """
    Recursively replaces tags. Prioritizes variables/math so logic gates
    can evaluate numeric results.
    """
    if 'resolve_table_tags' not in helpers: 
        helpers['resolve_table_tags'] = resolve_table_tags
        
    math_evaluator_func = helpers.get('math_evaluator')
    case_converter_func = helpers.get('case_converter')
    list_sorter_func = helpers.get('list_sorter')

    if recursion_depth > 25: 
        return "[Error: Max recursion depth]" 
        
    while True:
        original_text = text
        
        # --- STEP 1: RESOLVE MATH/VARIABLES ---
        # Run first so tags like {$val} are numbers before logic gates see them.
        text = math_evaluator_func(text, tables, helpers)
        
        found_action = False
        
        # --- STEP 2: IF/IFNOT LOGIC ---
        # [if "condition", "then", "else"]
        if_pattern = r'\[if\s+"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\]'
        if_match = re.search(if_pattern, text, re.IGNORECASE)
        if if_match and not found_action:
            full_tag = if_match.group(0)
            condition_str = if_match.group(1)
            then_branch = if_match.group(2)
            else_branch = if_match.group(3)
            
            if evaluate_custom_condition(condition_str):
                text = text.replace(full_tag, then_branch, 1)
            else:
                text = text.replace(full_tag, else_branch, 1)
            
            found_action = True
            continue

        # [ifnot "condition", "then", "else"]
        ifnot_pattern = r'\[ifnot\s+"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\]'
        ifnot_match = re.search(ifnot_pattern, text, re.IGNORECASE)
        if ifnot_match and not found_action:
            full_tag = ifnot_match.group(0)
            condition_str = ifnot_match.group(1)
            then_branch = ifnot_match.group(2)
            else_branch = ifnot_match.group(3)
            
            # Logic is inverted: if condition is FALSE, do 'then'
            if not evaluate_custom_condition(condition_str):
                text = text.replace(full_tag, then_branch, 1)
            else:
                text = text.replace(full_tag, else_branch, 1)
            
            found_action = True
            continue

        # --- STEP 3: HANDLE TABLE CALLS: [@Table] ---
        table_match = re.search(r"\[@(.*?)\]", text)
        if table_match and not found_action:
            full_tag = table_match.group(0) 
            content = table_match.group(1).strip()
            
            # Modifier Parsing
            case_modifier = None
            separator = ", "
            sort_flag = False 
            implode_applied = False
            
            while True:
                found_modifier = False
                implode_match = re.search(r'\s+>>\s+implode\s+"(.*?)"$', content, re.IGNORECASE)
                if implode_match and not implode_applied: 
                    separator = implode_match.group(1); content = content[:implode_match.start()].strip()
                    implode_applied = True; found_modifier = True; continue
                sort_match = re.search(r'\s+>>\s+sort$', content, re.IGNORECASE)
                if sort_match and not sort_flag: 
                    sort_flag = True; content = content[:sort_match.start()].strip()
                    found_modifier = True; continue
                case_match = re.search(r'\s+>>\s+(lower|upper|proper)$', content, re.IGNORECASE)
                if case_match and case_modifier is None: 
                    case_modifier = case_match.group(1).lower(); content = content[:case_match.start()].strip()
                    found_modifier = True; continue
                if not found_modifier: break

            # Multi-roll parsing
            count = 1
            table_ref = content
            match_multi_num = re.match(r"^(\d+)\s+(.*)", content)
            if match_multi_num:
                count = int(match_multi_num.group(1))
                table_ref = match_multi_num.group(2).strip()
            
            if table_ref in tables:
                results = []
                for _ in range(count):
                    raw_res = roll_on_table(table_ref, tables)
                    results.append(resolve_table_tags(raw_res, tables, helpers, recursion_depth + 1))
                
                if sort_flag: results = list_sorter_func(results)
                final_result = separator.join(results)
                if case_modifier: final_result = case_converter_func(final_result, case_modifier)
                text = text.replace(full_tag, final_result, 1)
                found_action = True
            else:
                text = text.replace(full_tag, f"[Error: Table '{table_ref}' not found]", 1)
                found_action = True

        # --- STEP 4: HANDLE IN-LINE PICKS [|A|B|] ---
        if "[|" in text and "|]" in text and not found_action:
            last_open = text.rfind('[|')
            open_count = 1; first_close = -1; i = last_open + 2
            while i < len(text):
                if text[i:i+2] == '[|': open_count += 1; i += 2
                elif text[i:i+2] == '||': # This seems to be a placeholder from your original logic
                    i += 2
                elif text[i:i+2] == '|]':
                    open_count -= 1
                    if open_count == 0: first_close = i; break
                    i += 2
                else: i += 1
            
            if first_close != -1:
                options = text[last_open + 2: first_close].split('|')
                selected = random.choice(options) if options else ""
                text = text[:last_open] + selected + text[first_close+2:]
                found_action = True

        if original_text == text and not found_action:
            break
            
    return text