# scraper/metadata_extractor.py

from bs4 import BeautifulSoup

def extract_metadata(soup: BeautifulSoup):
    """
    (En archivo separado) Extrae metadatos de un objeto BeautifulSoup.
    
    Incluye:
    - Título
    - Meta tags (description, keywords)
    - Open Graph tags (og:)
    """
    
    # 1. Título de la página
    title = soup.title.string.strip() if soup.title else "No Title Found"

    # 2. Meta tags relevantes
    meta_tags = {}
    
    # description y keywords
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        meta_tags['description'] = meta_desc.get('content', '')
        
    meta_keys = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keys:
        meta_tags['keywords'] = meta_keys.get('content', '')

    # Open Graph (og:)
    og_tags = soup.find_all('meta', property=lambda p: p and p.startswith('og:'))
    for tag in og_tags:
        meta_tags[tag['property']] = tag.get('content', '')
        
    return {
        "title": title,
        "meta_tags": meta_tags
    }