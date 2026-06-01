# main.py
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
class CodeRequest(BaseModel):
 code: str
@app.post('/visualize')
def visualize(req: CodeRequest):
 return {'events': []}
