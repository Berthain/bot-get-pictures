# main.py
import tkinter as tk
from gui import ImageDownloaderApp

def main():
    root = tk.Tk()
    app = ImageDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()