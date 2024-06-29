from fastapi import FastAPI
from pydantic import BaseModel
from api.v1.Prediction import Prediction
from api.v1.PredictionByScraping import PredictionByScraping

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
    # result = prompt.url
    result = PredictionByScraping.scrapingAndPredict(prompt.url, prompt.id_url)
    if result == "source not found":
        return {"status": "failed", "code": 404, "message": "source not found"}
    return {"status": "success", "code": 200, "data": result}