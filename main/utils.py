import string


def validate_filename(filename: str) -> str:
    """
    Validates and sanitizes the given filename string to ensure it contains only valid characters.

    ---

    ## Params
        - `filename`: The filename to be validated.

    ## Returns
        - `str`: The validated filename string containing only valid characters.

    ## Demo
        >>> filename = "my/file:name.txt"
        >>> valid_filename = validate_filename(filename)
        >>> print(valid_filename)
        "myfilename.txt"
    """
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    filename = ''.join(c for c in filename if c in valid_chars)
    return filename
