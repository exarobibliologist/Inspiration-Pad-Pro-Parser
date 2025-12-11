def case_converter(text, modifier):
    """
    Applies case conversion based on the modifier string (lower, upper, proper).
    This function is called by the core tag resolver.
    """
    modifier = modifier.lower()
    
    if modifier == "lower":
        return text.lower()
    elif modifier == "upper":
        return text.upper()
    elif modifier == "proper":
        return text.title() 
    
    return text