import re
import json



def extract_entities(text, replace):
    pattern = r"ENTITY{name:'(.*?)'}" 
    entities = re.findall(pattern, text) 

    replaced_text = text
    for i, entity in enumerate(entities):
        if i < len(replace):
            replaced_text = replaced_text.replace(":ENTITY{" + f"name:'{entity}'", ":ENTITY{" + f"name:'{replace[i]}'")
    return replaced_text


def replace_entities(data_cy,data_near):
    ans = {}
    entity = {}
    for query, cypher in data_cy.items():
        replace = []
        if cypher == []:
            ans[query] = []
            continue
        for mention_and_entities in data_near[query]:
            if mention_and_entities["entities"] != []:
                replace.append(*mention_and_entities["entities"])
            else:
                continue


        new_sentence = extract_entities(cypher, replace=replace)
        pattern = r"ENTITY{name:'(.*?)'}" 
        entities = re.findall(pattern, new_sentence) 
        entity[query] = entities
        
        ans[query] = new_sentence
       
        print("替换后的cql语句为：")
        print(new_sentence)
        return ans,entity

