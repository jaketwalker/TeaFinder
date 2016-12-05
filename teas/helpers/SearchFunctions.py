def parse_search_text(search_text):
    """
        Parses search criteria into individual words.
        Note this currently only supports single-word criteria separated by spaces.
    """
    return search_text.split(" ")