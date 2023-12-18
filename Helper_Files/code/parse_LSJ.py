"""
Converts entries from LSJ into greek charachter.
NOTE: The LSJ files aren't in this directory and can be
retrieved from https://github.com/PerseusDL/lexica 
"""

import xml.etree.ElementTree as XeT
import os
import pandas as pd
import re
import unicodedata

fileNames = [f"LSJ{n}.xml" for n in range(1,28)]
data_dir = os.path.dirname(__file__) + '/../data/LSJxml'
filePaths = [f"{data_dir}/{fileName}" for fileName in fileNames]

def create_lookup():
    lookup = {
            "a": "α",
            "b": "β",
            "g": "γ",
            "d": "δ",
            "e": "ε",
            "z": "ζ",
            "h": "η",
            "q": "θ",
            "i": "ι",
            "k": "κ",
            "l": "λ",
            "m": "μ",
            "n": "ν",
            "c": "ξ",
            "o": "ο",
            "p": "π",
            "r": "ρ",
            "s": "σ",
            "t": "τ",
            "u": "υ",
            "f": "φ",
            "x": "χ",
            "y": "ψ",
            "w": "ω",
            "a|":"ᾳ",
            "h|":"ῃ",
            "w|":"ῳ",
            "a=":"ᾶ",
            "h=":"ῆ",
            "i=":"ῖ",
            "u=":"ῦ",
            "w=":"ῶ"
        }

    # Non Capital letters: Format of {letter}{accent}
    # Capital letters: Formate 0f *{accent}{letter}
    for i, letter in enumerate(["a","e","h","i","o","u","w"]):
        # 1F00 = 7936
        ucode_pref = 7936 + 16*i
        for j, diacritic1 in enumerate((")","(",")\\","(\\",")/","(/",")=","(=")):
            ucode = ucode_pref + j
            lookup[letter+diacritic1] = chr(ucode)
            lookup["*"+diacritic1+letter] = chr(ucode)
        
        # 1F70 = 8048
        lookup[letter+"\\"] = chr(8048 + 2*i)
        lookup["*"+"\\"+letter] = chr(8048 + 2*i)

        lookup[letter+"/"] = chr(8048 + 2*i + 1)
        lookup["*"+"/"+letter] = chr(8048 + 2*i + 1)

    for i, letter in enumerate(["a","h","w"]):
        # 1F84 = 8068, 1F94 = 8084
        lookup[letter+")/|"] = chr(8068 + 16*i)
        lookup["*"+")/|"+letter] = chr(8068 + 16*i)

        lookup[letter+")=|"] = chr(8068 + 16*i + 2)
        lookup["*"+")=|"+letter] = chr(8068 + 16*i + 2)

    return lookup
def greekify_entry(entry,lookup):
    """
    Args:
        entry (str): Entry spelled in LSJ style
    Returns:
        str: Greek spelling of word with accents
    """

    # Use regular expressions to replace characters
    # lookup.keys() is read backwards to prioritize the special vowel cases with accents
    pattern = re.compile("|".join(map(re.escape, list(lookup.keys())[::-1])))
    result = pattern.sub(lambda match: lookup[match.group(0)], entry)
    if result[0] == "*":
        result = result.title()
    result = result.replace("*","")
    return result

def get_entry_words(filePaths):
    entry_words=[]
    lookup = create_lookup()
    for idx,filePath in enumerate(filePaths):
        print(f"Processing LSJ{idx+1}.xml")
        xmlparse = XeT.parse(filePath)
        root = xmlparse.getroot()
        entries = root.findall(".//entryFree")
        for entry in entries:
            word = greekify_entry(entry.get("key"),lookup)
            entry_words.append(word)
    return entry_words

def un_accent_LSJ(df):
    def normalize(word):
         result= ''.join([c for c in unicodedata.normalize('NFD', word) if not unicodedata.combining(c)])
         return re.sub(r'\d', '', result)
    df["MembershipKey"] = df["Entry"].apply(normalize)
    return df

if __name__ == "__main__":
    entry_words = get_entry_words(filePaths)
    df = pd.DataFrame(entry_words, columns=["Entry"]) 
    df = un_accent_LSJ(df)


    df.to_csv(f"{data_dir}/LSJ_Entries.csv",index=False)
    
        