"""
Converts data\\01-Merged XML\\Jastrow-full.xml (xml) into csv.
To change the file, change the filePath and data_dir below:
"""
import xml.etree.ElementTree as XeT
import pandas as pd
import os
import re

fileName = "Jastrow-full.xml"
data_dir = os.path.dirname(__file__) + '/../data/01-Merged XML'
filePath = f"{data_dir}/{fileName}"

cols = ["Entry", "Definition", "Has_Greek"]
rows = []
greek_letters = re.compile(r'[Α-Ωα-ωὁ]+')
xmlparse = XeT.parse(filePath)
root = xmlparse.getroot()

def parse_entry(entry):
    # Get head-word of entry
    head_word = " ".join(word.text for word in entry.findall("head-word") if word.text is not None)

    # If a word has binyans, the definition is inside the binyan
    binyans = entry.findall("binyan")
    binyan_def = ""
    if len(binyans)>0:
        binyan_def = get_binyan(binyans)
  
    senses = entry.find("senses") # Is the parent containing senses
    
    # If the only senses are in the binyan, don't search through senses
    if senses is None:
        if len(binyans)>0:
               senses = []
        else:
            raise Exception(f"No senses nor binyans for {entry.atrrib}")

    full_definition = def_from_senses(senses)

    full_definition = full_definition + " | " + binyan_def

    has_greek = greek_letters.search(full_definition) is not None

    return { 
        "Entry" : head_word,
        "Definition" : full_definition,
        "Has_Greek" : has_greek
    }

def def_from_senses(senses):
    full_definition = ""

    for sense in senses:
        number = getattr(sense.find("number"), "text", "")
        full_definition = full_definition + number

        definition = "".join(sense.find("definition").itertext())
        full_definition = full_definition + definition + " "

        notes_element = sense.find("notes")
        if notes_element is None:
            continue
        notes = "".join(notes_element.itertext())
        notes = "" if notes is None else notes
        full_definition = full_definition + notes
    return full_definition

def get_binyan(binyans):
    binyan_def = ""
    for binyan in binyans:
        # We check if either element is None or attribute is None
        # to avoid error
        name = binyan.find("binyan-name")
        form = binyan.find("binyan-form")
        if name is not None and name.text is not None:
            binyan_def = binyan_def + name.text + " "
        if form is not None and form.text is not None:
            binyan_def = binyan_def + form.text + " "

        binyan_def = binyan_def + def_from_senses(binyan.find("senses"))

    return binyan_def

if __name__ == "__main__":
    entries = root.findall(".//entry")
    num_entries = len(entries)
    for idx,entry in enumerate(entries):
        if idx%1000==0: print(f"{idx/num_entries*100:.2f}% done")
        rows.append(parse_entry(entry))

    df = pd.DataFrame(rows, columns=cols) 
    df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True)
    # Writing dataframe to csv 
    df.to_csv(f"{data_dir}/Jastrow-full.csv")
