from datetime import datetime
from helpers.Helpers import Helpers
from api.v1.scraping.Liputan6 import Liputan6
from api.v1.scraping.Kominfo import Kominfo
from api.v1.GetDetailNewsByGenAI import GetDetailNewsByGenAI
import os
import vertexai
from vertexai.language_models import TextGenerationModel
import json
import requests

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage/durable-boulder-407913-0a0904bf432a.json"

class PredictionByScraping:
    @classmethod
    def scrapingAndPredict(cls, url, id_url):
        source = Helpers.find_domain_in_url(url)
        
        if source == "liputan6.com":
            liputan6 = Liputan6(url)
            dataScraping = liputan6.get_data()
        elif source == "kominfo.go.id":
            kominfo = Kominfo(url)
            dataScraping = kominfo.get_data()
        else:
            return GetDetailNewsByGenAI.scrape_dynamic(url, id_url)
        
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
        data_dict = json.loads(Helpers.fix_json_format(cleaned_data_string))    
        
        # update ke database
        url_post = 'https://be-hoax-chaser.dzikrifaza.my.id/news/updateWithUrlRequest'
        current_time = datetime.now().isoformat()
        publish_date = str(dataScraping['publish_date'])
        dataPost = {
            "urlRequestId": id_url,
            "title": dataScraping['title'],
            "description": dataScraping['description'],
            "author": dataScraping['author'],
            "source": dataScraping['source'],
            "newsKeywords": ", ".join(data_dict['news_keywords']),
            "isTraining": 1,
            "trainingDate": current_time,
            "publishDate": publish_date,
            "label": data_dict['label'],
            "url": url,
            "ambigousKeywords": data_dict['ambigousKeywords']
            # "location": ""
        }
        print(f'datapost: {dataPost}')
        response = PredictionByScraping.post_news_data(url_post, json.dumps(dataPost))
        # print(data)            
        return response
    
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
                ambigousKeywords: berikan kata-kata ambigu yang terdapat pada berita ini jika tidak ada kirim tidak ada,
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
        }

        try:
            # response = requests.post(url, json=data, headers=headers)
            response = requests.request("POST", url, headers=headers, data=data)
            # print(response.text)
            response.raise_for_status() 
            print(response.text)
            return response.json() 
        except requests.exceptions.RequestException as e:
            print(f"Error posting data: {e}")
            return None