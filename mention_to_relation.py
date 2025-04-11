import json
import re

from neo4j import GraphDatabase

uri = "bolt://localhost:7687" 
username = "neo4j" 
password = "123456" 

driver = GraphDatabase.driver(uri, auth=(username, password))


def extract_entities(text):
    pattern = r"ENTITY{name:'(.*?)'}"  
    entities = re.findall(pattern, text)  
    return entities


def execute_query(query, timeout_seconds=50):
    try:
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                with session.begin_transaction(timeout=timeout_seconds) as transaction:
                    result = transaction.run(query)
                    li = []
                    
                    for record in result:
                        result_dict = {str(key): str(value) for key, value in record.items()}
                        li.append(result_dict)
                    extracted_values = [eval(d['relation_names']) for d in li]
                    
                    unique_values = set(value for sublist in extracted_values for value in sublist)
                   
                    result_list = list(unique_values)
                    return result_list
    except Exception as e:
        return []

def query_entity_skip_relationships(entity):
    cql_query1 = "MATCH (n:ENTITY{name:'" + entity + "'})-[r*1..1]->(m) RETURN [rel in r | rel.name] AS relation_names"
    cql_query2 = "MATCH (n:ENTITY{name:'" + entity + "'})<-[r*1..1]-(m) RETURN [rel in r | rel.name] AS relation_names"

    query1 = execute_query(cql_query1)
    query2 = execute_query(cql_query2)
    result = query1 + query2
    return list(set(result))

def query_relationships(cypher_queries):
    query_relationships = {}
    for key, value in cypher_queries.items():
        if value == []:
            query_relationships[key] = []
            continue
        entities = extract_entities(value)
        mention_to_entity = {}
        templist = []
        for item in entities:
            mention_to_entity = {
                "mention": item,
                "relationships": query_entity_skip_relationships(item)
            }
            templist.append(mention_to_entity)
        query_relationships[key] = templist
        return query_relationships

