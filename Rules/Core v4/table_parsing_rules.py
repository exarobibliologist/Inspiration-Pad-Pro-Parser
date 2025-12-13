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

# --- 2. CORE ENGINE: Single Roll Function ---

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

# --- 3. CORE ENGINE: Central Recursive Tag Resolver ---

def resolve_table_tags(text, tables, helpers, recursion_depth=0):
    """
    Recursively replaces tags, using functions from the 'helpers' dictionary.
    """
    
    # CRUCIAL: Set self-reference for recursion
    if 'resolve_table_tags' not in helpers: 
        helpers['resolve_table_tags'] = resolve_table_tags
        
    # Check for required helper functions by name
    if 'math_evaluator' not in helpers: return "[Fatal Error: Missing math_evaluator function]"
    if 'case_converter' not in helpers: return "[Fatal Error: Missing case_converter function]"
    if 'list_sorter' not in helpers: return "[Fatal Error: Missing list_sorter function]"

    math_evaluator_func = helpers['math_evaluator']
    case_converter_func = helpers['case_converter']
    list_sorter_func = helpers['list_sorter']

    if recursion_depth > 20: 
        return "[Error: Max recursion depth]" 
        
    while True:
        found_action = False
        
        # --- A. Handle Table Calls: [@Table] with modifiers ---
        table_match = re.search(r"\[@(.*?)\]", text)
        if table_match:
            full_tag = table_match.group(0) 
            content = table_match.group(1).strip()
            
            # --- MODIFIER INITIALIZATION ---
            case_modifier = None
            separator = ", "
            sort_flag = False 
            implode_applied = False
            
            # --- MODIFIER PARSING LOOP (Allows chaining in any order) ---
            while True:
                found_modifier = False

                # 1. Check for IMPLODE Clause
                implode_match = re.search(r'\s+>>\s+implode\s+"(.*?)"$', content, re.IGNORECASE)
                if implode_match and not implode_applied: 
                    separator = implode_match.group(1) 
                    content = content[:implode_match.start()].strip()
                    implode_applied = True
                    found_modifier = True
                    continue

                # 2. Check for SORT Modifier
                sort_match = re.search(r'\s+>>\s+sort$', content, re.IGNORECASE)
                if sort_match and sort_flag == False: 
                    sort_flag = True
                    content = content[:sort_match.start()].strip()
                    found_modifier = True
                    continue

                # 3. Check for Case Modifier
                case_match = re.search(r'\s+>>\s+(lower|upper|proper)$', content, re.IGNORECASE)
                if case_match and case_modifier is None: 
                    case_modifier = case_match.group(1).lower()
                    content = content[:case_match.start()].strip()
                    found_modifier = True
                    continue
                
                if not found_modifier:
                    break
            
            # --- END MODIFIER PARSING ---
            
            count = 1
            table_ref = content

            # Check for multi-roll count (Uses the math_evaluator)
            multi_roll_match_dice = re.match(r"^(\{.*?\})\s+(.*)", content)
            
            if multi_roll_match_dice:
                roll_expression = multi_roll_match_dice.group(1)
                table_ref = multi_roll_match_dice.group(2).strip()
                
                count_str = math_evaluator_func(roll_expression, tables, helpers) 
                
                try:
                    count = max(0, int(float(count_str))) 
                except ValueError:
                    count = 1 
                    table_ref = content
            else:
                match_multi_num = re.match(r"^(\d+)\s+(.*)", content)
                if match_multi_num:
                    count = int(match_multi_num.group(1))
                    table_ref = match_multi_num.group(2).strip()

            # Perform generation
            results = []
            if table_ref in tables:
                for _ in range(count):
                    raw_result = roll_on_table(table_ref, tables)
                    processed_result = resolve_table_tags(raw_result, tables, helpers, recursion_depth + 1)
                    results.append(processed_result)
                
                # Apply Sorting 
                if sort_flag:
                    results = list_sorter_func(results)
                    
                final_result = separator.join(results)
                
                # Apply Case Modification
                if case_modifier:
                    final_result = case_converter_func(final_result, case_modifier)
                
                text = text.replace(full_tag, final_result, 1)
                found_action = True
            else:
                text = text.replace(full_tag, f"[Error: Table '{table_ref}' not found]", 1)
                found_action = True
                
        # --- B. Handle In-line Picks: [|Option1|Option2|] (Robust Nested Fix) ---
        if "[|" in text and "|]" in text and not found_action:
            # Find the last (innermost) opening delimiter
            last_open = text.rfind('[|')
            
            # Search for the *matching* closing delimiter '|]' using a simple counter 
            # to handle arbitrary nesting. This prioritizes the innermost pick.
            
            open_count = 1 
            first_close_after_open = -1
            i = last_open + 2
            
            # Find the matching closing bracket |]
            while i < len(text):
                if text[i:i+2] == '[|':
                    open_count += 1
                    i += 2
                elif text[i:i+2] == '|]':
                    open_count -= 1
                    if open_count == 0:
                        first_close_after_open = i
                        break
                    i += 2
                else:
                    i += 1
            
            # If a matching closing delimiter was found, resolve the pick
            if first_close_after_open != -1:
                pick_content = text[last_open + 2: first_close_after_open]
                
                # Parse options, allowing for empty options (e.g., |||)
                options = pick_content.split('|')
                
                # Select a random option
                selected_option = random.choice(options) if options else ""

                # Replace the entire deck pick block with the selected option
                full_tag_start = last_open
                full_tag_end = first_close_after_open + 2
                
                text = text[:full_tag_start] + selected_option + text[full_tag_end:]
                found_action = True

        if not found_action: 
            break
            
    # --- C. Final Expression Evaluation (Math/Dice/Range) ---
    text = math_evaluator_func(text, tables, helpers)
    return text