"""
Takes the csv of merged_GreektoHeb and converts it to txt.
"""
import pandas as pd
import os

fileName_g2h = "merged_GreektoHeb"
fileName_h2g = "merged_HebtoGreek"

dir = os.path.dirname(__file__) + '/../..'
filePath_g2h = f"{dir}/Merge/data/{fileName_g2h}.csv"
filePath_h2g = f"{dir}/Merge/data/{fileName_h2g}.csv"


def load_dfs(*filePaths):
    output = []
    for path in filePaths:
        output.append(pd.read_csv(path))
    return output if len(output)>1 else output[0]

def to_txt(df,fileName, is_gktoheb, is_index=False, is_sample=False):
    html_content = f"""
<!DOCTYPE html>
<html lang="en" prefix="og: https://ogp.me/ns#">
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
    <meta property="og:title" content="Lexicon of Rabbinic Greek" />
</head>
<body style="padding-bottom: 30px;">
"""
    html_content += f"<h1>Lexicon of Rabbinic Greek</h1>\n"
    html_content += f"<h2>and Greek words in later Hebrew texts,</h2>\n"
    html_content += f"<h2>based on the Jastrow and Klein dictionaries</h2>\n"
    html_content += f"<h2>by Brayden Kohler</h2>\n"
    if is_gktoheb and not is_sample:
        other_version_link = r"https://braydenko.github.io/Jastrow-Klein-Dicts/websites/merged_HebtoGreek.html"
        html_content += f"""<h7>Sorted by Greek words in headword. </h7>
        Click <a href={other_version_link}>HERE</a> to see this lexicon sorted by the Hebrew words."""
    elif not is_gktoheb and not is_sample:
        other_version_link = r"https://braydenko.github.io/Jastrow-Klein-Dicts/"
        html_content += f"""<h7>Sorted by Hebrew words in headword.</h7>
        Click <a href={other_version_link}>HERE</a> to see this lexicon sorted by the Greek words."""

    intro_link = r"https://braydenko.github.io/Jastrow-Klein-Dicts/websites/intro.html"
    html_content += f"<h3><a href={intro_link}>Introduction and Selection Criteria</a></h3>\n"
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
    if is_index:
      with open(f"{dir}/index.html", 'w',encoding="utf-8") as file:
          file.write(html_content)
      return
    
    with open(f"{dir}/websites/{fileName}.html", 'w',encoding="utf-8") as file:
        file.write(html_content)

if __name__ == "__main__":
    df_g2h, df_h2g = load_dfs(filePath_g2h,filePath_h2g)
    to_txt(df_g2h, fileName_g2h, is_gktoheb=True, is_index=True)
    to_txt(df_h2g, fileName_h2g, is_gktoheb=False)