"""
Converts data\\Klein-FullDictionary.xml (xml) into csv.
To change the file, change the filePath and data_dir below:
"""
import xml.etree.ElementTree as XeT
import pandas as pd
import os
import re

fileName = "Klein-FullDictionary.xml"
data_dir = os.path.dirname(__file__) + '/../data'
filePath = f"{data_dir}/{fileName}"

cols = ["Entry", "Definition", "Has_Greek"]
rows = []
xmlparse = XeT.parse(filePath)
root = xmlparse.getroot()

def parse_entry(entry):
    # Get head-word of entry
    head_word = " ".join(word.text for word in entry.findall("head-word") if word.text is not None)
    # If a word has binyans, the definition is inside the binyan
    binyans = entry.findall("binyan")
  
    senses = entry.find("senses") # Is the parent containing senses
    
    # If the only senses are in the binyan, don't search through senses
    if senses is None:
        if len(binyans)>0:
               senses = []
        else:
            raise Exception(f"No senses nor binyans for {entry.atrrib}")

    full_definition = def_from_senses(senses)
    
    # If there is only 1 sense, the langauge-key will appear outside of the sense
    # This checks if there is a language-key for the entire entry and not individual senses.
    language_key = getattr(entry.find("language-key"), "text", "").strip()
    if language_key:
        full_definition = full_definition + language_key + " "
    
    
    notes_element = entry.find("notes")
    if notes_element is not None:
        notes = "".join(notes_element.itertext())
        notes = "" if notes is None else notes.strip()
        full_definition = full_definition + notes
    
    binyan_def = ""
    if len(binyans)>0:
        binyan_def = get_binyan(binyans)
    full_definition = full_definition + binyan_def

    has_greek = "Greek" in full_definition or "Gk." in full_definition

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
        if len(number)>0:
            full_definition = full_definition +") "

        definition = "".join(sense.find("definition").itertext()).strip()
        full_definition = full_definition + definition + " "
        
        language_key = getattr(sense.find("language-key"), "text", "").strip()
        if language_key:
            full_definition = full_definition + language_key + " "

    return full_definition

def get_binyan(binyans):
    binyan_def = " | "
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

    if binyan_def == " | ": # if no binyan info is added
        return ""
    
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
    df.to_csv(f"{data_dir}/Klein-full.csv")
