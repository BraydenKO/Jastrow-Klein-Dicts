"""
Im not a huge fan of the way this runs.
TODO: Organize and optimize
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

def greek_in_LSJ(word,LSJ,heb_word=""):
    """
    Args:
        word (str): A Klein-spelling of a word
    Returns:
        str: The correct greek spelling based on LSJ dict
    """
    replacements, lookup = create_lookup()
    greek_words = []
    
    new_word = word
    if word[0]=="h":
        new_word = word[1:]
    
    # Two letter consonants
    pattern = re.compile("|".join(map(re.escape, replacements.keys())))
    new_word = pattern.sub(lambda match: replacements[match.group(0)], new_word)

    pattern = re.compile("|".join(map(re.escape, lookup.keys())))
    greek_word = pattern.sub(lambda match: lookup[match.group(0)], new_word)
    greek_words = generate_words(greek_word)

    greek_words = list(set(greek_words))

    verified_greek_words = []

    for greek_word in greek_words:
        matched_rows = LSJ.loc[LSJ["MembershipKey"]==greek_word, "Entry"]
        for match in matched_rows:
            verified_greek_words.append(match)
    
    if len(verified_greek_words)==0:
        if len(greek_words)==1: # Even though it wasn't found, it unambiguous
            return greek_words[0], False
        # verified_greek_words.append(check_again(word,lookup,LSJ))
        # if verified_greek_words is None:
        #     print(f"No greek word found for {word}, {heb_word}: {greek_words}")
        #     return word, False
        # else:
        #     print(verified_greek_words)
        #     return verified_greek_words[0]
        return word, True
    elif len(verified_greek_words)>1:
        # print(f"Multiple words for for {word}, {heb_word}: {verified_greek_words}")
        return word, True
    else:
        return verified_greek_words[0], False


# def check_again(word,lookup,LSJ):
#     pattern = re.compile("|".join(map(re.escape, lookup.keys())))
#     if word[-3:] == "ein":
#         new_word = word[:-3]
#         suff = "ειν"
#     else:
#         suff = ""
#         for idx,letter in enumerate(word[::-1]):
#             if letter not in ("e","o","i"):
#                 suff = letter + suff 
#             else:
#                 break
#         suff = pattern.sub(lambda match: lookup[match.group(0)], suff)
#         new_word = word[:idx]

#     greek_word = pattern.sub(lambda match: lookup[match.group(0)], new_word)
#     greek_words = generate_words(greek_word)
#     greek_words = list(set(greek_words))
    
#     verified_greek_words = []
#     for greek_word in greek_words:
#         check = len(greek_word)
#         for idx in range(len(LSJ)):
#             greek = LSJ.iloc[idx,1][:check]
#             if greek==greek_word:
#                 verified_greek_words.append(greek+suff)
#                 break
#     if len(verified_greek_words)==0:
#         return None
#     return " or ".join(verified_greek_words)
            
