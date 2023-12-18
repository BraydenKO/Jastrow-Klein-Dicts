import os
import pandas as pd
from unidecode import unidecode
import unicodedata
import re
import time

import requests
from bs4 import BeautifulSoup

fileName = "Greek-Heb_Aram.csv"

dir = os.path.dirname(__file__) + "/../.."
filePath_0  = f"{dir}/Jastrow/data/01-Merged XML/{fileName}"
filePath_1  = f"{dir}/Klein/data/{fileName}"
filePath_2  = f"{dir}/Merge/data/manual_RomantoGreek_v3.csv"

def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output if len(output)>1 else output[0]

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

def get_greeked_word(word):
    """
    Args:
        word (str): A Klein-spelling of a word
    Returns:
        str: The correct greek spelling based on wiktionary
            or the original roman version of the word.
        bool: True if the returned string is the original
            word. False if the returned string is the greek
            spelled word.
        list: A list of the possible greek words if there are
            multiple candidates. Used by nongreeked_entries.csv
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
    
    verified_words = []
    for greek_word in greek_words:
        url = generate_url(greek_word)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        greek_word = soup.find("span", "searchmatch")
        if greek_word:
            verified_words.append(greek_word.text)
    if len(verified_words)==0:
        # Even though it wasn't found, it's unambiguous.
        # NOTE: This word won't have accents.
        if len(greek_words)==1: 
            return greek_words[0], False, []

        return word, True, []

    elif len(verified_words)>1:
        # print(f"Multiple words for for {word}, {heb_word}: {verified_greek_words}")
        return word, True, verified_words
    else:
        return verified_words[0], False, []
        
    
def generate_url(greek_word):
    return f"https://en.wiktionary.org/w/index.php?search={greek_word}&title=Special:Search&profile=advanced&fulltext=1&ns0=1"

def get_greeked_df(df,manual_romantogreek):
    entries = []
    is_roman_col = []
    possible_greeks = []
    row_count = len(df)
    count = 1
    start_time = time.time()
    print(f"0.00% complete",end="")
    for entry in df["Greek Entry"]:
        if count%5 == 0:
            p = 100*count/row_count
            t = time.time()-start_time
            e = t*(100/p -1) #t/p = T/100 & T = e + t -> e = t*(100/p - 1)
            print(f"\r{p:.2f}% complete. {t:.2f}s elapsed. Expected to finish in {e:.2f}s",end="")
        new_entry, is_roman, possible_greek = get_greeked_word(entry)
        if not is_roman:
            new_entry = new_entry + f" ({entry})"
        else:
            greek_entries = manual_romantogreek.loc[manual_romantogreek["Roman Entry"]==new_entry, "Greek Entry"]
            if not greek_entries.empty:
                new_entry = greek_entries[0]
                is_roman = False
        entries.append(new_entry)
        is_roman_col.append(is_roman)
        possible_greeks.append(possible_greek)
        count+=1
    print()

    df["Greek Entry"] = entries
    df["IsRoman"] = is_roman_col
    df["PossibleGreek"] = possible_greeks
    return df

def tag_roman_word(word,tag="ωωω"):
    """
    Adds a Greek letter to put the word into proper alpha-omega order.
    Adds an em—dash to make sure the roman spelled words come after greek
    spelled words.
    """
    replacements = {
        "th": "θ",
        "ph": "φ",
        "ch": "χ"
    }
    for key in replacements.keys():
        if word[:2] == key:
            word = replacements[key] + word[2:]
    lookup = {
        "a": "α",
        "b": "β",
        "v": "β",
        "g": "γ",
        "d": "δ",
        "e": "ε",
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
        "o": "ο",
        "p": "π",
        "r": "ρ",
        "s": "σ",
        "t": "τ",
        "u": "υ",
        "y": "υ",
        "ō": "ω",
    }
    if word[0] == "h":
        return lookup[word[1]] + tag + word[1:] + "<tag>h"

    return lookup.get(word[0], word[0]) + tag + word

def untag_roman_word(word,tag="ωωω"):
    word = word[len(tag)+1:]
    if word[-6:] == "<tag>h": # Has a tag
        word = "h" + word[:-6]
    replacements = {
        "θ" : "th",
        "φ" : "ph",
        "χ" : "ch",
        "ψ" : "ps"
    }
    for key in replacements.keys():
        if word[0] == key:
            word = replacements[key] + word[1:]

    return word

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn').lower()

def sort_words(jastrow_df, klein_df):
    # Prepare Dicts
    klein_df.drop("PossibleGreek",axis=1,inplace=True)
    X =  klein_df.loc[klein_df["IsRoman"]==True,"Greek Entry"]
    klein_df.loc[klein_df["IsRoman"]==True,"Greek Entry"] = X.apply(tag_roman_word)

    jastrow_df["IsRoman"]=False

    # Sort them
    df = pd.concat([jastrow_df,klein_df])
    df["SortKey"] = df["Greek Entry"].apply(strip_accents)
    df = df.sort_values(by="SortKey", kind="mergesort")
    df.drop("SortKey",axis=1, inplace=True)


    # Untag
    X = df.loc[df["IsRoman"]==True,"Greek Entry"]
    df.loc[df["IsRoman"]==True,"Greek Entry"] = X.apply(untag_roman_word)
    
    #df.drop("IsRoman",axis=1, inplace=True)
    return df

def save_romans(df):
    romans = df.loc[df["IsRoman"]==True]
    print(f"There are {len(romans)} un-greeked words")
    romans.to_csv(f"{dir}/Merge/data/nongreeked_entries_v3.csv", index=False)

if __name__ == "__main__":
    print("Loading dfs...")
    jastrow_df, klein_df, manual_romantogreek = load_dfs(filePath_0, filePath_1, filePath_2)

    print("Converting Klein entries into Greek...")
    klein_df = get_greeked_df(klein_df,manual_romantogreek)
    save_romans(klein_df)

    print("Sorting df...")
    df = sort_words(jastrow_df,klein_df)
    df.to_csv(f"{dir}/Merge/data/merged_GreektoHeb_v3.csv", index=False)