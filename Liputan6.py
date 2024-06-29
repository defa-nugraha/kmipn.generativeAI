from Helpers import Helpers
from bs4 import BeautifulSoup
import requests
import pandas as pd

class Liputan6:
    def __init__(self, url):
        self.urls = url

    def get_data(self):
        all_data = []
        title = ''
        author = ''
        date = ''
        data = ''
        for url in self.urls:
            
            res = requests.get(url)
            soup = BeautifulSoup(res.content, "html.parser")

            title = soup.find("h1", {"class": "read-page--header--title entry-title"})
            author = soup.fiod('span', {"class": "read-page--header--author__name fn"})
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
                title = title.text.strip()
                author = author.text.strip()
                date = Helpers.convert_to_datetime(date.text.strip())
                data = Helpers.clean_article_content(cleaned_text)
                
            else:
                print(f"Some elements were not found for URL: {url}")

        new_data = pd.DataFrame(all_data)

        return new_data, title, date, data