"""
Merges the Jastrow and Klein entries sorted by 
the Greek word.
This version searches the LSJ dict for matches to
Klein's Greek words.
"""
import sys
import os
sys.path.append(os.path.dirname(__file__) + "/../..")
from Klein.code import klein_to_greek


import pandas as pd
import unicodedata


fileName = "Greek-Heb_Aram(final).csv"

dir = os.path.dirname(__file__) + "/../.."
filePath_0  = f"{dir}/Jastrow/data/01-Merged XML/{fileName}"
filePath_1  = f"{dir}/Klein/data/{fileName}"
filePath_2  = f"{dir}/Merge/data/manual_RomantoGreek.csv"

def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output if len(output)>1 else output[0]

def create_lookup():
    replacements = {
        "th": "θ",
        "ph": "φ",
        "ch": "χ"
    }
    base_lookup = {
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
    lookup = base_lookup.copy()
    for latin,greek in base_lookup.items():
        lookup[latin.upper()]=greek.upper()
        
    return replacements, lookup

def tag_roman_word(word,tag="ωωω"):
    """
    Adds a Greek letter to put the word into proper alpha-omega order.
    Adds an em—dash to make sure the roman spelled words come after greek
    spelled words.
    """
    for key in replacements.keys():
        if word[:2] == key:
            word = replacements[key] + word[2:]

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

    jastrow_df["Unnamed: 0"] = jastrow_df["Unnamed: 0"].apply(lambda id: f"Jastrow {id}")
    klein_df["Unnamed: 0"] = klein_df["Unnamed: 0"].apply(lambda id: f"Klein {id}") 


    # Sort them
    df = pd.concat([jastrow_df,klein_df])
    df["SortKey"] = df["Greek Entry"].apply(strip_accents)
    df = df.sort_values(by="SortKey", kind="mergesort")
    df.drop("SortKey",axis=1, inplace=True)

    # Untag
    X = df.loc[df["IsRoman"]==True,"Greek Entry"]
    df.loc[df["IsRoman"]==True,"Greek Entry"] = X.apply(untag_roman_word)

    df.drop("IsRoman",axis=1, inplace=True)
    df = df.rename(columns = {"Unnamed: 0": "Dictionary ID"})
  
    return df

def save_romans(df):
    romans = df.loc[df["IsRoman"]==True]
    romans.to_csv(f"{dir}/Merge/data/nongreeked_entries.csv", index=False)
    return romans["Greek Entry"].nunique()

def fix_holem(df):    
    # Check if Holem is above Waw
    #if 'ו' not in normalized_word or '\u05B9' not in normalized_word:
    #    return False
    def fix_holem_in_word(entry):
      i = 1
      while i < len(entry):
          if entry[i] == 'ו' and entry[i - 1] == '\u05B9':
              entry = entry[:i-1] + 'ו' + '\u05B9' + entry[i+1:]
              i+=1
          i+=1
      return entry
    df["Entry"] = df["Entry"].apply(fix_holem_in_word)

    return df

def get_hebtogk(df):
    # Get Hebrew to Greek version
    def strip_hebrew(word):
        word = word.replace(',', '')
        return ''.join([c for c in unicodedata.normalize('NFD', word) if unicodedata.category(c) == "Lo"])
    
    df["SortKey"] = df["Entry"].apply(strip_hebrew)
    df = df.sort_values(by="SortKey", kind="mergesort")
    df.drop("SortKey",axis=1, inplace=True)

    return df

if __name__ == "__main__":
    print("Loading dfs...")
    jastrow_df, klein_df, manual_romantogreek = load_dfs(filePath_0, filePath_1, filePath_2)

    print("Converting Klein entries into Greek...")
    klein_df = klein_to_greek.get_greeked_df(klein_df,manual_romantogreek)
    num_ungreeked = save_romans(klein_df)
    print(f"There are {num_ungreeked} un-greeked words")

    print("Sorting df...")
    replacements, lookup = create_lookup()
    df = sort_words(jastrow_df,klein_df)
    df = fix_holem(df)
    df_hebtogk = get_hebtogk(df)


    print("Saving df...")
    df.to_csv(f"{dir}/Merge/data/merged_GreektoHeb.csv", index=False)
    df_hebtogk.to_csv(f"{dir}/Merge/data/merged_HebtoGreek.csv", index=False)