from helpers.Helpers import Helpers
from bs4 import BeautifulSoup
import requests
import pandas as pd

class Kominfo:
    def __init__(self, url):
        self.url = url

    def get_data(self):
        all_data = []
        news_data = {
            "title": "",
            "description": "",
            "author": "kominfo",
            "source": "kominfo",
            "publish_date": "",
            "url": self.url
        }

        res = requests.get(self.url)
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.find("h1", {"class": "title"})
        date = soup.find("div", {"class": "date"})
        data = soup.find("div", {"class": "youtube-container"})

        missing_elements = []
        
        if not title:
            missing_elements.append("title")
        if not date:
            missing_elements.append("date")
        if not data:
            missing_elements.append("data")

        if missing_elements:
            print(f"Some elements were not found for URL: {self.url}")
            print(f"Missing elements: {', '.join(missing_elements)}")
        else:
            cleaned_text = Helpers.clean_text(str(data))
            all_data.append(
                {
                    "title": title.text.strip(),
                    "date": Helpers.convert_to_datetime(date.text.strip()),
                    "text": Helpers.clean_article_content(cleaned_text),
                }
            )

            news_data["title"] = title.text.strip()
            news_data["publish_date"] = Helpers.convert_to_datetime(date.text.strip())
            news_data["description"] = Helpers.clean_article_content(cleaned_text)
            print(news_data)

        return news_data