import vertexai
import os
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import VertexAI
from langchain.embeddings import VertexAIEmbeddings
from datetime import datetime
import requests
import json
from helpers.Helpers import Helpers

# Set environment variable for Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "storage/durable-boulder-407913-0a0904bf432a.json"

class PredictionByVideo:
    @classmethod
    def analysisVideo(cls, url, userId, retry_count=0, max_retries=3):
        # Initialize Vertex AI
        vertexai.init(project="durable-boulder-407913", location="asia-southeast1")

        # Configure the LLM
        llm = VertexAI(
            model_name="text-bison",
            max_output_tokens=256,
            temperature=0.1,
            top_p=0.8,
            top_k=40,
            verbose=True,
        )

        # Configure the embeddings
        EMBEDDING_QPM = 100
        EMBEDDING_NUM_BATCH = 5
        embeddings = VertexAIEmbeddings(
            requests_per_minute=EMBEDDING_QPM,
            num_instances_per_batch=EMBEDDING_NUM_BATCH,
        )

        # Load and process the YouTube video
        loader = YoutubeLoader.from_youtube_url(url, add_video_info=True)
        result = loader.load()

        # Split the text into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=0)
        docs = text_splitter.split_documents(result)
        print(f"# of documents = {len(docs)}")

        # Create a Chroma vector store and retriever
        db = Chroma.from_documents(docs, embeddings)
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 2})

        # Create a RetrievalQA chain
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

        # Define the function to ask questions
        question = """
            Berdasarkan informasi di atas, tentukan apakah hoax atau bukan. Jawablah dengan ketentuan sebagai berikut:
            [
                label: tentukan text ini sebagai hoax atau actual,
                news_keywords: berikan beberapa keyword yang relevan untuk text ini,
                publish_date: berikan tanggal publikasi text sesuai dari informasi di atas dan format yyyy-mm-dd,
                title: berikan judul text sesuai dari informasi di atas,
                description: berikan rangkuman mengenai topik text sesuai dari informasi di atas,
                author: berikan penulis text sesuai dari informasi di atas,
                ambigousKeywords: berikan kata-kata ambigu yang terdapat pada text ini jika tidak ada kirim tidak ada
            ]
            
            Catatan: Pastikan jawaban dimulai dengan { dan diakhiri dengan }. Pastikan tidak ada karakter ```json dan ``` di awal atau di akhir string JSON.
        """
        
        video_subset = qa({"query": question})
        context = video_subset['source_documents']
        print("context: ", context)
        prompt = f"""
        Saya ingin Anda menentukan apakah text berikut adalah hoax atau bukan.
        
        Text:
        {context}
        
        {question}
        """
        parameters = {
            "temperature": 0,
            "max_output_tokens": 256,
            "top_p": 0.8,
            "top_k": 40,
        }
        
        response = llm.predict(prompt, **parameters)
        print("response: ", response)
        try:
            fix_json_format = Helpers.fix_json_format(response)
            data_dict = json.loads(fix_json_format)
            urlRequestId = PredictionByVideo.post_request_url(url, userId)
            data_dict['urlRequestId'] = urlRequestId
        except json.JSONDecodeError as e:
            print("JSON decode error: ", e)
            if retry_count < max_retries:
                print("Retrying analysisVideo... attempt", retry_count + 1)
                return cls.analysisVideo(url, userId, retry_count + 1, max_retries)
            else:
                print("Max retries reached. Could not decode JSON.")
                return None
            
        print(type(data_dict))
        try:
            data_dict[0]['source'] =  Helpers.get_domain_name(url)
        
            req = PredictionByVideo.post_news_data(url, data_dict[0])
            print(1)
        except Exception as e:
            data_dict['source'] =  Helpers.get_domain_name(url)
            print(2)
            req = PredictionByVideo.post_news_data(url, data_dict)
            
        print("type data: ", type(data_dict[0]))
        return req
    
    
    @classmethod
    def post_news_data(cls, url, body):
        headers = {
            'Content-Type': 'application/json',
        }

        try:
            current_time = datetime.now().isoformat()
            publish_date = str(body.get('publish_date', 'tidak ada'))
            
            dataPost = {
                "urlRequestId": body.get('urlRequestId', 'tidak ada'),
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
            
            url_post = 'https://be-hoax-chaser.dzikrifaza.my.id/news/createOrUpdate'
            response = requests.post(url_post, headers=headers, data=json.dumps(dataPost))
            response.raise_for_status() 
            print(response.text)
            return response.json() 
        except Exception as e:
            print(e)
            return e
        
    @classmethod
    def post_request_url(cls, url, userId):
        headers = {
            'Content-Type': 'application/json',
        }

        try:
            dataPost = {
                "userId": userId,
                "url": url
            }
            
            print(f'data post: {dataPost}')
            
            url_post = 'https://be-hoax-chaser.dzikrifaza.my.id/url-req/createOrUpdate'
            response = requests.post(url_post, headers=headers, data=json.dumps(dataPost))
            response.raise_for_status() 
            print(response.text)
            t = response.json() 
            return t["data"]["id"]
        except Exception as e:
            print(e)
            return e
