from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

url = "https://www.marca.com/radio/2026/06/15/gonzalo-miro-contundente-empate-espana-cabo-verde-primera-media-hora-hemos-tirado-basura.html"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get(url)

time.sleep(3)

# Rolar a página
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

print("=" * 80)
print("1. VERIFICANDO TAGS <picture> E <source>")
print("=" * 80)

# Verificar tags <picture>
pictures = driver.find_elements("tag name", "picture")
print(f"Total de tags <picture>: {len(pictures)}")

for i, pic in enumerate(pictures):
    sources = pic.find_elements("tag name", "source")
    if sources:
        print(f"\n<picture> {i+1}:")
        for src in sources:
            srcset = src.get_attribute("srcset") or src.get_attribute("data-srcset")
            media = src.get_attribute("media")
            if srcset:
                print(f"  📎 Source: {srcset}")
                if media:
                    print(f"     Media: {media}")

print("\n" + "=" * 80)
print("2. VERIFICANDO TODOS OS ATRIBUTOS DAS TAGS <img>")
print("=" * 80)

imgs = driver.find_elements("tag name", "img")
for i, img in enumerate(imgs):
    src = img.get_attribute("src") or ""
    if "estaticos-marca.com" in src and "loading-icon" not in src:
        print(f"\nImagem {i+1}:")
        print(f"  src: {src}")
        
        # Verificar TODOS os atributos
        all_attrs = driver.execute_script("""
            var attrs = {};
            for (var i = 0; i < arguments[0].attributes.length; i++) {
                var attr = arguments[0].attributes[i];
                attrs[attr.name] = attr.value;
            }
            return attrs;
        """, img)
        
        for attr_name, attr_value in all_attrs.items():
            if "webp" in attr_value.lower() or "srcset" in attr_name.lower() or "data" in attr_name.lower():
                print(f"  🔍 {attr_name}: {attr_value}")

print("\n" + "=" * 80)
print("3. BUSCANDO URLs .webp NO HTML COMPLETO")
print("=" * 80)

html = driver.page_source
webp_urls = re.findall(r'https?://[^\s"\'<>]+\.webp[^\s"\'<>]*', html)
webp_urls = list(set(webp_urls))  # Remover duplicatas

print(f"Total de URLs .webp encontradas no HTML: {len(webp_urls)}")
for url_webp in webp_urls[:10]:  # Mostrar apenas as 10 primeiras
    print(f"  🔗 {url_webp}")

driver.quit()