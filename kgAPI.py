from fastapi import APIRouter
from pydantic import BaseModel
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
router = APIRouter()

class Question(BaseModel):
    question: str

@router.post('/llmAnswer')
def llmAns_api(question: Question):

  from find_similar import direct_answer
  print("直接利用大模型进行回答：")
  direct_response = direct_answer(question.question)
  print(direct_response)
  return dict(code=200, msg='ok', data=direct_response)


@router.post('/finetuneAnswer')
def finetuneAns_api(question: Question):
  question = question.question
  query_output,base_model = generate_query(question)
  unload_model(base_model)
  execute_output = execute_query(query_output)
  print(execute_output)
  print("通过微调大模型生成的cql执行的结果为：")
  execute_output_answer = [list(item.values())[0] for item in execute_output['answer']]
  if(len(execute_output_answer)==0):
    final_ans = "我不知道，请你采用其他技术!"
  else:
    final_ans = ','.join(execute_output_answer)
  print(final_ans)
  return dict(code=200, msg='ok', data=final_ans)


@router.post('/ragAnswer')
def ragAns_api(question: Question):
  question = question.question
  query_output,base_model = generate_query(question)
  unload_model(base_model)
  execute_output = execute_query(query_output)
  from find_similar import find_most_similar_entity,get_answer
  query_cypher_dict = {}
  query_cypher_dict[question] = execute_output['query']
  entity_candidate = mention2entity(query_cypher_dict)
  most_similar_entity = find_most_similar_entity(entity_candidate)
  _, entity = replace_entities(query_cypher_dict,most_similar_entity)
  print(entity)
  context = merge_lists(entity)
  print(context)
  print("rag的推理结果：")
  final_ans = get_answer(context)
  print(final_ans)
  return dict(code=200, msg='ok', data=final_ans)

