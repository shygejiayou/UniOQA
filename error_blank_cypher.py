import json

with open('baichuan_60training/cql_results.json', 'r', encoding='utf-8') as file:
    data = json.load(file) 
query_cypher_dict = {}

with open('baichuan_60training/baichuan_60.json', 'r', encoding='utf-8') as file:
    data2 = json.load(file) 

for item1, item2 in zip(data, data2):
    query = item1.get('query')
    cypher = item2.get('cypher')
    answer = item1.get('answer')
    
    if len(answer)==0:
        query_cypher_dict[query] = cypher

with open('baichuan_60training/error_blank_cypher.json', 'w', encoding='utf-8') as json_file:
    json.dump(query_cypher_dict, json_file, ensure_ascii=False, indent=2)