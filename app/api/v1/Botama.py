import vertexai
import os
from vertexai.language_models import TextGenerationModel
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage/durable-boulder-407913-0a0904bf432a.json"

class Botama:
    @classmethod
    def predict(cls, prompt):
        
        vertexai.init(project="durable-boulder-407913", location="asia-southeast1")
        parameters = {
            "candidate_count": 1,
            "max_output_tokens": 2024,
            "temperature": 0, # 1 lebih creative, 0 presisi
            "top_p": 0.8,
            "top_k": 40
        }
        model = TextGenerationModel.from_pretrained("text-bison")
        text = "Nama kamu dalah Bot Chaser, kamu adalah asisten untuk membantu dalam percakapan pengguna mengenai pengetahuan berita hoax maupun aktual."
        prompt = text + prompt
        response = model.predict(
            prompt,
            **parameters
        )
        
        return response.text