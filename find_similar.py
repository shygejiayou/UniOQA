import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import json
device = "cuda:1"

tokenizer = AutoTokenizer.from_pretrained("/text2CQL/ZhipuAI/glm-4-9b-chat-1m",trust_remote_code=True)


model = AutoModelForCausalLM.from_pretrained(
    "/text2CQL/ZhipuAI/glm-4-9b-chat-1m",
    torch_dtype=torch.bfloat16,
    device_map={"": "cuda:1"},
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to(device).eval()



def find_most_similar_entity(cypher_queries):
    query_entity_nearest = {}
    for index, (key, value) in enumerate(cypher_queries.items()):
        tempList = []
        mention_to_entity = {}
        print(key, value)
        for item in value:
            if item['entities'] == [] or len(item['entities'])==1:
                mention_to_entity = {
                    "mention": item['mention'],
                    "entities": item['entities']
                }
            else:
                query = "给定查询：{} 和列表：{}，从列表中选择与查询最相关的词，仅返回所选词，除此之外不生成任何其他内容。".format(key, item['entities'])
                inputs = tokenizer.apply_chat_template([{"role": "user", "content": query}],
                                        add_generation_prompt=True,
                                        tokenize=True,
                                        return_tensors="pt",
                                        return_dict=True
                                        )

                inputs = inputs.to(device)
                gen_kwargs = {"max_length": 2500, "do_sample": True, "top_k": 1}
                with torch.no_grad():
                    outputs = model.generate(**inputs, **gen_kwargs)
                    outputs = outputs[:, inputs['input_ids'].shape[1]:]
                    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    print(response)
                    mention_to_entity = {
                            "mention": item['mention'],
                            "entities": [str(response.replace('\n', ''))]
                            }
            tempList.append(mention_to_entity)
        query_entity_nearest[key] = tempList
        return query_entity_nearest
    


def find_similar_relationships(cypher_queries):
    query_relationships_nearest = {}
    for index, (key, value) in enumerate(cypher_queries.items()):
        tempList = []
        mention_to_relationships = {}
        print(key, value)
        for item in value:
            if item['relationships'] == [] or len(item['relationships'])<=3:
                mention_to_relationships = {
                    "mention": item['mention'],
                    "relationships": item['relationships']
                }
            else:
                query ="你是一个识别语义相似度的专家，给你一个query：{},给你一系列词：{}，你从这些词中选三个和query语义最相关的，只返回你从这里面选的三个词，不要生成任何其他的话！不要回答query！比如query是'似乎有个日本军优叫乙夜，他是干哪行的'，一系列词list为['描述', '歧义关系', '中文名称', '身份', '职业'],那么你的返回值只能是这里面的三个词".format(key,item['relationships'])
                inputs = tokenizer.apply_chat_template([{"role": "user", "content": query}],
                                        add_generation_prompt=True,
                                        tokenize=True,
                                        return_tensors="pt",
                                        return_dict=True
                                        )

                inputs = inputs.to(device)
                gen_kwargs = {"max_length": 4000, "do_sample": True, "top_k": 1}
                with torch.no_grad():
                    outputs = model.generate(**inputs, **gen_kwargs)
                    outputs = outputs[:, inputs['input_ids'].shape[1]:]
                    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    print(response)
                mention_to_relationships = {
                "mention": item['mention'],
                "relationships": response.replace('\n','').split(',')
                }
            tempList.append(mention_to_relationships)
        query_relationships_nearest[key] = tempList
        print(query_relationships_nearest)
        return query_relationships_nearest,model



def get_answer(entity_queries):
    for key, value in entity_queries.items():
        query = key
        context = '。'.join(value)
        template = """基于以下已知信息，直接回答用户的问题，不要输出多余的内容。
                                如果无法从中得到答案，请回答 "[]"，不允许在答案中添加编造成分，答案请使用中文。
                                已知内容:
                                {context}
                                问题:
                                {question}
                                """
        inputs = tokenizer.apply_chat_template([{"role": "user", "content": template.format(context=context,question=query)}],
                                            add_generation_prompt=True,
                                            tokenize=True,
                                            return_tensors="pt",
                                            return_dict=True
                                            )

        inputs = inputs.to(device)
        gen_kwargs = {"max_length": 20000, "do_sample": True, "top_k": 1}
        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_kwargs)
            outputs = outputs[:, inputs['input_ids'].shape[1]:]
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response


def direct_answer(question):
    inputs = tokenizer.apply_chat_template([{"role": "user", "content": question}],
                                        add_generation_prompt=True,
                                        tokenize=True,
                                        return_tensors="pt",
                                        return_dict=True
                                        )

    inputs = inputs.to(device)
    gen_kwargs = {"max_length": 2500, "do_sample": True, "top_k": 1}
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response


def find_similar_context(question,context):
    bg = """"
- Role: 关系匹配与排序专家
- Background: 用户需要对一系列三元组数据按照关系匹配的分数进行排序。
- Profile: 你是一位专注于数据排序的专家，擅长分析关系匹配并据此进行排序。
- Skills: 数据分析、关系识别、排序算法、分数计算。
- Goals: 设计一个流程，对输入的三元组数据按照关系的匹配分数进行排序，并返回排序结果。
- Constrains: 确保排序过程公正、准确，并且可以处理大量数据。
- OutputFormat: 返回一个排序后的三元组列表。
- Workflow:
  1. 解析输入的三元组列表，提取每个三元组的关系。
  2. 为每个三元组计算关系匹配分数。
  3. 根据匹配分数对所有三元组进行排序。
  4. 返回排序后的三元组列表。
"""
    query ="给你一个问题：{},给你一个列表：{}，按照Workflow进行工作,返回排序后的三元组列表，不要回答问题".format(question,context)
    inputs = tokenizer.apply_chat_template([{"role": "user", "content": bg + query}],
                            add_generation_prompt=True,
                            tokenize=True,
                            return_tensors="pt",
                            return_dict=True
                            )

    inputs = inputs.to(device)
    gen_kwargs = {"max_length": 8000, "do_sample": True, "top_k": 1}
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
