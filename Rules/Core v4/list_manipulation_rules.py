# list_manipulation_rules.py

import re

def list_sorter(results_list):
    """
    Sorts a list of generated results using 'natural sorting' logic,
    by stripping HTML/XML tags before extracting the numerical prefix.
    """
    if not results_list:
        return []

    def strip_tags(text):
        """Removes all HTML/XML tags (<...>) and HTML entities (&...;) from a string."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove HTML entities (e.g., &nbsp;)
        text = re.sub(r'&[^;]+;', '', text)
        return text.strip()

    def get_sort_key(item):
        """
        Extracts the numerical prefix for sorting from the tag-stripped version.
        """
        # 1. Strip all HTML/XML tags first
        stripped_item = strip_tags(item)
        
        # 2. Match optional leading whitespace, then capture the number
        match = re.match(r'^\s*(\d+(\.\d*)?)', stripped_item) 
        
        if match:
            # Numerical key tuple: (0, numeric_value, original_string)
            try:
                num_value = float(match.group(1))
                # Primary key 0 ensures these items sort first.
                # Use the original, untripped item for the stable sort key (item).
                return (0, num_value, item)
            except ValueError:
                pass

        # String key tuple: (1, original_string)
        # Primary key 1 ensures these items sort last.
        return (1, stripped_item)

    # Apply the custom key and sort
    return sorted(results_list, key=get_sort_key)