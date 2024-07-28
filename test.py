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

# Contoh penggunaan:
json_response = '''```
{
"label": "actual",
"news_keywords": ["Biden", "Democratic Party", "election", "family", "humiliated", "performance"],
"publish_date": "2024-07-01",
"title": "President Biden is feeling ‘humiliated’ after debate performance",
"description": "President Biden is feeling ‘humiliated’ after debate performance",
"author": "Meet The Press NOW | NBC News NOW",
"ambigousKeywords": "tidak ada"
}
```
'''

fixed_json = fix_json_format(json_response)
print(fixed_json)

# Coba parsing dengan json.loads untuk memastikan format sudah benar
import json
try:
    data_dict = json.loads(fixed_json)
    print(data_dict)
except json.JSONDecodeError as e:
    print(f"Error parsing JSON: {e}")