import os
import pandas as pd
import unicodedata
from unidecode import unidecode

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

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def sort_words(greekdf, romandf):
    # Prepare Dicts
    romandf["Greek Entry"] = romandf["Greek Entry"].apply(tag_roman_word)
    greekdf["IsRoman"] = False
    romandf["IsRoman"] = True
    # Sort them
    df = pd.concat([greekdf,romandf])
    df["SortKey"] = df["Greek Entry"].apply(strip_accents)
    df = df.sort_values(by="SortKey", kind="mergesort")
    df.drop("SortKey",axis=1, inplace=True)

    df.loc[df["IsRoman"]==True,"Greek Entry"] = df.loc[df["IsRoman"]==True,"Greek Entry"].apply(
        untag_roman_word
    )
    df.drop("IsRoman",axis=1, inplace=True)
    return df


if __name__ == "__main__":
    greekdf, romandf = load_dfs(filePath_0, filePath_1)
    df = sort_words(greekdf,romandf)
    df.to_csv(f"{dir}/Merge/data/merged_GreektoHeb.csv", index=False)