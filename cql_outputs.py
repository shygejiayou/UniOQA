import json
import time

from neo4j import GraphDatabase

def execute_query(query, timeout_seconds=50):
    
    uri = "bolt://localhost:7687"  
    username = "neo4j"  
    password = "123456"  
    driver = GraphDatabase.driver(uri, auth=(username, password))
    li = []
    try:
        with driver.session() as session:
            with session.begin_transaction(timeout=timeout_seconds) as transaction:
                result = transaction.run(query)
                print(result)
                
                for record in result:
                    result_dict = {str(key): str(value) for key, value in record.items()}
                    li.append(result_dict)
                ans = {
                    "query": query,
                    "answer": li
                }
    except Exception as e:
        ans = {
            "query": query,
            "answer": []  
        }
    
    driver.close()
    return ans
