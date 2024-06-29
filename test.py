import os
from Liputan6 import Liputan6

def main():
    urls = [
        "https://www.liputan6.com/news/read/5628123/kpk-tetapkan-tersangka-proyek-pengadaan-truk-basarnas-ini-sosoknya",
        # "https://www.liputan6.com/islami/read/5626936/benarkah-bidah-jika-berkunjung-ke-orang-yang-pulang-haji-buya-yahya-ungkap-fadhilahnya?page=2"
    ]

    new_data, title, date, data = Liputan6(urls).get_data()
    if os.path.exists("berita.csv"):
        new_data.to_csv("berita.csv", mode="a", header=False, index=False)
    else:
        new_data.to_csv("berita.csv", index=False)
    # print(title)
    print(date)
    # print(data)
main()
