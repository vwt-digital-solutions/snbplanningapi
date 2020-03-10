def remap_attributes(dictionary, attribute_map, reverse=False):
    """Map attributes from one key to another on the given dictionary.
    When reverse is True, a dictionary will be mapped back to the original.

    :rtype: a new dictionary
    """
    if reverse:
        attribute_map = {v: k for k, v in attribute_map.items()}

    new_dictionary = {attribute_map.get(k, k): v for (k, v) in dictionary.items()}

    return new_dictionary
