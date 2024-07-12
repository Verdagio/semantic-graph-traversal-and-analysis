# main.py
import os
from app.lib.encoders import EmbModelName
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.analyser import Analyser

app = FastAPI()

class Config_Model_Request_Params(BaseModel):
    depreciation: float
    min_score_threshold: float
    # system_prompt: str
    default_prompt: str
    embedding_model: EmbModelName
    embedding_model_variant: Optional[str] = ''
    llm_name: Optional[str] = ''

class Traversal_Request_Params(BaseModel):
    graph_data: dict
    start_vertex_id: str
    context: str

analyser = Analyser(
    embedding_model_name=str(os.getenv('EMBEDDING_MODEL_NAME')),
    embedding_model_variant=str(os.getenv('EMBEDDING_MODEL_VARIANT')),
    llm_name=str(os.getenv('LLM_NAME'))
)

@app.post("/api/v1/set_config_params/")
async def set_config_params(params: Config_Model_Request_Params):
    try:
        if params.depreciation is not None and params.min_score_threshold is not None:
            analyser.set_traversal_params(params.depreciation, params.min_score_threshold)
        # if params.system_prompt is not None: # TODO
        #     analyser.set_system_prompt(params.system_prompt)
        if params.default_prompt is not None:
            analyser.set_default_prompt(params.default_prompt)
        if params.embedding_model is not None:
            analyser.set_embedding_model(params.embedding_model, params.embedding_model_variant)
        if params.llm_name is not None:
            analyser.set_llm(params.llm_name)
        return {"message": f'Configuration parameters applied successfully: {analyser.get_current_config()}'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/api/v1/get_current_config/")
async def get_current_config():
    try:
        config = analyser.get_current_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/get_traversal_history/")
async def get_traversal_history():
    try:
        history = analyser.get_traversal_history()
        return {"traversal_history": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/api/v1/analyse/")
async def analyze(params: Traversal_Request_Params):
    try:
        return analyser.analyse(params.graph_data, params.start_vertex_id, params.context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/traverse/")
async def analyze(params: Traversal_Request_Params):
    try:
        return analyser.traverse(params.graph_data, params.start_vertex_id, params.context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
