import os
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloader de Imagens - Berthain")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Variáveis
        self.url_var = tk.StringVar()
        self.dir_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Aguardando...")
        self.progress_var = tk.IntVar(value=0)

        # Mapeamento de tipos MIME para extensões (Garante AVIF, BMP, GIF, etc.)
        self.mime_to_ext = {
            'image/jpeg': '.jpg', 'image/jpg': '.jpg',
            'image/png': '.png', 'image/gif': '.gif',
            'image/bmp': '.bmp', 'image/avif': '.avif',
            'image/webp': '.webp', 'image/svg+xml': '.svg',
            'image/x-icon': '.ico', 'image/vnd.microsoft.icon': '.ico'
        }
        
        # Extensões que consideramos como imagens válidas
        self.allowed_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.avif', '.webp', '.svg', '.ico'}
        
        # Extensões de scripts/páginas que devemos ignorar se aparecerem na URL
        self.ignore_exts = {'.php', '.html', '.htm', '.asp', '.aspx', '.jsp', '.cgi'}

        self.create_widgets()

    def create_widgets(self):
        # Campo de URL
        tk.Label(self.root, text="Link do Site:", font=("Arial", 10, "bold")).pack(pady=(20, 5), anchor="w", padx=20)
        self.entry_url = tk.Entry(self.root, textvariable=self.url_var, width=70)
        self.entry_url.pack(padx=20, fill="x")

        # Campo de Diretório
        tk.Label(self.root, text="Salvar em:", font=("Arial", 10, "bold")).pack(pady=(15, 5), anchor="w", padx=20)
        frame_dir = tk.Frame(self.root)
        frame_dir.pack(padx=20, fill="x")
        
        self.entry_dir = tk.Entry(frame_dir, textvariable=self.dir_var, width=55)
        self.entry_dir.pack(side="left", fill="x", expand=True)
        
        self.btn_browse = tk.Button(frame_dir, text="Procurar...", command=self.browse_directory)
        self.btn_browse.pack(side="right", padx=(5, 0))

        # Barra de Progresso e Status
        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=560, mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(pady=20)
        
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, fg="blue")
        self.lbl_status.pack()

        # Botão de Download
        self.btn_download = tk.Button(self.root, text="Iniciar Download", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.start_download)
        self.btn_download.pack(pady=20)

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Selecione a pasta para salvar as imagens")
        if directory:
            self.dir_var.set(directory)

    def start_download(self):
        url = self.url_var.get().strip()
        save_dir = self.dir_var.get().strip()

        if not url:
            messagebox.showwarning("Atenção", "Por favor, insira o link do site.")
            return
        if not save_dir:
            messagebox.showwarning("Atenção", "Por favor, selecione uma pasta para salvar as imagens.")
            return

        self.btn_download.config(state="disabled")
        self.btn_browse.config(state="disabled")
        self.progress_var.set(0)

        thread = threading.Thread(target=self.download_images, args=(url, save_dir))
        thread.start()

    def finish_download_process(self, message):
        self.reset_ui()  # Limpa a barra e os botões primeiro
        messagebox.showinfo("Sucesso", message) # Depois mostra a mensagem
    
    def download_images(self, url, save_dir):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        try:
            self.status_var.set("Conectando ao site...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro de Conexão", f"Não foi possível acessar o site:\n{e}"))
            self.reset_ui()
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        if not img_tags:
            self.root.after(0, lambda: messagebox.showinfo("Info", "Nenhuma tag <img> encontrada na página."))
            self.reset_ui()
            return

        total_images = len(img_tags)
        downloaded = 0
        self.root.after(0, lambda: self.progress_bar.config(maximum=total_images))

        for img in img_tags:
            src = img.get('src')
            if not src or src.startswith('data:'):
                continue
                
            img_url = urljoin(url, src)
            parsed_url = urlparse(img_url)
            
            # Extrair extensão da URL
            path = parsed_url.path
            if path.endswith('/'): path = path[:-1]
            url_ext = os.path.splitext(path)[1].lower()
            
            # Ignorar extensões de scripts/páginas
            if url_ext in self.ignore_exts:
                url_ext = ''

            try:
                img_response = requests.get(img_url, headers=headers, timeout=15, stream=True)
                content_type = img_response.headers.get('content-type', '').split(';')[0].strip().lower()
                
                # Lógica robusta para identificar se é imagem (JPEG, BMP, AVIF, GIF, etc)
                is_valid = False
                final_ext = url_ext
                
                if url_ext in self.allowed_exts:
                    is_valid = True
                elif content_type in self.mime_to_ext:
                    is_valid = True
                    if not final_ext:
                        final_ext = self.mime_to_ext[content_type]
                elif content_type.startswith('image/'):
                    is_valid = True
                    if not final_ext:
                        final_ext = '.' + content_type.split('/')[-1]

                if img_response.status_code == 200 and is_valid:
                    
                    # Gerar nome do arquivo
                    filename = os.path.basename(parsed_url.path)
                    
                    # Se não tiver nome ou extensão válida, criar um
                    if not filename or '.' not in filename or not filename.lower().endswith(tuple(self.allowed_exts)):
                        filename = f"image_{downloaded}{final_ext}"
                        
                    # Limpar caracteres inválidos
                    filename = "".join(c for c in filename if c.isalnum() or c in ('.', '-', '_')).rstrip()
                    if not filename:
                        filename = f"image_{downloaded}{final_ext}"
                        
                    filepath = os.path.join(save_dir, filename)
                    
                    # Evitar sobrescrever
                    counter = 1
                    base, ext = os.path.splitext(filepath)
                    while os.path.exists(filepath):
                        filepath = f"{base}_{counter}{ext}"
                        counter += 1

                    # Salvar o arquivo
                    with open(filepath, 'wb') as f:
                        for chunk in img_response.iter_content(1024):
                            f.write(chunk)
                            
                    downloaded += 1
                    self.root.after(0, lambda d=downloaded: self.progress_var.set(d))
                    self.root.after(0, lambda d=downloaded, t=total_images: self.status_var.set(f"Baixando... {d}/{t}"))
                    
            except Exception:
                continue
        msg = f"Download concluído!\n{downloaded} imagens salvas em:\n{save_dir}"        
        #self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"Download concluído!\n{downloaded} imagens salvas em:\n{save_dir}"))
        self.root.after(0, self.finish_download_process, msg)
        self.reset_ui()

    def reset_ui(self):
        self.btn_download.config(state="normal")
        self.btn_browse.config(state="normal")
        self.status_var.set("Aguardando...")
        self.progress_var.set(0)        




if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()