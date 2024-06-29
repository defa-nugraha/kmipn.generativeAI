from datetime import datetime
from helpers.Helpers import Helpers
from api.v1.Liputan6 import Liputan6
import os
import vertexai
from vertexai.language_models import TextGenerationModel
import json
import requests
import time

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage/durable-boulder-407913-0a0904bf432a.json"

class PredictionByScraping:
    @classmethod
    def scrapingAndPredict(cls, url, id_url):
        source = Helpers.find_domain_in_url(url)
        
        if source == "liputan6.com":
            liputan6 = Liputan6(url)
            dataScraping = liputan6.get_data()
            data = {
                "title": dataScraping["title"],
                "description": dataScraping["description"],
                "url": dataScraping["url"],
                "source": dataScraping["source"],
                "publish_date": dataScraping["publish_date"],
            }
            predict = PredictionByScraping.predict(data)
        
            cleaned_data_string = predict.strip().strip('`').strip()

            # Mengubah string JSON menjadi dictionary
            data_dict = json.loads(cleaned_data_string)
            
            # update ke database
            url_post = 'https://be-hoax-chaser.dzikrifaza.my.id/news/createOrUpdate'
            now = datetime.now()
            current_time = datetime.now().isoformat()
            data = {
                "id": id_url,
                "description": dataScraping['description'],
                "author": dataScraping['author'],
                "source": dataScraping['source'],
                "publish_date": dataScraping['publish_date'],
                "news_keywords": ", ".join(data_dict['news_keywords']),
                "is_training": True,
                "training_date": current_time,
                # "training_date": "2024-01-01 00:00:00",
                "label": data_dict['label'],
                # "location": ""
            }
            response = PredictionByScraping.post_news_data(url_post, json.dumps(data, default = str))
            print(response)
        else:
            data_dict = "source not found"        
        return data_dict
    
    @classmethod
    def predict(cls, data):
        prompt = f"""
            Saya ingin Anda menentukan apakah berita berikut adalah hoax atau bukan. Data berita ini adalah hasil scraping abaikan jika ada data yang tidak relevan. Berikut adalah informasi mengenai berita tersebut:

            1. **Judul Berita (Title)**: {data['title']}
            2. **Deskripsi (Description)**: {data['description']}
            3. **Link Berita (Link)**: {data['url']}
            4. **Sumber Berita (Source)**: {data['source']}
            5. **Waktu Publikasi (Timestamp)**: {data['publish_date']}

            Berdasarkan informasi di atas, tolong tentukan apakah berita ini adalah hoax atau bukan. Jawablah dengan ketentuan sebagai berikut:
            [
                label: tentukan berita ini sebagai hoax atau actual,
                news_keywords: berikan beberapa keyword yang relevan untuk berita ini,
            ]
            .
        """
        
        vertexai.init(project="durable-boulder-407913", location="asia-southeast1")
        parameters = {
            "candidate_count": 1,
            "max_output_tokens": 2024,
            "temperature": 0, # 1 lebih creative, 0 presisi
            "top_p": 0.8,
            "top_k": 40
        }
        model = TextGenerationModel.from_pretrained("text-bison")
        response = model.predict(
            prompt,
            **parameters
        )
        
        return response.text
    
    @classmethod
    def post_news_data(cls, url, data):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raises an error for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error posting data: {e}")
            return None