import html2text
import re
from datetime import datetime
from urllib.parse import urlparse

class Helpers:
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
            "Advertisement": "",
            "SCROLL TO CONTINUE WITH CONTENT": "",
            "Diterbitkan ": "",
        }

        for old, new in replacements.items():
            clean_text = clean_text.replace(old, new)

        return clean_text
    
    def clean_article_content(raw_content):
        # Menghapus baris yang dimulai dengan "BACA JUGA:"
        cleaned_content = re.sub(r'BACA JUGA:.*\n?', '', raw_content)
        
        # Menghapus bagian "Baca Juga" dan paragraf setelahnya
        cleaned_content = re.sub(r'Baca Juga\n\n.*?\n\n', '', cleaned_content, flags=re.DOTALL)
    
        # Menghapus baris yang dimulai dengan "* ###"
        cleaned_content = re.sub(r'\* ###.*\n', '', cleaned_content)
        
        cleaned_content = re.sub(r'Diterbitkan', '', cleaned_content)
        
        
        return cleaned_content
    
    def convert_to_datetime(date_string):
        # Menghapus kata "Diterbitkan" dari string
        date_string = date_string.replace("Diterbitkan ", "")
        
        # Mendefinisikan format dari input string
        # date_format = "%d %b %Y, %H:%M %Z"
        date_format = "%d %b %Y, %H:%M %Z"
        
        # Mengonversi string ke objek datetime
        date_obj = datetime.strptime(date_string, date_format)
        
        return date_obj
    
    def find_domain_in_url(cari):
        data = ['liputan6.com', 'kompas.com', 'news.detik.com', 'cnnindonesia.com', 'cbncindonesia.com', 'kominfo.go.id']
        # Loop melalui setiap item dalam list 'data'
        for domain in data:
            # Periksa apakah domain ada dalam URL 'cari'
            if domain in cari:
                return domain
        return "source not found"
    
    def get_domain_name(url):
        # Mem-parse URL untuk mendapatkan komponen-komponen individual
        parsed_url = urlparse(url)
        
        # Mendapatkan hostname dari URL
        hostname = parsed_url.hostname
        
        # Memisahkan hostname menjadi bagian-bagian dan menghilangkan subdomain
        domain_parts = hostname.split('.')
        
        # Memastikan domain minimal memiliki 2 bagian (misalnya, 'example.com')
        if len(domain_parts) > 2:
            domain_name = domain_parts[-2]
        else:
            domain_name = domain_parts[0]
        
        return domain_name
    
    def fix_json_format(json_str):
        # Hapus ``` atau ```json di awal dan akhir jika ada
        if json_str.startswith('```') or json_str.startswith('```json'):
            json_str = json_str.lstrip('```json').strip()
        if json_str.endswith('```'):
            json_str = json_str.rstrip('```').strip()
        
        # Hapus spasi kosong ekstra di awal dan akhir
        json_str = json_str.strip()
        
        # Pastikan string JSON dimulai dengan { atau [ dan diakhiri dengan } atau ]
        if not json_str.startswith('{') and not json_str.startswith('['):
            json_str = '{' + json_str
        if not json_str.endswith('}') and not json_str.endswith(']'):
            json_str = json_str + '}'
        
        return json_str