# from bs4 import BeautifulSoup
# import html2text
# import requests
# import pandas as pd
# import os

# def clean_text(text):
#     # Menghapus tag HTML
#     text_maker = html2text.HTML2Text()
#     text_maker.ignore_links = True
#     clean_text = text_maker.handle(text).strip()

#     # Mengganti karakter yang tidak diinginkan
#     replacements = {
#         "€": "",
#         "â": "",
#         "œ": "",
#         "#####": "",

#         "ADVERTISEMENT": "",
#         "SCROLL TO CONTINUE WITH CONTENT": ""
#     }

#     for old, new in replacements.items():
#         clean_text = clean_text.replace(old, new)

#     return clean_text

# def main():
#     url = 'https://www.cnnindonesia.com/nasional/20150115140901-32-24892/budi-gunawan-resmi-kapolri-pramono-anung-temui-megawati'
#     res = requests.get(url)
#     soup = BeautifulSoup(res.text, 'html.parser')

#     title = soup.find('h1', {'class': 'mb-2 text-[28px] leading-9 text-cnn_black'})
#     date = soup.find('div', {'class': 'text-cnn_grey text-sm mb-4'})
#     data = soup.find('div', {'class': 'detail-text text-cnn_black text-sm grow min-w-0'})

#     if title and date and data:
#         cleaned_text = clean_text(str(data))
#         new_data = pd.DataFrame({
#             'title': [title.text.strip()],
#             'date': [date.text.strip()],
#             'text': [cleaned_text]
#         })

#         output_file = 'berita.csv'

#         if os.path.exists(output_file):
#             new_data.to_csv(output_file, mode='a', header=False, index=False)
#         else:
#             new_data.to_csv(output_file, index=False)

#         print("Data has been written to berita.csv")
#     else:
#         print("Some elements were not found")

# main()


from bs4 import BeautifulSoup
import html2text
import requests
import pandas as pd
import os


def clean_text(text):
    # Menghapus tag HTML
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = True
    clean_text = text_maker.handle(text).strip()

    # Mengganti karakter yang tidak diinginkan
    replacements = {
        "€": "",
        "â": "",
        "œ": "",
        "####": "",
        "ADVERTISEMENT": "",
        "SCROLL TO CONTINUE WITH CONTENT": "",
    }

    for old, new in replacements.items():
        clean_text = clean_text.replace(old, new)

    return clean_text


def scrape_and_append(urls, output_file):
    all_data = []
    for url in urls:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.find("h1", {"class": "mb-2 text-[28px] leading-9 text-cnn_black"})
        date = soup.find("div", {"class": "text-cnn_grey text-sm mb-4"})
        data = soup.find(
            "div", {"class": "detail-text text-cnn_black text-sm grow min-w-0"}
        )

        if title and date and data:
            cleaned_text = clean_text(str(data))
            all_data.append(
                {
                    "title": title.text.strip(),
                    "date": date.text.strip(),
                    "text": cleaned_text,
                }
            )
        else:
            print(f"Some elements were not found for URL: {url}")

    new_data = pd.DataFrame(all_data)

    if os.path.exists(output_file):
        new_data.to_csv(output_file, mode="a", header=False, index=False)
    else:
        new_data.to_csv(output_file, index=False)

    print(f"Data has been written to {output_file}")


def main():
    urls = [
        "https://www.cnnindonesia.com/nasional/20240516074518-32-1098261/dua-eks-timses-prabowo-ditunjuk-jadi-stafsus-jokowi-grace-dan-juri",
        "https://www.cnnindonesia.com/nasional/20240207112824-617-1059701/jokowi-soal-pemilu-2024-saya-tidak-akan-berkampanye",
        "https://www.cnnindonesia.com/nasional/20240411123029-20-1085270/prabowo-ajak-didit-salaman-lebaran-dengan-jokowi-di-istana",
        "https://www.cnnindonesia.com/nasional/20240203115736-617-1058058/umy-kritik-pemerintahan-jokowi-ri-di-ambang-pintu-jadi-negara-gagal",
    ]

    output_file = "berita.csv"
    scrape_and_append(urls, output_file)


main()
