 # NOTE: Useing regex instead of re to make variable width lookahead
import regex
import os
import pandas as pd
import unicodedata

fileName = "Greek-Klein.csv"

dir = os.path.dirname(__file__) + '/../data'
filePath  = f"{dir}/{fileName}"

greek_letters = regex.compile(r'''\b(?<=Gk. suff. -\s?|Greek suff. -\s?|Gk. suff. –\s?|Gk. –\s?|Gk. -\s?
                              |Gk. \(pathos\)\s?|Gk. form\s?|Gk. from\s?|Gk. adjectives ending in – |Gk. vulgar var.|
                              Gk.\s?)\w+(?<!suff|word|words|form|from|pref|adjectives|privative|vulgar)\b''',regex.X)

def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output if len(output)>1 else output[0]

def get_greek_word(df):
    greek_words= []
    extra_rows = []
    for idx in range(len(df)):
        row = df.iloc[idx]
        # Is >1 and not >=1 to exclude mentions of Gk. t corresponding to Heb tet
        match = list(set( i for i in greek_letters.findall(row["Definition"]) if len(i)>1))
        # Handle the first match easily by adding to the same row
        try:
            greek_words.append(match[0].lower())
        except: # Doesn't explicitly mention the word, just mentions "Greek"
            greek_words.append("REMOVE")
            continue
        # later matches need duplicated rows
        for m in match[1:]:
            duplicated_row = row.copy()
            duplicated_row["Greek Entry"] = m.lower()
            extra_rows.append(duplicated_row)
    print(f"Adding {len(extra_rows)} more rows than the original dict")
    return greek_words, extra_rows

def re_organize_df(df, greek_words,extra_rows):
    df["Greek Entry"] = greek_words
    df = df.drop(df[df["Greek Entry"] == "REMOVE"].index)
    df = pd.concat([df,pd.DataFrame(extra_rows)],ignore_index=True)
    df['SortKey'] = df["Greek Entry"].apply(lambda x: unicodedata.normalize('NFD', x))
    df = df.sort_values(by="SortKey", kind="mergesort")
    df.drop('SortKey', axis=1, inplace=True)
    df = df.reindex(columns=['Unnamed: 0', 'Greek Entry', 'Entry', 'Definition'])
    return df

        
            


if __name__ == "__main__":
    df = load_dfs(filePath)
    greek_words, extra_rows = get_greek_word(df)
    df = re_organize_df(df, greek_words,extra_rows)
    df.to_csv(f"{dir}/Greek-Heb_Aram.csv", index=False)