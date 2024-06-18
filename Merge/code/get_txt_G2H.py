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
    <style>
        /* Add some basic styling for the footer */
        footer {{
            display: flex; /* Enables Flexbox layout */
            justify-content: left; 
            align-items: center;
            padding: 5px; 
            background-color: #f1f1f1;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            height: 30px; 
        }}
    </style>
</head>
<body>
"""
    html_content += f"<h1>Lexicon of Rabbinic Greek</h1>\n"
    html_content += f"<h2>and of Greek words in later Hebrew texts,</h2>\n"
    html_content += f"<h2>based on the Jastrow and Klein dictionaries (title is WIP)</h2>\n"
    html_content += f"<h2>by Brayden Kohler</h2>\n"
    link = r"https://htmlpreview.github.io/?https://github.com/BraydenKO/Jastrow-Klein-Dicts/blob/master/Merge/data/intro.html"
    html_content += f"<h3><a href={link}>Introduction and Selection Criteria</a></h3>\n"
    html_content += "<br>\n"
    for idx, row in enumerate(df.iterrows()):
        html_content += f"<h3>{row[1]['Greek Entry']} - {row[1]['Entry']}</h3>\n"
        html_content += f"<h6>{idx}, {row[1]['Dictionary ID']}</h6>\n"
        definition = row[1]["Definition"]
        while len(definition) > 79:
            idx = definition.find(" ", 79)
            html_content += f"<h5>{definition[:idx]}"
            definition = definition[idx:]

        html_content += f"<h5>{definition}</h5>\n"
        html_content += "<br>\n"
    html_content +="""
  <footer>
      <p>© 2024 by Brayden Kohler</p>
  </footer>
</body>
</html>
"""
    with open(f"{dir}/websites/{fileName}.html", 'w',encoding="utf-8") as file:
        file.write(html_content)
    return

if __name__ == "__main__":
    df = load_df(filePath)
    to_txt(df, fileName)