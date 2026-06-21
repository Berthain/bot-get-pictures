# 🖼️ Image Downloader - Berthain

Uma aplicação desktop em Python para baixar automaticamente todas as imagens de uma página web. Desenvolvida com interface gráfica intuitiva usando Tkinter, a aplicação suporta múltiplos formatos de imagem e possui um modo especial para sites protegidos contra scraping.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey)

## ✨ Funcionalidades

- 🌐 **Download automático** de todas as imagens de qualquer página web
- 📁 **Escolha da pasta** de destino através de um navegador de arquivos
- 🖼️ **Suporte a múltiplos formatos**: JPEG, PNG, GIF, BMP, AVIF, WebP, SVG e ICO
- 📊 **Barra de progresso** em tempo real
- 🤖 **Dois modos de operação**:
  - **Modo Rápido**: Usa `requests` + `BeautifulSoup` (ideal para a maioria dos sites)
  - **Modo Completo**: Usa `Selenium` com navegador headless (para sites protegidos ou com lazy-loading)
- 🔒 **Headers realistas** para simular um navegador e evitar bloqueios
- 📜 **Suporte a lazy-loading** (imagens carregadas dinamicamente)
- 🛡️ **Tratamento de erros** robusto (URLs quebradas, arquivos duplicados, etc.)
- 🧵 **Multithreading**: Interface responsiva durante o download

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)
- Google Chrome instalado (apenas se for usar o modo Selenium)

## 🚀 Instalação

### 1. Clone ou baixe o projeto

```bash
git clone https://github.com/seu-usuario/image-downloader.git
cd image-downloader