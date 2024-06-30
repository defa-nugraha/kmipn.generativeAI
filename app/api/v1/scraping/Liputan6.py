from helpers.Helpers import Helpers
from bs4 import BeautifulSoup
import requests
import pandas as pd

class Liputan6:
    def __init__(self, url):
        self.url = url

    def get_data(self):
        all_data = []
        news_data = {
            "title": "",
            "description": "",
            "author": "",
            "source": "liputan6",
            "publish_date": "",
            "url": self.url
        }
            
        res = requests.get(self.url)
        soup = BeautifulSoup(res.content, "html.parser")

        title = soup.find("h1", {"class": "read-page--header--title entry-title"})
        author = soup.find('span', {"class": "read-page--header--author__name fn"})
        date = soup.find("time", {"class": "read-page--header--author__datetime"})
        data = soup.find(
            "div", {"class": "article-content-body__item-content"}
        )

        if title and date and data:
            cleaned_text = Helpers.clean_text(str(data))
            all_data.append(
                {
                    "title": title.text.strip(),
                    "date": Helpers.convert_to_datetime(date.text.strip()),
                    "text": Helpers.clean_article_content(cleaned_text),
                }
            )
                
            news_data["title"] = title.text.strip()
            news_data["author"] = author.text.strip()
            news_data["publish_date"] = Helpers.convert_to_datetime(date.text.strip())
            news_data["description"] = Helpers.clean_article_content(cleaned_text)
            news_data["data"] = pd.DataFrame(all_data)
            print(news_data["publish_date"])
        else:
            print(f"Some elements were not found for URL: {self.url}")


        return news_data