"""
Im not a huge fan of the way this runs.
TODO: Organize and optimize

These functions are used to determine whether a word or
its variations are in LSJ
"""

import pandas as pd
import os
import unicodedata
import re

fileName = "LSJ_Entries.csv"
dir = os.path.dirname(__file__) + '/../data'
filePath  = f"{dir}/{fileName}"

lsj_entries = pd.read_csv(filePath)

def create_lookup():
    replacements = {
            "th": "θ",
            "ph": "φ",
            "ch": "χ",
            "ps": "ψ",
            "rh": "ρ"
        }

    lookup = {
        "a": "α",
        "b": "β",
        "v": "β",
        "g": "γ",
        "d": "δ",
        # "e": "ε" or "e" : "η"
        "ē": "ε",
        "z": "ζ",
        "i": "ι",
        "í": "ι",
        "ï": "ι",
        "c": "κ",
        "k": "κ",
        "l": "λ",
        "m": "μ",
        "n": "ν",
        "x": "ξ",
        # "o": "ο" or "o": "ω"
        "p": "π",
        "r": "ρ",
        "s": "σ",
        "t": "τ",
        "u": "υ",
        "y": "υ",
        "ō": "ω",
    }

    return replacements, lookup

def generate_words(word):
    results = []
    def generate_variations(pref,suff):
        if len(suff)==0:
            pref = pref.replace("ηι","ῃ")
            pref = pref.replace("ωι","ῳ")
            results.append(pref)
            return
        
        if suff[0]=="e":
            generate_variations(pref+"ε",suff[1:])
            generate_variations(pref+"η",suff[1:])
        elif suff[0]=="o":
            generate_variations(pref+"ο",suff[1:])
            generate_variations(pref+"ω",suff[1:])
        else:
            generate_variations(pref + suff[0],suff[1:])
        return word
    generate_variations("",word)
    return results


replacements, lookup = create_lookup()
pattern_2letter = re.compile("|".join(map(re.escape, replacements.keys())))
pattern = re.compile("|".join(map(re.escape, lookup.keys())))
def greek_in_LSJ(word,LSJ):
    """
    Args:
        word (str): A Klein-spelling of a word
    Returns:
        str: The correct greek spelling based on LSJ dict
            or the original latin version of the word.
        bool: True if the returned string is the original
            word. False if the returned string is the greek
            spelled word.
        list: A list of the possible greek words if there are
            multiple candidates. Used by nongreeked_entries.csv
    """
    
    new_word = word.lower()
    
    if new_word[0]=="h":
        new_word = word[1:]
    
    # Two letter consonants
    new_word = pattern_2letter.sub(lambda match: replacements[match.group(0)], new_word)

    greek_word = pattern.sub(lambda match: lookup[match.group(0)], new_word)
    greek_words = generate_words(greek_word)

    verified_greek_words = []

    for greek_word in greek_words:
        matched_rows = LSJ.loc[LSJ["MembershipKey"]==greek_word, "Entry"]
        for match in matched_rows:
            verified_greek_words.append(match)
    
    if len(verified_greek_words)==0:
        return word, True, []
    
    elif len(verified_greek_words)>1:
        return word, True, verified_greek_words
    else:
        return verified_greek_words[0], False, []
