def get_concept_explanation(concept):
    """
    Returns user-friendly explanation for a concept.
    """
    explanations = {
        "VARIABLE_NOT_DEFINED":
        "You are using a variable before creating it. In Python, variables must be assigned a value before use.",

        "LIST_INDEX_OUT_OF_RANGE":
        "You are trying to access an element outside the list's valid index range.",

        "TYPE_MISMATCH":
        "You are performing an operation on incompatible data types.",

        "SYNTAX_ERROR":
        "Your Python syntax is incorrect. Check brackets, colons, or indentation.",

        "UNKNOWN_ERROR":
        "An unexpected error occurred. Review your code logic."
    }
    return explanations.get(concept, "No specific explanation available.")
