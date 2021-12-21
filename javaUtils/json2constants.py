#!/bin/python
import json

def display(a: str):
    if len(a) == 0:
        return
    s = "private String "
    for c in a:
        if c.isupper():
            s += "_"
        s += c.upper()
    print(s+";")
    


def parse(d:dict):
    for a in d:
        display(a)
        if type(d[a]) == dict:
            parse(d[a])


with open("./1.json", "r") as f:
    data = f.read()
    d = json.loads(data)
    parse(d)
