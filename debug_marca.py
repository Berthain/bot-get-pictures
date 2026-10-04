# debug_marca.py
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

url = "https://www.marca.com/radio/2026/06/15/gonzalo-miro-contundente-empate-espana-cabo-verde-primera-media-hora-hemos-tirado-basura.html"
save_dir = "D:\\temp\\marca_test"

# Criar pasta se não existir
os.makedirs(save_dir, exist_ok=True)

print("=" * 80)
print("INICIANDO DEBUG DO MARCA.COM")
print("=" * 80)

# Configurar Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36")

print("\n1. Iniciando navegador...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

print("2. Carregando página...")
driver.get(url)
time.sleep(3)

print("3. Rolando página...")
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

print("4. Obtendo HTML...")
html = driver.page_source

print("\n" + "=" * 80)
print("ANÁLISE DO HTML")
print("=" * 80)

# Buscar URLs .webp com article_660_widen_webp
print("\n🔍 Buscando URLs com 'article_660_widen_webp'...")
webp_urls_660 = re.findall(r'https?://[^\s"\'<>]*article_660_widen_webp[^\s"\'<>]*\.webp[^\s"\'<>]*', html)
webp_urls_660 = list(set(webp_urls_660))

print(f"✅ Encontradas {len(webp_urls_660)} URLs:")
for i, url_img in enumerate(webp_urls_660, 1):
    print(f"   {i}. {url_img}")

# Buscar TODAS as URLs .webp
print("\n🔍 Buscando TODAS as URLs .webp...")
all_webp_urls = re.findall(r'https?://[^\s"\'<>]+\.webp[^\s"\'<>]*', html)
all_webp_urls = list(set(all_webp_urls))

print(f"✅ Encontradas {len(all_webp_urls)} URLs .webp no total")

# Filtrar apenas as que queremos
target_urls = []
for url_img in all_webp_urls:
    if '6a305bcf19002' in url_img or '6a305c8cd0f9a' in url_img or '6a305d12d0c79' in url_img:
        target_urls.append(url_img)

print(f"\n🎯 URLs alvo encontradas: {len(target_urls)}")
for url_img in target_urls:
    print(f"   → {url_img}")

print("\n" + "=" * 80)
print("TESTE DE DOWNLOAD")
print("=" * 80)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Testar download das URLs alvo
for i, img_url in enumerate(target_urls[:3], 1):  # Testar apenas as 3 primeiras
    print(f"\n📥 Testando download {i}: {img_url}")
    
    try:
        response = requests.get(img_url, headers=headers, timeout=15, stream=True)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            # Gerar nome do arquivo
            parsed_url = urlparse(img_url)
            filename = os.path.basename(parsed_url.path)
            
            if '?' in filename:
                filename = filename.split('?')[0]
            
            if not filename or '.' not in filename:
                filename = f"test_image_{i}.webp"
            
            filename = sanitize_filename(filename)
            if not filename:
                filename = f"test_image_{i}.webp"
            
            filepath = os.path.join(save_dir, filename)
            
            # Salvar
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            file_size = os.path.getsize(filepath)
            print(f"   ✅ Salvo: {filename}")
            print(f"   📦 Tamanho: {file_size} bytes")
            
        else:
            print(f"   ❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {str(e)}")

driver.quit()

print("\n" + "=" * 80)
print("DEBUG CONCLUÍDO")
print("=" * 80)
print(f"\nArquivos salvos em: {save_dir}")