from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://www.marca.com/radio/2026/06/15/gonzalo-miro-contundente-empate-espana-cabo-verde-primera-media-hora-hemos-tirado-basura.html"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get(url)

time.sleep(3)

# Rolar a página para carregar lazy-loading
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# Pegar todas as imagens
imgs = driver.find_elements("tag name", "img")
print(f"Total de imagens encontradas: {len(imgs)}")

for i, img in enumerate(imgs):
    src = img.get_attribute("src") or img.get_attribute("data-src")
    if src and "estaticos-marca.com" in src and "loading-icon" not in src:
        print(f"\nImagem {i+1}:")
        print(f"  URL: {src}")
        if ".webp" in src:
            print(f"  ✅ Formato: WebP (otimizado)")
        elif ".jpeg" in src or ".jpg" in src:
            print(f"  📷 Formato: JPEG")

driver.quit()