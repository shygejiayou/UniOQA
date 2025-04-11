import re
import json

import numpy as np

np.seterr(divide='ignore', invalid='ignore')


def extract_relationship(cyp):
    pattern = r"Relationship{name:'(.*?)'}"  
    relas = re.findall(pattern, cyp)  

    return relas


def replace_relationship(text, replace, size):
    if replace == [] or replace[0] == []:
        return [text]
    pattern = r"Relationship{name:'(.*?)'}"  
    relas = re.findall(pattern, text)  

    repalced_text = text
    ans = []

    for ress in replace:
        for j in ress:
            for i, relation in enumerate(relas):
                if i < size:
                    ans.append(repalced_text.replace(":Relationship{" + f"name:'{relation}'",
                                                     ":Relationship{" + f"name:'{j}'"))

    return ans


def replace(data,relationships_candidate):
    ans = {}
    replace_rela = [] 
    for question, an in relationships_candidate.items():
        cql_sentence = data[question] 
        if an == []:
            ans[question] = []
            continue

        relationship = extract_relationship(cql_sentence)  
        res = []
        if(len(relationship) == 0):
           ans[question] == cql_sentence
           return ans
        for i in range(len(relationship)):
            if i > len(data[question]): continue
            try:
                simi_relation = relationships_candidate[question][i]['relationships']
            except IndexError:
                continue
            replace_rela.append(simi_relation) 
            res = replace_relationship(cql_sentence, replace_rela, len(relationships_candidate[question]))  # 替换
            ans[question] = res
    return ans

