from fastapi import FastAPI
from pydantic import BaseModel
from api.v1.Prediction import Prediction

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "API GENERATIVE AI - HOAX CHASER"}

class PredictionRequest(BaseModel):
    title: str
    description: str
    link: str
    sumber: str
    timestamp: str

@app.post("/prediction")
async def prediction(request: PredictionRequest):
    prompt = request
    
    result = Prediction.predict(prompt)
    return {"status": 200, "data": {'hoax': result}}

class PredictionScrappingRequest(BaseModel):
    url: str
    id_url: str
    
@app.post("/prediction/scraping")
async def prediction(request: PredictionScrappingRequest):
    prompt = request
    
    # result = Prediction.predict(prompt)
    return {"status": "success", "code": 200}