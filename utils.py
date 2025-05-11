import difflib

def find_best_match(search_text: str, corpus: str) -> str:
    """
    Find the best matching substring in the corpus for the given search text.
    
    Parameters:
    search_text (str): The text to search for
    corpus (str): The document to search in
    
    Returns:
    str: The best matching section of the corpus
    """
    # Split the corpus into lines to search
    lines = corpus.splitlines()
    
    if not lines:
        return ""
    
    if search_text in corpus:
        return search_text
    
    words = corpus.split()
    best_match = ""
    best_ratio = 0
    
    window_size = min(len(search_text.split()), len(words))
    if window_size == 0:
        return ""
        
    for i in range(len(words) - window_size + 1):
        window = " ".join(words[i:i + window_size])
        ratio = difflib.SequenceMatcher(None, search_text, window).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = window
    
    return best_match

def find_and_replace(find: str, replace: str, corpus: str) -> str:
    """
    Find the best matching substring in the corpus for the given search text and replace it with the new text.
    """
    best_match = find_best_match(find, corpus)
    return corpus.replace(best_match, replace)