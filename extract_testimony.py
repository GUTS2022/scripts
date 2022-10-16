# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 17:43:53 2022

@author: hbarr
"""
def extract_tests():
    with open("Data/student_statements.txt", "r") as txt:
        text = txt.read()
    text = text.split("\n")
    
    ids = []
    names = []
    tests = []
    for i in range(len(text)):
        if i%5 == 1:
            ids.append(text[i][16:])
        elif i%5 == 2:
            names.append(text[i][6:])
        elif i%5 == 3:
            tests.append(text[i][11:])
    
    out = {ids[i]: tests[i] for i in range(len(ids))}
    return out

if __name__ == "__main__":
    
    extract_tests()