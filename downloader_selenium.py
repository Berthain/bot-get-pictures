# downloader_selenium.py
import os
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils import ALLOWED_EXTS, get_image_extension, sanitize_filename

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class ImageDownloaderSelenium:
    def __init__(self, url, save_dir, on_status, on_progress, on_complete):
        self.url = url
        self.save_dir = save_dir
        self.on_status = on_status
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.driver = None

    def run(self):
        try:
            self.on_status("Iniciando navegador...")
            
            # Configurar Chrome
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36")
            
            # Iniciar driver
            self.on_status("Configurando ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.on_status("Carregando página...")
            self.driver.get(self.url)
            
            # Aguardar carregamento inicial
            time.sleep(3)
            
            # Rolar a página para carregar imagens lazy-loading
            self.on_status("Rolando página para carregar todas as imagens...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            max_scrolls = 5
            
            while scroll_count < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_count += 1
                self.on_status(f"Rolando... ({scroll_count}/{max_scrolls})")
            
            # Voltar para o topo
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Obter HTML após JavaScript
            self.on_status("Analisando imagens...")
            html = self.driver.page_source
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Lista para armazenar URLs de imagens (usar set para evitar duplicatas)
            img_urls = set()
            
            # ========================================
            # ESTRATÉGIA 1: Tags <picture> → <source> (srcset)
            # Para sites como Marca.com que usam imagens responsivas
            # ========================================
            self.on_status("Buscando imagens em tags <picture>...")
            picture_tags = soup.find_all('picture')
            for picture in picture_tags:
                sources = picture.find_all('source')
                for source in sources:
                    srcset = source.get('srcset') or source.get('data-srcset')
                    if srcset:
                        # srcset pode ter múltiplas URLs separadas por vírgula
                        # Ex: "url1.webp 360w, url2.webp 660w, url3.webp 1320w"
                        urls = [url.strip().split()[0] for url in srcset.split(',')]
                        for url in urls:
                            if url and not url.startswith('data:'):
                                img_urls.add(url)
            
            # ========================================
            # ESTRATÉGIA 2: Tags <img> com múltiplos atributos
            # Para sites como The Sun, AS.com que usam lazy-loading
            # ========================================
            self.on_status("Buscando imagens em tags <img>...")
            img_tags = soup.find_all('img')
            for img in img_tags:
                # Tentar pegar o src de diferentes atributos
                src = (img.get('src') or 
                       img.get('data-src') or 
                       img.get('data-lazy-src') or 
                       img.get('data-original') or
                       img.get('data-srcset') or
                       img.get('data-lazy-srcset') or
                       img.get('srcset') or
                       '')
                
                # Se for srcset, pegar a primeira URL
                if src and ' ' in src:
                    src = src.split(' ')[0]
                
                if src and not src.startswith('data:'):
                    img_urls.add(src)
            
            # ========================================
            # ESTRATÉGIA 3: Buscar URLs de imagem no HTML com regex
            # Fallback para URLs escondidas em JavaScript ou JSON
            # ========================================
            self.on_status("Buscando URLs de imagem no HTML...")
            
            # Buscar URLs .webp
            webp_urls = re.findall(r'https?://[^\s"\'<>]+\.webp[^\s"\'<>]*', html)
            for url in webp_urls:
                clean_url = url.strip('"\'()[]')
                img_urls.add(clean_url)
            
            # Buscar URLs .jpg, .jpeg, .png, .gif
            other_urls = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|bmp|avif)[^\s"\'<>]*', html, re.IGNORECASE)
            for url in other_urls:
                clean_url = url.strip('"\'()[]')
                img_urls.add(clean_url)
            
            # ========================================
            # FILTRO: Remover URLs inválidas
            # ========================================
            img_urls = {url for url in img_urls if 
                       url and 
                       not url.startswith('data:') and 
                       'loading-icon' not in url and 
                       'spinner' not in url.lower() and
                       'placeholder' not in url.lower()}
            
            if not img_urls:
                self.on_complete(error="no_images")
                return

            total_images = len(img_urls)
            downloaded = 0
            skipped = 0
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            
            for i, img_url in enumerate(img_urls):
                try:
                    parsed_url = urlparse(img_url)
                    response = requests.get(img_url, headers=headers, timeout=15, stream=True)
                    content_type = response.headers.get('content-type', '').split(';')[0].strip().lower()
                    
                    final_ext = get_image_extension(parsed_url.path, content_type)

                    if response.status_code == 200 and final_ext is not None:
                        filename = os.path.basename(parsed_url.path)
                        
                        # Remover parâmetros da URL
                        if '?' in filename:
                            filename = filename.split('?')[0]
                        
                        if not filename or '.' not in filename:
                            filename = f"image_{downloaded}{final_ext}"
                            
                        filename = sanitize_filename(filename)
                        if not filename:
                            filename = f"image_{downloaded}{final_ext}"
                            
                        filepath = os.path.join(self.save_dir, filename)
                        
                        # Evitar sobrescrever arquivos existentes
                        counter = 1
                        base, ext = os.path.splitext(filepath)
                        while os.path.exists(filepath):
                            filepath = f"{base}_{counter}{ext}"
                            counter += 1

                        # Salvar o arquivo
                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                                
                        downloaded += 1
                        self.on_progress(downloaded, total_images)
                        self.on_status(f"Baixando... {downloaded}/{total_images} (ignoradas: {skipped})")
                        
                except Exception as e:
                    skipped += 1
                    continue

            self.on_complete(downloaded=downloaded)
            
        except Exception as e:
            self.on_complete(error=f"Erro no Selenium: {str(e)}")
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass