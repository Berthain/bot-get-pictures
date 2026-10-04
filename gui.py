# gui.py
import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ImageDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Downloader de Imagens - Berthain")
        self.root.geometry("650x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#070d18")
        self.root.option_add("*Font", "Arial 10")
        self.root.option_add("*Background", "#070d18")
        self.root.option_add("*Foreground", "#e5e7eb")

        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_download_dir.json")
        self.default_download_dir = self.load_default_directory()
        self.current_theme = "dark"
        self.theme_var = tk.StringVar(value=self.current_theme)
        self.themes = {
            "dark": {
                "bg": "#070d18",
                "panel": "#111827",
                "panel_alt": "#0f172a",
                "title": "#f8fafc",
                "text": "#dfe7f5",
                "subtext": "#94a3b8",
                "primary": "#1d4ed8",
                "primary_soft": "#22d3ee",
                "success": "#10b981",
                "success_text": "#03120d",
                "danger": "#ef4444",
                "danger_text": "#fff1f2",
                "button_secondary": "#1f2937",
                "button_secondary_text": "#c7d2fe",
                "button_green": "#1f3b34",
                "button_green_text": "#a7f3d0",
                "progress": "#60a5fa",
                "status": "#7dd3fc",
                "check_fg": "#e2e8f0",
                "border": "#1f2937",
            },
            "blank": {
                "bg": "#ffffff",
                "panel": "#f3f4f6",
                "panel_alt": "#ffffff",
                "title": "#111827",
                "text": "#111827",
                "subtext": "#4b5563",
                "primary": "#2563eb",
                "primary_soft": "#93c5fd",
                "success": "#22c55e",
                "success_text": "#ffffff",
                "danger": "#ef4444",
                "danger_text": "#ffffff",
                "button_secondary": "#e5e7eb",
                "button_secondary_text": "#111827",
                "button_green": "#eafaf0",
                "button_green_text": "#14532d",
                "progress": "#2563eb",
                "status": "#1d4ed8",
                "check_fg": "#111827",
                "border": "#d1d5db",
            },
            "system": {
                "bg": "#f5f5f5",
                "panel": "#ffffff",
                "panel_alt": "#f5f5f5",
                "title": "#1f2937",
                "text": "#1f2937",
                "subtext": "#6b7280",
                "primary": "#3b82f6",
                "primary_soft": "#93c5fd",
                "success": "#2ecc71",
                "success_text": "#ffffff",
                "danger": "#e74c3c",
                "danger_text": "#ffffff",
                "button_secondary": "#e5e7eb",
                "button_secondary_text": "#111827",
                "button_green": "#dcfce7",
                "button_green_text": "#166534",
                "progress": "#3b82f6",
                "status": "#1d4ed8",
                "check_fg": "#1f2937",
                "border": "#d1d5db",
            },
        }

        self.url_var = tk.StringVar()
        self.dir_var = tk.StringVar(value=self.default_download_dir)
        self.status_var = tk.StringVar(value="Aguardando...")
        self.progress_var = tk.IntVar(value=0)
        self.use_selenium = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self.root, bg="#111827", fg="#f8fafc", activebackground="#1d4ed8", activeforeground="#ffffff", relief="flat")
        self.root.config(menu=menubar)

        tools_menu = tk.Menu(menubar, tearoff=0, bg="#111827", fg="#f8fafc", activebackground="#1d4ed8", activeforeground="#ffffff")
        tools_menu.add_command(label="Configurar", command=self.configure_default_directory)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)

        view_menu = tk.Menu(menubar, tearoff=0, bg="#111827", fg="#f8fafc", activebackground="#1d4ed8", activeforeground="#ffffff")
        view_menu.add_radiobutton(label="Dark", value="dark", variable=self.theme_var, command=lambda: self.apply_theme("dark"))
        view_menu.add_radiobutton(label="Blank", value="blank", variable=self.theme_var, command=lambda: self.apply_theme("blank"))
        view_menu.add_radiobutton(label="Sistema", value="system", variable=self.theme_var, command=lambda: self.apply_theme("system"))
        menubar.add_cascade(label="Exibir", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0, bg="#111827", fg="#f8fafc", activebackground="#1d4ed8", activeforeground="#ffffff")
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Ajuda", menu=help_menu)

        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            self.main_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg=self.themes[self.current_theme]["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=18, pady=18)

        theme = self.themes[self.current_theme]

        title_label = tk.Label(
            self.main_frame,
            text="Downloader de Imagens",
            font=("Arial", 18, "bold"),
            fg=theme["title"],
            bg=theme["bg"]
        )
        title_label.pack(anchor="w", pady=(0, 18))

        accent_line = tk.Frame(self.main_frame, bg=theme["primary_soft"], height=3)
        accent_line.pack(fill="x", pady=(0, 14))

        card_url = tk.Frame(self.main_frame, bg=theme["panel"], padx=10, pady=10, bd=0, highlightthickness=1, highlightbackground=theme["primary"])
        card_url.pack(fill="x", pady=(0, 12))
        tk.Label(card_url, text="Link do Site:", font=("Arial", 10, "bold"), fg=theme["text"], bg=theme["panel"]).pack(anchor="w", pady=(0, 6))
        frame_url = tk.Frame(card_url, bg=theme["panel"])
        frame_url.pack(fill="x")
        self.entry_url = tk.Entry(
            frame_url,
            textvariable=self.url_var,
            width=70,
            font=("Arial", 10),
            bg=theme["panel_alt"],
            fg=theme["title"],
            insertbackground=theme["title"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme["primary"],
            highlightcolor=theme["primary_soft"],
            bd=0,
        )
        self.btn_clear_url = tk.Button(
            frame_url,
            text="🗑️ Limpar",
            command=self.clear_url,
            bg=theme["button_secondary"],
            fg=theme["button_secondary_text"],
            activebackground="#334155" if self.current_theme == "dark" else "#d1d5db",
            activeforeground=theme["button_secondary_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=16,
            pady=8,
        )
        self.btn_clear_url.pack(side="right", padx=(8, 0))
        self.set_button_hover(self.btn_clear_url, theme["button_secondary"], "#334155" if self.current_theme == "dark" else "#d1d5db")
        self.entry_url.pack(side="left", fill="x", expand=True)

        card_dir = tk.Frame(self.main_frame, bg=theme["panel"], padx=10, pady=10, bd=0, highlightthickness=1, highlightbackground=theme["success"])
        card_dir.pack(fill="x", pady=(0, 12))
        tk.Label(card_dir, text="Salvar em:", font=("Arial", 10, "bold"), fg=theme["text"], bg=theme["panel"]).pack(anchor="w", pady=(0, 6))
        frame_dir = tk.Frame(card_dir, bg=theme["panel"])
        frame_dir.pack(fill="x")

        self.entry_dir = tk.Entry(
            frame_dir,
            textvariable=self.dir_var,
            width=55,
            font=("Arial", 10),
            bg=theme["panel_alt"],
            fg=theme["title"],
            insertbackground=theme["title"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme["border"],
            highlightcolor=theme["primary_soft"],
            bd=0,
        )

        self.btn_browse = tk.Button(
            frame_dir,
            text="📁 Procurar...",
            command=self.browse_directory,
            bg=theme["button_green"],
            fg=theme["button_green_text"],
            activebackground="#2b5c52" if self.current_theme == "dark" else "#d1fae5",
            activeforeground=theme["button_green_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=8,
        )
        self.btn_browse.pack(side="right", padx=(8, 0))
        self.set_button_hover(self.btn_browse, theme["button_green"], "#2b5c52" if self.current_theme == "dark" else "#d1fae5")

        self.btn_clear_dir = tk.Button(
            frame_dir,
            text="🗑️ Limpar",
            command=self.clear_directory,
            bg=theme["button_secondary"],
            fg=theme["button_secondary_text"],
            activebackground="#334155" if self.current_theme == "dark" else "#d1d5db",
            activeforeground=theme["button_secondary_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=16,
            pady=8,
        )
        self.btn_clear_dir.pack(side="right", padx=(8, 0))
        self.set_button_hover(self.btn_clear_dir, theme["button_secondary"], "#334155" if self.current_theme == "dark" else "#d1d5db")
        self.entry_dir.pack(side="left", fill="x", expand=True)

        frame_mode = tk.Frame(self.main_frame, bg=theme["panel"], padx=10, pady=10, highlightthickness=1, highlightbackground=theme["primary"])
        frame_mode.pack(fill="x", pady=(0, 12), anchor="w")

        self.chk_selenium = tk.Checkbutton(
            frame_mode,
            text="Usar modo completo (Selenium)",
            variable=self.use_selenium,
            font=("Arial", 9),
            bg=theme["panel"],
            fg=theme["check_fg"],
            activebackground=theme["panel"],
            selectcolor=theme["panel_alt"],
            highlightthickness=0,
        )
        self.chk_selenium.pack(anchor="w")

        info_label = tk.Label(
            frame_mode,
            text="✓ Modo Rápido: sites simples\n✓ Modo Completo: sites protegidos e com lazy-loading",
            font=("Arial", 9),
            fg=theme["subtext"],
            bg=theme["panel"],
            justify="left"
        )
        info_label.pack(anchor="w", pady=(6, 0))

        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            orient="horizontal",
            length=560,
            mode="determinate",
            variable=self.progress_var,
            style="Dark.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(10, 12))

        self.lbl_status = tk.Label(self.main_frame, textvariable=self.status_var, fg=theme["status"], bg=theme["bg"], font=("Arial", 10, "bold"))
        self.lbl_status.pack(anchor="w", pady=(0, 10))

        frame_actions = tk.Frame(self.main_frame, bg=theme["bg"])
        frame_actions.pack(fill="x", pady=(8, 0))

        self.btn_download = tk.Button(
            frame_actions,
            text="⬇️ Iniciar Download",
            bg=theme["success"],
            fg=theme["success_text"],
            activebackground="#34d399" if self.current_theme == "dark" else "#22c55e",
            activeforeground=theme["success_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            command=self.start_download,
        )
        self.btn_download.pack(side="left", padx=(0, 12))
        self.set_button_hover(self.btn_download, theme["success"], "#34d399" if self.current_theme == "dark" else "#22c55e")

        self.btn_exit = tk.Button(
            frame_actions,
            text="✖️ Encerrar",
            bg=theme["danger"],
            fg=theme["danger_text"],
            activebackground="#f87171" if self.current_theme == "dark" else "#dc2626",
            activeforeground=theme["danger_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 12, "bold"),
            padx=18,
            pady=10,
            command=self.exit_application,
        )
        self.btn_exit.pack(side="left")
        self.set_button_hover(self.btn_exit, theme["danger"], "#f87171" if self.current_theme == "dark" else "#dc2626")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Horizontal.TProgressbar", background=theme["progress"], troughcolor=theme["panel"], lightcolor=theme["progress"], darkcolor=theme["progress"])

    def apply_theme(self, theme_name):
        if theme_name not in self.themes:
            return

        self.current_theme = theme_name
        self.theme_var.set(theme_name)
        self.root.configure(bg=self.themes[theme_name]["bg"])
        self.root.option_add("*Background", self.themes[theme_name]["bg"])
        self.root.option_add("*Foreground", self.themes[theme_name]["text"])

        if hasattr(self, "main_frame") and self.main_frame.winfo_exists():
            self.main_frame.destroy()

        self.main_frame = tk.Frame(self.root, bg=self.themes[theme_name]["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=18, pady=18)
        self.update_theme_widgets()

    def update_theme_widgets(self):
        theme = self.themes[self.current_theme]

        title_label = tk.Label(
            self.main_frame,
            text="Downloader de Imagens",
            font=("Arial", 18, "bold"),
            fg=theme["title"],
            bg=theme["bg"]
        )
        title_label.pack(anchor="w", pady=(0, 18))

        accent_line = tk.Frame(self.main_frame, bg=theme["primary_soft"], height=3)
        accent_line.pack(fill="x", pady=(0, 14))

        card_url = tk.Frame(self.main_frame, bg=theme["panel"], padx=10, pady=10, bd=0, highlightthickness=1, highlightbackground=theme["primary"])
        card_url.pack(fill="x", pady=(0, 12))
        tk.Label(card_url, text="Link do Site:", font=("Arial", 10, "bold"), fg=theme["text"], bg=theme["panel"]).pack(anchor="w", pady=(0, 6))
        frame_url = tk.Frame(card_url, bg=theme["panel"])
        frame_url.pack(fill="x")
        self.entry_url = tk.Entry(
            frame_url,
            textvariable=self.url_var,
            width=70,
            font=("Arial", 10),
            bg=theme["panel_alt"],
            fg=theme["title"],
            insertbackground=theme["title"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme["primary"],
            highlightcolor=theme["primary_soft"],
            bd=0,
        )
        self.entry_url.pack(side="left", fill="x", expand=True)
        self.btn_clear_url = tk.Button(
            frame_url,
            text="🗑️ Limpar",
            width=12,
            command=self.clear_url,
            bg=theme["button_secondary"],
            fg=theme["button_secondary_text"],
            activebackground="#334155" if self.current_theme == "dark" else "#d1d5db",
            activeforeground=theme["button_secondary_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=8,
            pady=8,
        )
        self.btn_clear_url.pack(side="right", padx=(8, 0))
        self.set_button_hover(self.btn_clear_url, theme["button_secondary"], "#334155" if self.current_theme == "dark" else "#d1d5db")

        card_dir = tk.Frame(self.main_frame, bg=theme["panel"], padx=10, pady=10, bd=0, highlightthickness=1, highlightbackground=theme["success"])
        card_dir.pack(fill="x", pady=(0, 12))
        tk.Label(card_dir, text="Salvar em:", font=("Arial", 10, "bold"), fg=theme["text"], bg=theme["panel"]).pack(anchor="w", pady=(0, 6))
        frame_dir = tk.Frame(card_dir, bg=theme["panel"])
        frame_dir.pack(fill="x")

        self.entry_dir = tk.Entry(
            frame_dir,
            textvariable=self.dir_var,
            width=55,
            font=("Arial", 10),
            bg=theme["panel_alt"],
            fg=theme["title"],
            insertbackground=theme["title"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme["border"],
            highlightcolor=theme["primary_soft"],
            bd=0,
        )
        self.entry_dir.pack(side="left", fill="x", expand=True)

        self.btn_browse = tk.Button(
            frame_dir,
            text="📁 Procurar...",
            command=self.browse_directory,
            bg=theme["button_green"],
            fg=theme["button_green_text"],
            activebackground="#2b5c52" if self.current_theme == "dark" else "#d1fae5",
            activeforeground=theme["button_green_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=8,
        )
        self.btn_browse.pack(side="right", padx=(8, 0))
        self.set_button_hover(self.btn_browse, theme["button_green"], "#2b5c52" if self.current_theme == "dark" else "#d1fae5")

        self.btn_clear_dir = tk.Button(
            frame_dir,
            text="🗑️ Limpar",
            width=12,
            command=self.clear_directory,
            bg=theme["button_secondary"],
            fg=theme["button_secondary_text"],
            activebackground="#334155" if self.current_theme == "dark" else "#d1d5db",
            activeforeground=theme["button_secondary_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=8,
            pady=8,
        )
        self.btn_clear_dir.pack(side="right", padx=(8, 0))
        self.set_button_hover(self.btn_clear_dir, theme["button_secondary"], "#334155" if self.current_theme == "dark" else "#d1d5db")

        frame_mode = tk.Frame(self.main_frame, bg=theme["panel"], padx=10, pady=10, highlightthickness=1, highlightbackground=theme["primary"])
        frame_mode.pack(fill="x", pady=(0, 12), anchor="w")

        self.chk_selenium = tk.Checkbutton(
            frame_mode,
            text="Usar modo completo (Selenium)",
            variable=self.use_selenium,
            font=("Arial", 9),
            bg=theme["panel"],
            fg=theme["check_fg"],
            activebackground=theme["panel"],
            selectcolor=theme["panel_alt"],
            highlightthickness=0,
        )
        self.chk_selenium.pack(anchor="w")

        info_label = tk.Label(
            frame_mode,
            text="✓ Modo Rápido: sites simples\n✓ Modo Completo: sites protegidos e com lazy-loading",
            font=("Arial", 9),
            fg=theme["subtext"],
            bg=theme["panel"],
            justify="left"
        )
        info_label.pack(anchor="w", pady=(6, 0))

        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            orient="horizontal",
            length=560,
            mode="determinate",
            variable=self.progress_var,
            style="Dark.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=(10, 12))

        self.lbl_status = tk.Label(self.main_frame, textvariable=self.status_var, fg=theme["status"], bg=theme["bg"], font=("Arial", 10, "bold"))
        self.lbl_status.pack(anchor="w", pady=(0, 10))

        frame_actions = tk.Frame(self.main_frame, bg=theme["bg"])
        frame_actions.pack(fill="x", pady=(8, 0))

        self.btn_download = tk.Button(
            frame_actions,
            text="⬇️ Iniciar Download",
            bg=theme["success"],
            fg=theme["success_text"],
            activebackground="#34d399" if self.current_theme == "dark" else "#22c55e",
            activeforeground=theme["success_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            command=self.start_download,
        )
        self.btn_download.pack(side="left", padx=(0, 12))
        self.set_button_hover(self.btn_download, theme["success"], "#34d399" if self.current_theme == "dark" else "#22c55e")

        self.btn_exit = tk.Button(
            frame_actions,
            text="✖️ Encerrar",
            bg=theme["danger"],
            fg=theme["danger_text"],
            activebackground="#f87171" if self.current_theme == "dark" else "#dc2626",
            activeforeground=theme["danger_text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 12, "bold"),
            padx=18,
            pady=10,
            command=self.exit_application,
        )
        self.btn_exit.pack(side="left")
        self.set_button_hover(self.btn_exit, theme["danger"], "#f87171" if self.current_theme == "dark" else "#dc2626")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Horizontal.TProgressbar", background=theme["progress"], troughcolor=theme["panel"], lightcolor=theme["progress"], darkcolor=theme["progress"])

    def load_default_directory(self):
        if not os.path.exists(self.config_path):
            return ""

        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data.get("default_download_dir", "") if isinstance(data, dict) else ""
        except Exception:
            return ""

    def save_default_directory(self, directory):
        try:
            with open(self.config_path, "w", encoding="utf-8") as file:
                json.dump({"default_download_dir": directory}, file, ensure_ascii=False)
        except Exception:
            messagebox.showerror("Erro", "Não foi possível salvar a pasta padrão.")

    def configure_default_directory(self):
        selected = filedialog.askdirectory(title="Selecione a pasta padrão para salvar imagens")
        if not selected:
            return

        self.default_download_dir = selected
        self.save_default_directory(selected)
        self.dir_var.set(selected)
        messagebox.showinfo("Configuração", f"Pasta padrão definida em:\n{selected}")

    def show_about(self):
        messagebox.showinfo(
            "About",
            "Downloader de Imagens\n\nVersão: 1.0\nDesenvolvido para baixar imagens de páginas web com suporte a modos rápidos e Selenium."
        )

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Selecione a pasta para salvar as imagens")
        if directory:
            self.dir_var.set(directory)

    def clear_url(self):
        self.url_var.set("")
        self.entry_url.focus_set()

    def clear_directory(self):
        self.dir_var.set("")
        self.entry_dir.focus_set()

    def set_button_hover(self, button, base_bg, hover_bg):
        button.configure(bg=base_bg, activebackground=hover_bg)
        button.bind("<Enter>", lambda event, b=button, color=hover_bg: b.configure(bg=color))
        button.bind("<Leave>", lambda event, b=button, color=base_bg: b.configure(bg=color))

    def exit_application(self):
        self.root.destroy()

    def open_directory(self, directory_path):
        if not directory_path or not os.path.isdir(directory_path):
            return

        try:
            if os.name == "nt":
                os.startfile(directory_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", directory_path])
            else:
                subprocess.Popen(["xdg-open", directory_path])
        except Exception:
            pass

    def start_download(self):
        url = self.url_var.get().strip()
        save_dir = self.dir_var.get().strip()

        if not url:
            messagebox.showwarning("Atenção", "Informe o endereço no campo 'Link do Site' antes de iniciar o download.")
            return

        if not save_dir:
            messagebox.showwarning("Atenção", "Informe a pasta de destino em 'Salvar em' antes de iniciar o download.")
            return

        self.dir_var.set(save_dir)

        self.btn_download.config(state="disabled")
        self.btn_browse.config(state="disabled")
        self.btn_clear_url.config(state="disabled")
        self.btn_clear_dir.config(state="disabled")
        self.progress_var.set(0)

        # Verifica qual modo usar
        if self.use_selenium.get():
            # MODO COMPLETO (Selenium)
            self.status_var.set("Iniciando modo completo (Selenium)...")
            try:
                from downloader_selenium import ImageDownloaderSelenium
                downloader = ImageDownloaderSelenium(
                    url=url, 
                    save_dir=save_dir, 
                    on_status=self.update_status, 
                    on_progress=self.update_progress, 
                    on_complete=self.download_finished
                )
            except ImportError:
                messagebox.showerror("Erro", "Selenium não instalado!\n\nInstale com:\npip install selenium webdriver-manager")
                self.reset_ui()
                return
        else:
            # MODO RÁPIDO (Requests + BeautifulSoup)
            from downloader import ImageDownloader
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
            self.open_directory(save_dir)

    def reset_ui(self):
        self.btn_download.config(state="normal")
        self.btn_browse.config(state="normal")
        self.btn_clear_url.config(state="normal")
        self.btn_clear_dir.config(state="normal")
        self.status_var.set("Aguardando...")
        self.progress_var.set(0)  # Zera a barra de progresso