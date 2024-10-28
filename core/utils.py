import hashlib


def flatten_list(nested_list):
    """
    Recursively flattens a nested list, returning a single-level list containing all elements.

    Args:
        nested_list (list): A list that may contain nested lists at various depths.

    Returns:
        list: A flat list containing all elements from the nested structure in a single level.
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


def generate_sha256_hash(input_string):
    """
    Generates a SHA-256 hash for a given input string.

    Args:
        input_string (str): The input string to be hashed.

    Returns:
        str: The SHA-256 hash of the input string, represented as a hexadecimal string.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(str(input_string).encode("utf-8"))
    return sha256_hash.hexdigest()
