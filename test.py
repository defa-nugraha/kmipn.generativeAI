import requests
import json

url = "https://sxzh8vmg-4005.asse.devtunnels.ms/news/updateWithUrlRequest"

payload = json.dumps({
  "urlRequestId": "a47fa774-f72c-437b-b8a5-82845c20c82a",
  "title": "Ganti News Title",
  "description": "Ganti Deskripsi",
  "author": "Dzikri Faza",
  "source": "Narasi",
  "publishDate": "2023-11-28 19:30:43.934129",
  "newsKeywords": "Mengajukan, Klimis",
  "isTraining": True,
  "trainingDate": "2023-11-28 19:30:43.934129",
  "label": "NOT TRAINED",
  "location": "Bandung"
})
headers = {
  'Content-Type': 'application/json',
  }

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
