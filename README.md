# 🖼️ Image Downloader - Berthain

Uma aplicação desktop em Python para baixar automaticamente todas as imagens de uma página web. Desenvolvida com interface gráfica intuitiva usando Tkinter, a aplicação suporta múltiplos formatos de imagem e possui dois modos de operação para lidar com sites simples e sites protegidos contra scraping.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey)

## ✨ Funcionalidades

-  **Download automático** de todas as imagens de qualquer página web
- 📁 **Escolha da pasta** de destino através de um navegador de arquivos
- ️ **Suporte a múltiplos formatos**: JPEG, PNG, GIF, BMP, AVIF, WebP, SVG e ICO
- 📊 **Barra de progresso** em tempo real com reset automático ao final
- 🤖 **Dois modos de operação**:
  - **Modo Rápido**: Usa `requests` + `BeautifulSoup` (ideal para sites simples)
  - **Modo Completo (Selenium)**: Usa navegador Chrome headless (para sites protegidos ou com lazy-loading)
- 🔒 **Headers realistas** para simular um navegador e evitar bloqueios
- 📜 **Suporte a lazy-loading** (imagens carregadas dinamicamente ao rolar a página)
- 🛡️ **Tratamento de erros** robusto (URLs quebradas, arquivos duplicados, caracteres inválidos)
- 🧵 **Multithreading**: Interface responsiva durante o download
- 🔄 **Detecção automática** de extensões via MIME type e URL
- ☑️ **Checkbox intuitiva** para alternar entre os modos de download

## 📋 Pré-requisitos

- Python 3.8 ou superior (recomendado 3.11+)
- pip (gerenciador de pacotes do Python)
- Google Chrome instalado (necessário para o modo Selenium)
- Windows, macOS ou Linux

## 🚀 Instalação

### 1. Clone ou baixe o projeto

```bash
git clone https://github.com/Berthain/bot-get-pictures.git
cd bot-get-pictures

### 2. Instale as dependências

Dependências básicas (Modo Rápido):
