import os
import pandas as pd
import re
import unicodedata

fileName = "Greek-Jastrow.csv"

dir = os.path.dirname(__file__) + '/../data/01-Merged XML'
filePath  = f"{dir}/{fileName}"
greek_letters = re.compile(r'\b\w*[\u0386-\u03C9\u1F00-\u1FFE\u0300-\u0306\u0308-\u0344]+[-]*\w*\b')

def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output if len(output)>1 else output[0]

def get_greek_word(df):
    greek_words = []
    for row in df["Definition"]:
        match = greek_letters.findall(row)
        if isinstance(match, list):
            greek_words.append(match[0].lower())
        else:
            greek_words.append(match.lower())
    return greek_words

def re_organize_df(df, greek_words):
    df["Greek Entry"] = greek_words
    df['SortKey'] = df["Greek Entry"].apply(lambda x: unicodedata.normalize('NFD', x))
    df = df.sort_values(by="SortKey")
    df.drop('SortKey', axis=1, inplace=True)
    df = df.reindex(columns=['Unnamed: 0', 'Greek Entry', 'Entry', 'Definition'])
    return df    

if __name__ == "__main__":
    df = load_dfs(filePath)
    greek_words = get_greek_word(df)
    df = re_organize_df(df, greek_words)
    df.to_csv(f"{dir}/Greek-Heb_Aram.csv", index=False)