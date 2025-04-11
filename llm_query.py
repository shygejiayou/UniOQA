import os
from dataclasses import dataclass, field
from typing import Optional

import torch
import tyro
from accelerate import Accelerator
from datasets import load_dataset
from peft import  LoraConfig
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments,T5ForConditionalGeneration

from trl import SFTTrainer
from trl.import_utils import is_xpu_available
from trl.trainer import ConstantLengthDataset

# bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_quant_type="nf4",
#     bnb_4bit_compute_dtype=torch.bfloat16,
# )

def generate_query(input_text):
    base_model = AutoModelForCausalLM.from_pretrained(
            "/text2CQL/NL2CQL",
            
            load_in_8bit=True,
            torch_dtype=torch.float16,
            device_map={"": "cuda:0"},
            trust_remote_code=True
    )
    tokenizer = AutoTokenizer.from_pretrained("/text2CQL/NL2CQL", use_fast=False, trust_remote_code=True)
    
    input_ids = tokenizer(input_text, return_tensors="pt").to('cuda:0')

    output = base_model.generate(**input_ids,num_beams=10,max_new_tokens=200, repetition_penalty=1.1)
    output_cyp = tokenizer.decode(output.cpu()[0], skip_special_tokens=True).split("cypher:")[1][1:]
    print(output_cyp)
    return output_cyp,base_model