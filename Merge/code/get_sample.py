import pandas as pd
from get_txt_G2H import to_txt
from merge_GreektoHeb import strip_accents
import os

fileName = "merged_GreektoHeb"

dir = os.path.dirname(__file__) + '/../..'
filePath = f"{dir}/Merge/data/{fileName}.csv"

def load_df(filePath):
    return pd.read_csv(filePath)

def get_samples(df, n = 10, seed = 1):
    klein = df[df['Dictionary ID'].str.split(' ').str[0] == "Klein"]
    jastrow = df[df['Dictionary ID'].str.split(' ').str[0] == "Jastrow"]
    klein_sample = klein.sample(n = n//2, random_state=seed)
    jastrow_sample = jastrow.sample(n = n - n//2, random_state=seed)

    df = pd.concat([jastrow_sample,klein_sample])
    df["SortKey"] = df["Greek Entry"].apply(strip_accents)
    df = df.sort_values(by="SortKey", kind="mergesort")
    df.drop("SortKey",axis=1, inplace=True)

    return df

if __name__ == "__main__":
    df = load_df(filePath)
    df = get_samples(df, n = 50, seed =3)
    to_txt(df,"Sample")

    