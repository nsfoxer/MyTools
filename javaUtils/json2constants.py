#!/bin/python
import json

def display(a: str, depth: int):
    if len(a) == 0:
        return
    s = "\t"*depth + "private String "
    for c in a:
        if c.isupper():
            s += "_"
        s += c.upper()
    print(s+";")

def parse(d:dict, depth:int):
    for a in d:
        if type(d[a]) == dict:
            s = "\t"*depth
            print(f"{s}interface {a} {{")
            parse(d[a], depth+1)
            print(f"{s}}}")
        else:
            display(a, depth)


with open("./1.json", "r") as f:
    data = f.read()
    d = json.loads(data)
    parse(d, 0)
