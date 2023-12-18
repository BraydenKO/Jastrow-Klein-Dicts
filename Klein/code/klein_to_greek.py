"""
These functions are specifically used when merging
the Jastrow version of Greek-Heb_Aram.csv and the Klein version.
The Greek words in Klein's dictionary are spelled with Latin
characters. 
These functions help convert those words into
Greek spelling to match what Jastrow has."""
# NOTE: Useing regex instead of re to make variable width lookahead
import sys
import os
sys.path.append(os.path.dirname(__file__) + "/../..")
import time
import regex
import pandas as pd
import unicodedata
from Helper_Files.code import in_LSJ

dir = os.path.dirname(__file__) + "/../.."
LSJPath = f"{dir}/Helper_Files/data/LSJ_Entries.csv"

def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output if len(output)>1 else output[0]

def re_organize_df(df, greek_words,extra_rows):
    df["Greek Entry"] = greek_words
    df = df.drop(df[df["Greek Entry"] == "REMOVE"].index)
    df = pd.concat([df,pd.DataFrame(extra_rows)],ignore_index=True)
    df['SortKey'] = df["Greek Entry"].apply(lambda x: unicodedata.normalize('NFD', x))
    df = df.sort_values(by="SortKey", kind="mergesort")
    df.drop('SortKey', axis=1, inplace=True)
    df = df.reindex(columns=['Unnamed: 0', 'Greek Entry', 'Entry', 'Definition'])
    return df


def greekify(df,LSJ,manual_romantogreek):
    greek_entries = []
    is_roman_col = []
    possible_greeks = []
    row_count = len(df)
    start_time = time.time()
    count = 1
    print(f"0.00% complete",end="")
    for greek_entry in df["Greek Entry"]:
        if count%100 == 0:
            p = 100*count/row_count
            t = time.time()-start_time
            e = t*(100/p -1) #t/p = T/100 & T = e + t -> e = t*(100/p - 1)
            print(f"\r{p:.2f}% complete. {t:.2f}s elapsed. Expected to finish in {e:.2f}s",end="")
        verified_greek, is_roman, possible_greek = in_LSJ.greek_in_LSJ(greek_entry,LSJ)
        if not is_roman:
            verified_greek = f"{verified_greek} ({greek_entry})"
        else:
            manual_greek_entries = manual_romantogreek.loc[manual_romantogreek["Roman Entry"]==verified_greek.lower(), "Greek Entry"]
            if not manual_greek_entries.empty:
                # Have to use .iloc because the index isn't always the same number which Series[0] would use.
                verified_greek = f"{manual_greek_entries.iloc[0]} ({greek_entry})"
                is_roman = False
        if greek_entry[0].isupper():
            verified_greek = verified_greek[0].upper() + verified_greek[1:]
        greek_entries.append(verified_greek)
        is_roman_col.append(is_roman)
        possible_greeks.append(possible_greek)
        count +=1
    print()

    df["Greek Entry"] = greek_entries
    df["IsRoman"] = is_roman_col
    df["PossibleGreek"] = possible_greeks
    return df

def get_greeked_df(df,manual_romantogreek):
    LSJ = load_dfs(LSJPath)
    df = greekify(df,LSJ,manual_romantogreek)
    return df