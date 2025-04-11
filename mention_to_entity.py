import time
import requests
import json
import re


def extract_entities(text):
    pattern = r"ENTITY{name:'(.*?)'}"  
    entities = re.findall(pattern, text)  
    return entities


url = 'https://api.ownthink.com/kg/ambiguous'



def mention2entity(cypher_queries):
    query_entities = {}
    for key, value in cypher_queries.items():
        if value == []:
            query_entities[key] = []
            continue
        entities = extract_entities(value)
        mention_to_entity = {}
        templist = []
        for item in entities:
            params = {'mention': item}
            time.sleep(1)
            response = requests.get(url, params=params)
            json_data = response.json()
            if response.status_code == 200:
                mention_to_entity = {
                    "mention": item,
                    "entities": [el[0] for el in json_data['data']]
                }
            templist.append(mention_to_entity)
        query_entities[key] = templist
        print("{} 的实体提及片段转换为知识图谱的实体为：".format(key), templist)
        return query_entities


