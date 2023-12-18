"""
Gets specifically only greek-related entries from
the main Jastrow csv. Creates a file called 'Greek-Jastrow.csv'
"""
import pandas as pd
import os

fileName = "Jastrow-full.csv"
data_dir = os.path.dirname(__file__) + '/../data/01-Merged XML'
filePath = f"{data_dir}/{fileName}"

if __name__ == "__main__":
    df = pd.read_csv(filePath) 
    cols = df.columns
    df = df[df["Has_Greek"]]
    df.to_csv(f"{data_dir}/Greek-Jastrow.csv", index=False, columns=cols)

    with open(f"{data_dir}/Greek-Jastrow.txt", 'w', encoding="utf-8") as file:
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
    
    print(f"{len(df)} entries")