import html2text
import re
from datetime import datetime

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