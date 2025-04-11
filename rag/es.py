#总行数：108460779 
import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

id_num = 0
def deployES(input_file, host, port):
    """ put triples into es
        input: input_file, host, port
        output: None
    """
    print("Processing:" + input_file)
    global id_num  
    f = open(input_file, 'r', encoding='utf-8')
    es_dir = ":".join((host, port))
    print("es_dir:", es_dir)
    es = Elasticsearch([es_dir])
    es.indices.create(index='kbqa-data', ignore=[400, 404])
    lines = []
    while True:
        line = f.readline()
        id_num += 1
        if line == "":
            break
        line = line.split(",")
        action = {
            "_index": "kbqa-data",
            "_type": "kbList",
            "_id": id_num, 
            "_source": {
                "entity": line[0],
                "relation": line[1],
                "value": line[2].strip(),
                }}
        lines.append(action)
        if id_num % 5000 == 0:
            bulk(es, lines, index="kbqa-data", raise_on_error=True)
            lines = []
        if id_num % 50000 == 0:
            print(id_num, " triples has been deployed")
    bulk(es, lines, index="kbqa-data", raise_on_error=True)
    print(id_num, " triples has been deployed")
    f.close()
if __name__ == "__main__":
    
    host = "127.0.0.1"
    port = "9200"
    folder_path = "/text2CQL/cql/processed_output_text_files"
    for file_name in os.listdir(folder_path):
        print(os.listdir(folder_path))
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            deployES(file_path, host, port)