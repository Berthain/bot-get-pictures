# gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from downloader import ImageDownloader

class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloader de Imagens - Berthain")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.url_var = tk.StringVar()
        self.dir_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Aguardando...")
        self.progress_var = tk.IntVar(value=0)

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Link do Site:", font=("Arial", 10, "bold")).pack(pady=(20, 5), anchor="w", padx=20)
        self.entry_url = tk.Entry(self.root, textvariable=self.url_var, width=70)
        self.entry_url.pack(padx=20, fill="x")

        tk.Label(self.root, text="Salvar em:", font=("Arial", 10, "bold")).pack(pady=(15, 5), anchor="w", padx=20)
        frame_dir = tk.Frame(self.root)
        frame_dir.pack(padx=20, fill="x")
        
        self.entry_dir = tk.Entry(frame_dir, textvariable=self.dir_var, width=55)
        self.entry_dir.pack(side="left", fill="x", expand=True)
        
        self.btn_browse = tk.Button(frame_dir, text="Procurar...", command=self.browse_directory)
        self.btn_browse.pack(side="right", padx=(5, 0))

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=560, mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(pady=20)
        
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, fg="blue")
        self.lbl_status.pack()

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

        # Cria a instância do downloader com as funções de callback
        downloader = ImageDownloader(
            url=url, 
            save_dir=save_dir, 
            on_status=self.update_status, 
            on_progress=self.update_progress, 
            on_complete=self.download_finished
        )

        # Inicia em uma thread separada
        thread = threading.Thread(target=downloader.run)
        thread.start()

    # --- Métodos de Callback (Atualizam a UI de forma segura) ---
    def update_status(self, msg):
        self.root.after(0, lambda: self.status_var.set(msg))

    def update_progress(self, current, total):
        if total > 0:
            self.root.after(0, lambda: self.progress_bar.config(maximum=total))
        self.root.after(0, lambda: self.progress_var.set(current))

    def download_finished(self, downloaded=None, error=None):
        self.root.after(0, self.finish_download_process, downloaded, error)

    def finish_download_process(self, downloaded, error):
        self.reset_ui()
        
        if error:
            if error == "no_images":
                messagebox.showinfo("Info", "Nenhuma tag <img> encontrada na página.")
            else:
                messagebox.showerror("Erro", f"Ocorreu um erro:\n{error}")
        else:
            save_dir = self.dir_var.get().strip()
            messagebox.showinfo("Sucesso", f"Download concluído!\n{downloaded} imagens salvas em:\n{save_dir}")

    def reset_ui(self):
        self.btn_download.config(state="normal")
        self.btn_browse.config(state="normal")
        self.status_var.set("Aguardando...")
        self.progress_var.set(0) # Zera a barra de progresso