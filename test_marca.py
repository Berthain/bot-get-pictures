import requests
from bs4 import BeautifulSoup

url = "https://www.marca.com/radio/2026/06/15/gonzalo-miro-contundente-empate-espana-cabo-verde-primera-media-hora-hemos-tirado-basura.html"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

imgs = soup.find_all('img')
print(f"Total de tags <img> encontradas: {len(imgs)}")

for i, img in enumerate(imgs):
    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
    if src and 'estaticos-marca.com' in src:
        print(f"\nImagem {i+1}:")
        print(f"  URL: {src}")
        print(f"  Alt: {img.get('alt', 'N/A')}")