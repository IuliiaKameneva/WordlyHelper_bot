import numpy as np
import math


# create a file with 5-lenth words from file with all russians nouns
def five_words_filter(filename='russian_nouns.txt', word_lenth=5, res_filename='wordly_nouns.txt'):
    """
    Creates a file with nouns of a fixed length from a file containing all nouns.
    
    Parameters:
    - filename (str): List of all nouns.
    - word_lenth (int): Length of words that needed for the game.
    - res_filename (str): Filename for nouns of a fixed length.

    Returns:
    - tuple (str, bool): The output file name and the success flag of the function.
    """
    try:
        with open(filename, 'r', encoding='utf8') as fr:
            with open(res_filename, 'w', encoding='utf8') as fw:
                all_words = fr.readlines()
                five_letter_words = [word.strip() for word in all_words if len(word.strip()) == word_lenth]
                for word in five_letter_words:
                    fw.write(word + "\n")
    except:
        return res_filename, 0
    return res_filename, 1


def load_words(filename='wordly_nouns.txt'):
    """
    Loads words from a file, processes them by stripping whitespace, replacing 'ё' with 'е', 
    and returns the words as a 2D numpy array where each word is represented as a list of characters.

    Args:
        filename (str): The name of the file to read the words from. Default is 'wordly_nouns.txt'.

    Returns:
        numpy.ndarray: A numpy array containing the words, each row is a separate word.

    """
    with open(filename, 'r', encoding='utf8') as fr:
        all_words = [word.strip().replace('ё', 'е') for word in fr.readlines()]
        array_words = np.array([list(word) for word in all_words])
        return array_words
    
    
def get_feedback(word, candidate):
    """
    Compares the given candidate word with the target word and generates feedback
    for each letter in the candidate word based on its match with the target word.

    The feedback is represented by the following colors:
        'G' - Correct letter in the correct position (green).
        'Y' - Correct letter in the wrong position (yellow).
        'B' - Incorrect letter (black).

    Args:
        word : The target word to compare against.
        candidate : The candidate word to check for feedback.

    Returns:
        str: A string containing feedback ('G', 'Y', 'B') for each character in the candidate word.
        
    Example:
        >>> get_feedback("apple", "apric")
        'GGBBB'
    """
    res = ''
    for i in range(len(word)):
        if word[i]==candidate[i]:
            res += 'G'
        elif word[i] in candidate:
            res += 'Y'
        else:
            res += 'B'
    return res

def word_fit(pword, best_word, feedback) -> bool:
    """
    Determines if a word (pword) fits the feedback constraints based on the best word.

    The function checks if the given word (pword) can be a valid guess according to the feedback
    generated from comparing the best word with previous guesses.

    Args:
        pword (list): The word to check if it fits the feedback.
        best_word (list): The target word against which feedback was generated.
        feedback (str): A string of feedback letters ('G', 'Y', 'B') corresponding to each letter in pword.

    Returns:
        bool: True if pword fits the feedback constraints for best_word, False otherwise.

    Example:
        >>> word_fit(["a","p","p","l","e"], ["a","p","r","i","c"], "GGYBB")
        False
        >>> word_fit(["a","p","p","l","e"], ["a","p","r","i","c"], "GGBBB")
        True
    """
    pword, best_word = copy.deepcopy(pword_original), copy.deepcopy(best_word_original)
    sort_ind = np.argsort(list(feedback.replace('G', '0').replace('Y', '1').replace('B', '2')))
    index_to_remove = 0
    for i in sort_ind:
        f = feedback[i]
        if (f=='G'):
            if (pword[i]!=best_word[i]):
                return False
            pword[i] = '*'
            best_word[i] = '*'
        if (f=='Y'):
            if ((best_word[i] not in [pword[x] for x in sort_ind]) or (pword[i]==best_word[i])):
                return False
            pword[np.where(pword == best_word[i])[0][0]] = '*'
            best_word[i] = '*'
        if (f=='B') and (best_word[i] in [pword[x] for x in sort_ind]):
                return False
    return True


def filter_words(possible_words, best_word, feedback) -> list:
    """
    Filters a list of possible words based on feedback constraints from the best word.

    Args:
        possible_words (list of lists): The list of candidate words to filter.
        best_word (list): The target word against which feedback was generated.
        feedback (str): The feedback string ('G', 'Y', 'B') indicating the correctness of each letter
                        in the candidate words compared to the best word.

    Returns:
        list of lists: A list of words from possible_words that fit the feedback constraints.

    Example:
        >>> filter_words([["a","p","p","l","e"], ["g","r","a","p","e"], ["p","l","a","n","e"]],  ["a","p","r","i","c"], "GGBBB")
        [['a', 'p', 'p', 'l', 'e']]
    """
    res_list = []
    for pword in possible_words:
        if word_fit(pword, best_word, feedback):
            res_list.append(pword)
    return res_list

# Функция для расчета энтропии
def calculate_entropy(word, possible_words) -> float:
    """
    Calculates the entropy of a given word based on the set of possible words.

    Args:
        word (list): The word for which to calculate the entropy.
        possible_words (list of lists): The list of possible words to compare the given word against.

    Returns:
        float: The entropy value of the given word, which represents the uncertainty of the feedback outcomes.
    """
    outcomes = {}
    for candidate in possible_words:
        outcome = get_feedback(word, candidate)  # GGYBB, etc.
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
    entropy = 0
    for count in outcomes.values():
        p = count / len(possible_words)
        entropy -= p * math.log2(p)
    return entropy


def checkFeedback(feedback):
    """
    Checks if the provided feedback string is valid.

    A valid feedback string must meet the following criteria:
    - It must have exactly 5 characters.
    - It must only contain the characters 'B', 'G', and 'Y', corresponding to black, green, and yellow feedback in a word game.

    Args:
        feedback (str): The feedback string to check.

    Returns:
        bool: True if the feedback is valid, False otherwise.
    """
    if (len(feedback)!=5) or (not(set(feedback) <= set('BGY'))):
        return False
    return True