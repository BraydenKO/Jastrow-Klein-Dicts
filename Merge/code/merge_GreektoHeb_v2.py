import sys
import os
sys.path.append(os.path.dirname(__file__) + "/../..")
from Klein.code import klein_to_greek


import pandas as pd
from unidecode import unidecode
import unicodedata


fileName = "Greek-Heb_Aram.csv"

dir = os.path.dirname(__file__) + "/../.."
filePath_0  = f"{dir}/Jastrow/data/01-Merged XML/{fileName}"
filePath_1  = f"{dir}/Klein/data/{fileName}"
#["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "v", "x", "y", "z", "í", "ï", "ē", "ō"]

def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output if len(output)>1 else output[0]

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

def sort_words(jastrow_df, kleindf):
    # Prepare Dicts
    X =  kleindf.loc[kleindf["IsRoman"]==True,"Greek Entry"]
    kleindf.loc[kleindf["IsRoman"]==True,"Greek Entry"] = X.apply(tag_roman_word)
    jastrow_df["IsRoman"]=False

    # Sort them
    df = pd.concat([jastrow_df,klein_df])
    df["SortKey"] = df["Greek Entry"].apply(lambda x: unidecode(unicodedata.normalize("NFD", x)))
    df = df.sort_values(by="SortKey", kind="mergesort")
    df.drop("SortKey",axis=1, inplace=True)


    # Untag
    X = df.loc[df["IsRoman"]==True,"Greek Entry"]
    df.loc[df["IsRoman"]==True,"Greek Entry"] = X.apply(untag_roman_word)

    df.drop("IsRoman",axis=1, inplace=True)
    return df


if __name__ == "__main__":
    print("Loading dfs...")
    jastrow_df, klein_df = load_dfs(filePath_0, filePath_1)
    print("Converting Klein entries into Greek...")
    klein_df = klein_to_greek.get_greeked_df(klein_df)
    print("Sorting df...")
    df = sort_words(jastrow_df,klein_df)
    df.to_csv(f"{dir}/Merge/data/merged_GreektoHeb_v2.csv", index=False)