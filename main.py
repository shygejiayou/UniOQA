
from cql_outputs import execute_query
from mention_to_entity import mention2entity
from replace_entities import replace_entities
from rag.get_context_from_entity import KgAnswer,merge_lists
from mention_to_relation import query_relationships
from replace_relationships import replace
from cql_outputs_1entity_3relation import query_correct_cql
from llm_query import generate_query
import torch

def unload_model(model):
    del model
    torch.cuda.empty_cache()

if __name__ == '__main__':
    input = input("请输入问题：")

    query_output,base_model = generate_query(input)
    unload_model(base_model)
    execute_output = execute_query(query_output)
    print(execute_output)
    print("通过微调大模型生成的cql执行的结果为：")
    execute_output_answer = [list(item.values())[0] for item in execute_output['answer']]
    print(execute_output_answer)

    from find_similar import find_most_similar_entity,find_similar_relationships,get_answer,direct_answer,find_similar_context

    print("直接利用大模型进行回答：")
    direct_response = direct_answer(input)
    print(direct_response)
    query_cypher_dict = {}
    query_cypher_dict[input] = execute_output['query']
    entity_candidate = mention2entity(query_cypher_dict)
    most_similar_entity = find_most_similar_entity(entity_candidate)
    print(most_similar_entity)
    replace_cql,entity = replace_entities(query_cypher_dict,most_similar_entity)
    print(replace_cql)
    relation_candidate= query_relationships(replace_cql)
    print("实体的一跳关系为：")
    print(relation_candidate)
    similar_relationships,model = find_similar_relationships(relation_candidate)
    print("最相近的top3个关系：")
    print(similar_relationships)
    unload_model(model)
    correct_cql = replace(replace_cql,similar_relationships)
    print("纠正后的cql：")
    print(correct_cql)
    correct_cql_outputs = query_correct_cql(correct_cql)
    print("进行实体关系纠正后的cql执行结果为：")
    correct_cql_outputs_ans = [list(item.values())[0] for sublist in correct_cql_outputs['answer'] for item in sublist]
    print(correct_cql_outputs_ans)
    print(entity)
    context = merge_lists(entity)
    print(context)
    print("rag的推理结果：")
    response = get_answer(context)
    print(response)
