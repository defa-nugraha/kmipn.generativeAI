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
    def analysisVideo(cls, url, userId):
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
            Pertanyaan: Saya ingin Anda menentukan apakah text berikut adalah hoax atau bukan:

            Berdasarkan informasi di atas, tolong tentukan apakah hoax atau bukan. Jawablah dengan ketentuan sebagai berikut:
            [
                label: tentukan text ini sebagai hoax atau actual,
                news_keywords: berikan beberapa keyword yang relevan untuk text ini,
                publish_date: berikan tanggal publikasi text sesuai dari informasi di atas dan format yyyy-mm-dd,
                title: berikan judul text sesuai dari informasi di atas,
                description: berikan deskripsi text sesuai dari informasi di atas,
                author: berikan penulis text sesuai dari informasi di atas,
                ambigousKeywords: berikan kata-kata ambigu yang terdapat pada text ini jika tidak ada kirim tidak ada
            ]
            
            Contoh Jawaban yang Benar:

            {
                "label": "actual",
                "news_keywords": ["coding", "job", "no cs degree", "no bootcamp"],
                "publish_date": "2023-06-13",
                "title": "How I Learned to Code in 4 Months & Got a Job! (No CS Degree, No Bootcamp)",
                "description": "In this video, Tim Kim shares his journey of learning to code in 4 months and landing a job as a software developer without a CS degree or a bootcamp. He talks about the resources he used, the challenges he faced, and the strategies he employed to succeed.",
                "author": "Tim Kim",
                "ambigousKeywords": "tidak ada"
            }
            
            Catatan: Pastikan jawaban dimulai dengan { dan diakhiri dengan }. Pastikan tidak ada karakter ```json dan ``` di awal atau di akhir string JSON.
        """
        
        video_subset = qa({"query": question})
        context = video_subset['source_documents']
        
        prompt = f"""json
        Jawablah pertanyaan berikut ini secara terperinci, dengan menggunakan informasi dari teks di bawah ini. Jika jawabannya tidak ada di dalam teks, katakanlah saya tidak tahu dan jangan membuat jawaban Anda sendiri.
        
        Text:
        {context}
        
        {question}
        """
        parameters = {
            "temperature": 0.1,
            "max_output_tokens": 256,
            "top_p": 0.8,
            "top_k": 40,
        }
        print("Kirim ke url request")
        response = llm.predict(prompt, **parameters)
        print("response: ", response)
        try:
            data_dict = json.loads(Helpers.fix_json_format(response))
            PredictionByVideo.post_request_url(url, userId)
        except:
            # lakukan predict ulang
            PredictionByVideo.analysisVideo(url, userId)
            
        print(type(data_dict))
        try:
            data_dict[0]['source'] =  Helpers.get_domain_name(url)
        
            req = PredictionByVideo.post_news_data(url, data_dict[0])
            print(1)
        except Exception as e:
            data_dict['source'] =  Helpers.get_domain_name(url)
            print(2)
            req = PredictionByVideo.post_news_data(url, data_dict)
            
        print("type dtaa: ", type(data_dict[0]))
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
                # "urlRequestId": "680030b2-1b5a-4aba-8086-4c86ec66b3bb",
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
            return response.json() 
        except Exception as e:
            print(e)
            return e
    