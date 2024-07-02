import requests
from bs4 import BeautifulSoup
import os
import vertexai
from vertexai.language_models import TextGenerationModel
from helpers.Helpers import Helpers
from datetime import datetime
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/storage/durable-boulder-407913-0a0904bf432a.json"

class GetDetailNewsByGenAI:
    @classmethod
    def scrape_dynamic(cls, url, id_url):
        news_data = {
            "title": "",
            "description": "",
            "author": "kominfo",
            "source": "kominfo",
            "publish_date": "",
            "url": url
        }
        
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        
        potential_classes = [
            'article', 'post', 'content', 'entry', 'news', 'story', 'blog-post', 'main-content', 'container'
            'post-content', 'article-content', 'entry-content', 'body-content', 'title', 'headline',
            'post-title', 'article-title', 'entry-title', 'story-title', 'news-title', 'page-title',
            'heading', 'news-headline', 'author', 'byline', 'post-author', 'article-author', 'entry-author',
            'writer', 'reporter', 'contributor', 'author-name', 'author-info', 'date', 'published-date',
            'post-date', 'article-date', 'entry-date', 'date-posted', 'date-published', 'pub-date',
            'timestamp', 'publish-time', 'image', 'post-image', 'article-image', 'entry-image',
            'thumbnail', 'featured-image', 'image-wrapper', 'news-image', 'img-responsive', 'img-thumbnail',
            'summary', 'excerpt', 'post-summary', 'article-summary', 'entry-summary', 'story-summary',
            'news-summary', 'intro', 'lead', 'description', 'category', 'tag', 'post-category', 'article-category',
            'entry-category', 'news-category', 'post-tag', 'article-tag', 'entry-tag', 'news-tag', 'breadcrumb',
            'breadcrumbs', 'nav', 'navigation', 'post-nav', 'article-nav', 'entry-nav', 'news-nav', 'breadcrumb-item',
            'breadcrumbs-list', 'comments', 'comment', 'post-comments', 'article-comments', 'entry-comments',
            'discussion', 'replies', 'feedback', 'comment-section', 'comment-list', 'social', 'share', 'social-share',
            'share-buttons', 'social-links', 'post-share', 'article-share', 'entry-share', 'share-icons', 'share-tools'
        ]

        # Mencari elemen berdasarkan beberapa kemungkinan umum
        title = soup.find(["h1", "h2", "title"])
        date = soup.find(["time", "span", "div"], class_="date detail__date")
        content = soup.find_all(["p", "div"], class_='container')
        
        if title:
            news_data["title"] = title.text.strip()
        
        if date:
            news_data["publish_date"] = date.text.strip()
        
        if content:
            cleaned_text = ' '.join([elem.text.strip() for elem in content])
            news_data["description"] = cleaned_text
        
        # Print or return the scraped data
        prediction_result = GetDetailNewsByGenAI.predict(cls, news_data['description'])
        print(prediction_result)
        cleaned_data_string = prediction_result.strip().strip('`').strip()

        # Mengubah string JSON menjadi dictionary
        data_dict = json.loads(cleaned_data_string)
        try:
            data_dict[0]['source'] =  Helpers.get_domain_name(url)
        
            req = GetDetailNewsByGenAI.post_news_data(url, id_url, data_dict[0])
        except Exception as e:
            data_dict['source'] =  Helpers.get_domain_name(url)
        
            req = GetDetailNewsByGenAI.post_news_data(url, id_url, data_dict)
        print(type(data_dict))
        return req
    
    @classmethod
    def predict(cls, data, url):
        prompt = f"""
            Saya ingin Anda menentukan apakah berita berikut adalah hoax atau bukan. Data berita ini adalah hasil scraping abaikan jika ada data yang tidak relevan. Berikut adalah hasil scraping tersebut:
            url berita: {url}

            data scraping:
            {data}

            Berdasarkan informasi di atas, tolong tentukan apakah berita ini adalah hoax atau bukan. Jawablah dengan ketentuan sebagai berikut:
            [
                label: tentukan berita ini sebagai hoax atau actual,
                news_keywords: berikan beberapa keyword yang relevan untuk berita ini,
                publish_date: berikan tanggal publikasi berita sesuai dari scraping di atas dan format yyyy-mm-dd,
                title: berikan judul berita sesuai dari scraping di atas,
                description: berikan deskripsi berita sesuai dari scraping di atas,
                author: berikan penulis berita sesuai dari scraping di atas,
                ambigousKeywords: berikan kata-kata ambigu yang terdapat pada berita ini jika tidak ada kirim tidak ada
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
    def post_news_data(cls, url, id_url, body):
        headers = {
            'Content-Type': 'application/json',
        }

        try:
            current_time = datetime.now().isoformat()
            publish_date = str(body['publish_date'])
            print(body)
            dataPost = {
                "urlRequestId": id_url,
                "title": body.get('title', 'tidak ada'),
                "description": body.get('description', 'tidak ada'),
                "author": body.get('author', 'tidak ada'),
                "source": body.get('source', 'tidak ada'),
                "newsKeywords": ", ".join(body.get('news_keywords', 'tidak ada')),
                "isTraining": 1,
                "trainingDate": current_time,
                "publishDate": publish_date,
                "label": body.get('label', 'tidak ada'),
                "url": url,
                "ambigousKeywords": body.get('ambigousKeywords', 'tidak ada')
                # "location": ""
            }
            
            print(f'data post: {dataPost}')
            
            url_post = 'https://be-hoax-chaser.dzikrifaza.my.id/news/updateWithUrlRequest'
            response = requests.post(url_post, headers=headers, data=json.dumps(dataPost))
            response.raise_for_status() 
            print(response.text)
            return response.json() 
        except Exception as e:
            print(e)
            return e