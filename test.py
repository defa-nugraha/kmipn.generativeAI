import vertexai
import os
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import VertexAI
from langchain.embeddings import VertexAIEmbeddings

# Set environment variable for Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "app/storage/durable-boulder-407913-0a0904bf432a.json"

# Initialize Vertex AI
vertexai.init(project="durable-boulder-407913", location="asia-southeast1")

# Configure the LLM
llm = VertexAI(
    model_name="text-bison@001",
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
loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=WR1ydijTx5E&pp=ygUGY29kaW5n", add_video_info=True)
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
def sm_ask(question, print_results=True):
    video_subset = qa({"query": question})
    context = video_subset['source_documents']
    
    prompt = f"""
    Answer the following question in a detailed manner, using information from the text below. If the answer is not in the text, say I don't know and do not generate your own response.

    Question:
    {question}
    Text:
    {context}

    Question:
    {question}

    Answer:
    """
    parameters = {
        "temperature": 0.1,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    response = llm.predict(prompt, **parameters)
    return {
        "answer": response
    }

# Function to get response from the model
def get_response(input_text):
    response = sm_ask(input_text)
    return response

# Main loop to ask questions from the terminal
if __name__ == "__main__":
    while True:
        input_text = input("Enter your question (or 'exit' to quit): ")
        if input_text.lower() == 'exit':
            break
        response = get_response(input_text)
        print(f"Answer: {response['answer']}\n")
