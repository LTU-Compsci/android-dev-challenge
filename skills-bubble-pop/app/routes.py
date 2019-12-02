from flask import Flask, render_template, request
from app import app
import json
import glob
import pandas as pd
import re
import os

""" this app is for demo purposes!
"""

# fetch data
path = os.path.join(app.root_path, r'static/data')
all_files = glob.glob(path + "/twitter/raw/tweets_120719/tweets_*.json")
li = []
with open(path + "/wordlists.json", encoding='utf-8', errors='ignore') as json_data:
    wordlists = json.load(json_data, strict=False)

for filename in all_files:
    with open(filename, encoding='utf-8', errors='ignore') as json_data:
        li = li + json.load(json_data, strict=False)

def get_keywords():
    """ get the keywords from the wordlists data
    """
    keywords = []
    for d in wordlists["skills"]:
        keywords.append(d["keyword"])
    return keywords

def get_data(keyword):
    """ gets the list of tools associated 
        with a given keyword from wordlists data
        TODO: avoid having to keep calling this
        (i.e. cache the data somewhere)
    """
    data = {"name": keyword, "children": []}
    for d in wordlists["skills"]:
        if d["keyword"] == keyword:
            tools_list = d["tools"]
    for word in tools_list:
        regex = r'\b[#|@|_]?{}[_]?\b'.format(word)
        count = 0
        for tweet in li:
            if re.search(regex, tweet, re.IGNORECASE):
                  count += 1
        if count > 0:
            data["children"].append({
                "name": word,
                "value": count,
                "symbol": gen_symbol(word),
                "tooltip": word.split("|")[0]})
    return data

def gen_symbol(word):
    """ generate a short symbol for a keyword
        TODO: make this less rubbish/work on dataset
    """
    if len(word) < 5:
        return word.upper()
    else:
        parts = word.split("|")
        shortest_part = min(parts, key=len)

        #return re.sub('[^A-Za-z0-9]+', '', word)[0:5].upper()
        if len(shortest_part) < 5:
            return shortest_part.upper()
        else:
            return shortest_part.upper()[0:4]

# --- ROUTES ---

@app.route('/')
def index():
    cat = request.args.get('cat') # TODO: use param to modify data
    if cat is None:
        cat = "languages"
    keywords = get_keywords()
    return render_template('index.html', keywords=keywords, cat=cat)

@app.route('/data')
def data():
    """
        the endpoint for the data
    """
    cat = request.args.get('cat') # TODO: use param to modify data
    if cat is None:
        cat = "languages"
    data = get_data(cat)
    return json.dumps(data)

@app.route('/training')
def training():
    urls = ["http://www.leedstrinity.ac.uk/courses/computer-science"]
    return render_template('training.html', urls=urls, tool="Java")

