from fastapi import FastAPI
from pydantic import BaseModel
from api.v1.Prediction import Prediction
from api.v1.PredictionByScraping import PredictionByScraping
from api.v1.Botama import Botama
from api.v1.PredictionByVideo import PredictionByVideo

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
    try:
        result = PredictionByScraping.scrapingAndPredict(prompt.url, prompt.id_url)
        if result == "source not found":
            return {"status": "failed", "code": 404, "message": "source not found"}
        return {"status": "success", "code": 200, "data": result}
    except Exception as e:
        print(e)
        return {"status": "failed", "code": 500, "message": "internal server error"}
    
    
class BotamaRequest(BaseModel):
    prompt: str
    
@app.post("/botama")
async def prediction(request: BotamaRequest):
    prompt = request
    # result = prompt.url
    try:
        result = Botama.predict(prompt.prompt)
        if result == "source not found":
            return {"status": "failed", "code": 404, "message": "source not found"}
        return {"status": "success", "code": 200, "data": result}
    except Exception as e:
        print(e)
        return {"status": "failed", "code": 500, "message": "internal server error"}
    
    
# GET BY VIDEO
class PredictionByVideoRequest(BaseModel):
    url: str
    userId: str
    
@app.post("/prediction/video")
async def prediction(request: PredictionByVideoRequest):
    prompt = request
    # result = prompt.url
    try:
        result = PredictionByVideo.analysisVideo(prompt.url, prompt.userId)
        return {"status": "success", "code": 200, "data": result}
    except Exception as e:
        print(e)
        return {"status": "success", "code": 200}