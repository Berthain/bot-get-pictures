# utils.py

# Mapeamento de tipos MIME para extensões
MIME_TO_EXT = {
    'image/jpeg': '.jpg', 'image/jpg': '.jpg',
    'image/png': '.png', 'image/gif': '.gif',
    'image/bmp': '.bmp', 'image/avif': '.avif',
    'image/webp': '.webp', 'image/svg+xml': '.svg',
    'image/x-icon': '.ico', 'image/vnd.microsoft.icon': '.ico'
}

# Extensões que consideramos como imagens válidas
ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.avif', '.webp', '.svg', '.ico'}

# Extensões de scripts/páginas que devemos ignorar se aparecerem na URL
IGNORE_EXTS = {'.php', '.html', '.htm', '.asp', '.aspx', '.jsp', '.cgi'}

def sanitize_filename(filename):
    """Remove caracteres inválidos do nome do arquivo."""
    return "".join(c for c in filename if c.isalnum() or c in ('.', '-', '_')).rstrip()

def get_image_extension(url_path, content_type):
    """Determina a extensão correta com base na URL e no cabeçalho HTTP."""
    import os
    path = url_path
    if path.endswith('/'): path = path[:-1]
    url_ext = os.path.splitext(path)[1].lower()
    
    if url_ext in IGNORE_EXTS:
        url_ext = ''

    if url_ext in ALLOWED_EXTS:
        return url_ext
    elif content_type in MIME_TO_EXT:
        return MIME_TO_EXT[content_type]
    elif content_type.startswith('image/'):
        return '.' + content_type.split('/')[-1]
    
    return None