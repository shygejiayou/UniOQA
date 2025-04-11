
from fastapi import FastAPI
from kgAPI import router as kgAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           
    allow_credentials=True,           
    allow_methods=["*"],              
    allow_headers=["*"],              
)
app.include_router(
  kgAPI,
  prefix='/llm/api'
)
