import json

from elasticsearch import Elasticsearch
class KgAnswer(object):
    def __init__(self, es_host, es_port):
        # init the model we need to use
        self.es = Elasticsearch([":".join((es_host, es_port))])

    def answer(self, input):
        query1 = {
            "query":{
                "match": {
                    "entity": input
                }
            }

        }
        query2 = {
            "query":{
                "match": {
                    "value": input
                }
            }
        }
        ans = []
        es_results1 = self.es.search(index="kbqa-data", body=query1, size=20)
        es_results2 = self.es.search(index="kbqa-data", body=query2, size=20)

        for i in range(len(es_results1['hits']['hits'])):
            entity = es_results1['hits']['hits'][i]['_source']['entity']
            relation = es_results1['hits']['hits'][i]['_source']['relation']
            value = es_results1['hits']['hits'][i]['_source']['value']
            answer_triple = entity + " " + relation + " " + value
            ans.append(answer_triple)
            if entity:
                query = {
                    "query":{
                        "term": {
                            "entity.keyword": entity
                        }
                    }

                }
                es_results = self.es.search(index="kbqa-data", body=query, size=20)
                for i in range(len(es_results['hits']['hits'])):
                    entity = es_results['hits']['hits'][i]['_source']['entity']
                    relation = es_results['hits']['hits'][i]['_source']['relation']
                    value = es_results['hits']['hits'][i]['_source']['value']
                    answer_triple = entity + " " + relation + " " + value
                    ans.append(answer_triple)
        for i in range(len(es_results2['hits']['hits'])):
            entity = es_results2['hits']['hits'][i]['_source']['entity']
            relation = es_results2['hits']['hits'][i]['_source']['relation']
            value = es_results2['hits']['hits'][i]['_source']['value']
            answer_triple = entity + " " + relation + " " + value
            ans.append(answer_triple)
            if entity:
                query = {
                    "query":{
                        "term": {
                            "entity.keyword": entity
                        }
                    }
                }
                es_results = self.es.search(index="kbqa-data", body=query, size=20)
                for i in range(len(es_results['hits']['hits'])):
                    entity = es_results['hits']['hits'][i]['_source']['entity']
                    relation = es_results['hits']['hits'][i]['_source']['relation']
                    value = es_results['hits']['hits'][i]['_source']['value']
                    answer_triple = entity + " " + relation + " " + value
                    ans.append(answer_triple)
        unique_list = []
        [unique_list.append(x) for x in ans if x not in unique_list]
        return unique_list

es_host = "127.0.0.1"
es_port = "9200"
kg = KgAnswer(es_host, es_port)


def merge_lists(json_data):
    res = {}
    for key, values in json_data.items():
        merged_list = []
        for value in values:
            result = kg.answer(value)
            merged_list.extend(result)
        res[key] = merged_list
    return res





