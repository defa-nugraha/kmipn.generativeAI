import os
import vertexai
from vertexai.language_models import TextGenerationModel

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage/durable-boulder-407913-0a0904bf432a.json"

class Prediction:
    @classmethod
    def predict(cls, data):
        prompt = f"""
            Saya ingin Anda menentukan apakah berita berikut adalah hoax atau bukan. Berikut adalah informasi mengenai berita tersebut:

            1. **Judul Berita (Title)**: {data.title}
            2. **Deskripsi (Description)**: {data.description}
            3. **Link Berita (Link)**: {data.link}
            4. **Sumber Berita (Source)**: {data.sumber}
            5. **Waktu Publikasi (Timestamp)**: {data.timestamp}

            Berdasarkan informasi di atas, tolong tentukan apakah berita ini adalah hoax atau bukan. Jawablah dengan True atau False.
        """
        
        vertexai.init(project="durable-boulder-407913", location="asia-southeast1")
        parameters = {
            "candidate_count": 1,
            "max_output_tokens": 2024,
            "temperature": 0.2, # 1 lebih creative, 0 presisi
            "top_p": 0.8,
            "top_k": 40
        }
        model = TextGenerationModel.from_pretrained("text-bison")
        response = model.predict(
            prompt,
            **parameters
        )
        
        return response.text
 
 
        
    