import os
import pandas as pd
import re
import unicodedata

fileName = "Greek-Jastrow.csv"

dir = os.path.dirname(__file__) + '/../data/01-Merged XML'
filePath  = f"{dir}/{fileName}"
# regex to identify a Greek word (might be overkill)
greek_letters = re.compile(r'\b\w*[\u0386-\u03C9\u1F00-\u1FFE\u0300-\u0305\u0313-\u0315\u0340-\u0344]+-?\w*\b')

def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output if len(output)>1 else output[0]

def get_greek_word(df):
    greek_words = []
    extra_rows = []
    for idx in range(len(df)):
        row = df.iloc[idx]
        match = greek_letters.findall(row["Definition"])
        if isinstance(match, list):
            greek_words.append(match[0].lower())
            for m in match[1:]:
                duplicated_row = row.copy()
                duplicated_row["Greek Entry"] = m.lower()
                extra_rows.append(duplicated_row)
        else:
           greek_words.append(match[0].lower()) 
    print(f"Adding {len(extra_rows)} more rows than the original dict")
    return greek_words, extra_rows

def re_organize_df(df, greek_words,extra_rows):
    df["Greek Entry"] = greek_words
    df = pd.concat([df,pd.DataFrame(extra_rows)],ignore_index=True)
    df['SortKey'] = df["Greek Entry"].apply(lambda x: unicodedata.normalize('NFD', x))
    df = df.sort_values(by="SortKey")
    df.drop('SortKey', axis=1, inplace=True)
    df = df.reindex(columns=['Unnamed: 0', 'Greek Entry', 'Entry', 'Definition'])
    return df    

if __name__ == "__main__":
    df = load_dfs(filePath)
    greek_words, extra_rows = get_greek_word(df)
    df = re_organize_df(df, greek_words,extra_rows)
    df.to_csv(f"{dir}/Greek-Heb_Aram.csv", index=False)