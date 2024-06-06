"""
Merges the Greek entries from Jastrow and Klein sorted
by the hebrew/aramaic word.

In the Jastrow entries, the entry contains a greek character.
In the Klein entries, the entry contrains either "Greek" or "Gk." even if it
doesn't contain any Ancient Greek root or word.

"""
import re
import os
import pandas as pd

fileName_0 = "Greek-Jastrow.csv"
fileName_1= "Greek-Klein.csv"

dir = os.path.dirname(__file__) + '/../..'
filePath_0  = f"{dir}/Jastrow/data/01-Merged XML/{fileName_0}"
filePath_1  = f"{dir}/Klein/data/{fileName_1}"

def sort_hebrew(heb_text,indeces):
    text = []
    for entry in heb_text:
        text.append(re.sub(r'[\u0591-\u05c7()*, □]', '', entry))

    x = zip(text, indeces)
    y = sorted(x)
    output_indeces = [entry[1] for entry in y]
    return output_indeces

def merge_dfs(*dfs):
    return pd.concat(dfs)

def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output

def sort_df(df):
    indeces = range(len(df))
    entries = df["Entry"]
    indeces = sort_hebrew(entries, indeces)

    return df.iloc[indeces]

def to_txt(df,fileName):
    with open(f"{dir}/Merge/data/{fileName}", 'w', encoding="utf-8") as file:
        for row in df.iterrows():
            file.write(row[1]["Entry"])
            file.write("\n")
            definition = row[1]["Definition"]
            while len(definition) > 79: # pep8 style
                file.write(definition[:79])
                file.write("\n")
                definition = definition[79:]
            file.write(definition)
            file.write("\n")
            file.write("\n")

if __name__ == "__main__":
    jastrow_df, klein_df = load_dfs(filePath_0,filePath_1)
    df = merge_dfs(jastrow_df,klein_df)
    df = sort_df(df)
    df.to_csv(f"{dir}/Merge/data/merged.csv", index=False)
    to_txt(df, "merged.txt")