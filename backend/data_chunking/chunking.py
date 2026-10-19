import os
import json
# 
from langchain_text_splitters import RecursiveCharacterTextSplitter

PATH_TO_FILE = r""
DATA_DIR = r""

text_to_split = ""

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 100,
    chunk_overlap = 20
)

with open(PATH_TO_FILE, "r", encoding="utf-8") as f:
    # if it is json
    text_to_split = json.load(f)["full_text"]

    # if it is txt
    # text_to_split = f.read()

text = text_splitter.split_text(text_to_split)
data = {"info": []}

for info in text:
    data["info"].append(info)

with open(DATA_DIR, "a", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)