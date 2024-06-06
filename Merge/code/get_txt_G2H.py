"""
Takes the csv of merged_GreektoHeb and converts it to txt.
"""
import pandas as pd
import os

fileName = "merged_GreektoHeb"

dir = os.path.dirname(__file__) + '/../..'
filePath = f"{dir}/Merge/data/{fileName}.csv"

def load_df(filePath):
    return pd.read_csv(filePath)

def to_txt(df,fileName):
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{fileName}</title>
</head>
<body>
"""
    html_content += f"<h1>Kohler's Dictionary of Greek Words Used in Rabbinic Literature (KGRL)</h1>\n"
    for idx, row in enumerate(df.iterrows()):
        html_content += f"<h3>{row[1]['Greek Entry']} - {row[1]['Entry']}</h3>\n"
        html_content += f"<h6>{idx}, {row[1]['Dictionary ID']}</h6>\n"
        definition = row[1]["Definition"]
        while len(definition) > 79:
            idx = definition.find(" ", 79)
            html_content += f"<h5>{definition[:idx]}"
            definition = definition[idx:]

        html_content += f"<h5>{definition}</h5>\n"
        html_content += "<p></p>\n"
    html_content +="""
</body>
</html>
"""
    with open(f"{dir}/Merge/data/{fileName}.html", 'w',encoding="utf-8") as file:
        file.write(html_content)
    return
    with open(f"{dir}/Merge/data/{fileName}.txt", 'w', encoding="utf-8") as file:
        file.write("Kohler's Dictionary of Greek Words Used in Rabbinic Literature (KGRL)")
        for row in df.iterrows():
            file.write(f"{row[1]['Greek Entry']} - {row[1]['Entry']}")
            file.write("\n")
            file.write(row[1]["Dictionary ID"])
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
    df = load_df(filePath)
    to_txt(df, fileName)