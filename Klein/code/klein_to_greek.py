 # NOTE: Useing regex instead of re to make variable width lookahead
import sys
import os
sys.path.append(os.path.dirname(__file__) + "/../..")

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


def greekify(df,LSJ):
    greek_entries = []
    is_roman_col = []
    for greek_entry in df["Greek Entry"]:
        verified_greek, is_roman = in_LSJ.greek_in_LSJ(greek_entry,LSJ)
        if not is_roman:
            verified_greek = f"{verified_greek} ({greek_entry})"
        greek_entries.append(verified_greek)
        is_roman_col.append(is_roman)

    df["Greek Entry"] = greek_entries
    df["IsRoman"] = is_roman_col
    return df

def get_greeked_df(df):
    LSJ = load_dfs(LSJPath)
    df = greekify(df,LSJ)
    return df