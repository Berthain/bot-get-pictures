# downloader.py
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils import ALLOWED_EXTS, get_image_extension, sanitize_filename

class ImageDownloader:
    def __init__(self, url, save_dir, on_status, on_progress, on_complete):
        self.url = url
        self.save_dir = save_dir
        # Callbacks para comunicar com a Interface Gráfica
        self.on_status = on_status
        self.on_progress = on_progress
        self.on_complete = on_complete

    def run(self):
    # Headers mais completos e realistas
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            # Usar Session para manter cookies
            session = requests.Session()
            response = session.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            self.on_complete(error=str(e))
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        if not img_tags:
            self.on_complete(error="no_images")
            return

        total_images = len(img_tags)
        downloaded = 0

        for img in img_tags:
            src = img.get('src')
            if not src or src.startswith('data:'):
                continue
                
            img_url = urljoin(self.url, src)
            parsed_url = urlparse(img_url)
            
            try:
                img_response = requests.get(img_url, headers=headers, timeout=15, stream=True)
                content_type = img_response.headers.get('content-type', '').split(';')[0].strip().lower()
                
                final_ext = get_image_extension(parsed_url.path, content_type)

                if img_response.status_code == 200 and final_ext is not None:
                    filename = os.path.basename(parsed_url.path)
                    
                    if not filename or '.' not in filename or not filename.lower().endswith(tuple(ALLOWED_EXTS)):
                        filename = f"image_{downloaded}{final_ext}"
                        
                    filename = sanitize_filename(filename)
                    if not filename:
                        filename = f"image_{downloaded}{final_ext}"
                        
                    filepath = os.path.join(self.save_dir, filename)
                    
                    counter = 1
                    base, ext = os.path.splitext(filepath)
                    while os.path.exists(filepath):
                        filepath = f"{base}_{counter}{ext}"
                        counter += 1

                    with open(filepath, 'wb') as f:
                        for chunk in img_response.iter_content(1024):
                            f.write(chunk)
                            
                    downloaded += 1
                    self.on_progress(downloaded, total_images)
                    self.on_status(f"Baixando... {downloaded}/{total_images}")
                    
            except Exception:
                continue

        self.on_complete(downloaded=downloaded)