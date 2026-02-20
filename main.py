import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# Les deux pages que vous voulez fusionner
URLS = [
    "https://mainichi.jp/incident/",
    "https://mainichi.jp/shakai/"
]

def get_articles():
    # Ce dictionnaire va contenir TOUS les articles uniques
    # La clé sera l'URL, ce qui empêche techniquement les doublons
    articles_uniques = {} 
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for url in URLS:
        print(f"Analyse de la page : {url}")
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # On cherche tous les liens sur la page
            for link in soup.find_all("a", href=True):
                href = link['href']
                title = link.get_text().strip()

                # On ne prend que les vrais articles du Mainichi
                if "/articles/" in href:
                    # On transforme le lien relatif en lien complet
                    if href.startswith("/"):
                        full_url = "https://mainichi.jp" + href
                    else:
                        full_url = href
                    
                    # CONDITIONS POUR AJOUTER :
                    # 1. Le titre ne doit pas être vide (ex: une image)
                    # 2. Le titre doit être assez long (pour éviter les menus "Aide", "Contact")
                    # 3. L'URL ne doit pas déjà être dans notre dictionnaire
                    if len(title) > 20 and full_url not in articles_uniques:
                        articles_uniques[full_url] = {
                            "title": title,
                            "link": full_url,
                            "date": datetime.now(timezone.utc)
                        }
                        print(f"  ✅ Ajouté : {title[:50]}...")
        except Exception as e:
            print(f"Erreur sur {url}: {e}")
            
    return articles_uniques

def create_rss(articles):
    fg = FeedGenerator()
    fg.title('Mainichi - Incident et Shakai (Complet)')
    fg.description('Tous les articles de Incident et Shakai, sans doublons.')
    fg.link(href='https://mainichi.jp', rel='alternate')
    fg.language('ja')

    # On transforme notre dictionnaire en liste pour le flux RSS
    for url, data in articles.items():
        fe = fg.add_entry()
        fe.title(data['title'])
        fe.link(href=data['link'])
        fe.guid(data['link'], permalink=True)
        fe.pubDate(data['date'])

    fg.rss_file('rss.xml')

if __name__ == "__main__":
    tous_les_articles = get_articles()
    print(f"Total récupéré : {len(tous_les_articles)} articles uniques.")
    create_rss(tous_les_articles)
