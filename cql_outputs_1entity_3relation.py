import json
import time

from neo4j import GraphDatabase


uri = "bolt://localhost:7687"  
username = "neo4j" 
password = "123456"  
driver = GraphDatabase.driver(uri, auth=(username, password))
def query_correct_cql(cypher_queries):
    for key, value in cypher_queries.items():
        temp = []
        for item in value:
            li = []
            try:
                with driver.session() as session:
                    with session.begin_transaction(timeout=50) as transaction:
                        result = transaction.run(item)
                        
                        for record in result:
                            result_dict = {str(key): str(value) for key, value in record.items()}
                            li.append(result_dict)
            except Exception as e:
                print(f"Error executing query: {value}")
                print(f"Error message: {str(e)}")
            finally:
                temp.append(li)
        ans = {
            "query": key,
            "answer": temp
        }
        return ans
driver.close()