def list_from_string(string, split_char=","):
    new_list = string.split(split_char)
    for h in new_list:
        h.strip()
    return new_list