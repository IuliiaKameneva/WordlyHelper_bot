import numpy as np
import math


# create a file with 5-lenth words from file with all russians nouns
def five_words_filter(filename='russian_nouns.txt', word_lenth=5, res_filename='wordly_nouns.txt'):
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
    with open(filename, 'r', encoding='utf8') as fr:
        all_words = [word.strip().replace('ё', 'е') for word in fr.readlines()]
        array_words = np.array([list(word) for word in all_words])
        return array_words
    
    
def get_feedback(word, candidate):
    res = ''
    for i in range(len(word)):
        if word[i]==candidate[i]:
            res += 'G'
        elif word[i] in candidate:
            res += 'Y'
        else:
            res += 'B'
    return res

def word_fit(pword, best_word, feedback):
    for i, f in enumerate(feedback):
        if (f=='G') and (pword[i]!=best_word[i]):
            return False
        if (f=='Y') and ((best_word[i] not in pword) or (pword[i]==best_word[i])):
            return False
        if (f=='B') and (best_word[i] in pword):
            return False
    return True

def filter_words(possible_words, best_word, feedback):
    res_list = []
    for pword in possible_words:
        if word_fit(pword, best_word, feedback):
            res_list.append(pword)
    return res_list

# Функция для расчета энтропии
def calculate_entropy(word, possible_words):
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
    if (len(feedback)!=5) or (not(set(feedback) <= set('BGY'))):
        return False
    return True