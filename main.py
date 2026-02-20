import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# Les pages que nous voulons surveiller
URLS = [
    "https://mainichi.jp/incident/",
    "https://mainichi.jp/shakai/"
]

def get_articles():
    all_articles = {} # On utilise un dictionnaire pour bloquer les doublons (l'URL est la clé)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for url in URLS:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Le Mainichi utilise souvent des balises 'article' ou des listes avec des liens
            # On cherche tous les liens qui contiennent "/articles/" dans l'URL
            for link in soup.find_all("a", href=True):
                href = link['href']
                
                # Nettoyage de l'URL
                if href.startswith("/articles/"):
                    full_url = "https://mainichi.jp" + href
                elif "mainichi.jp/articles/" in href:
                    full_url = href
                else:
                    continue

                # Extraction du titre
                title = link.get_text().strip()
                
                # On ne garde que si on a un vrai titre et si on n'a pas déjà vu cette URL
                if len(title) > 15 and full_url not in all_articles:
                    all_articles[full_url] = {
                        "title": title,
                        "link": full_url,
                        "date": datetime.now(timezone.utc)
                    }
        except Exception as e:
            print(f"Erreur sur {url}: {e}")
            
    return all_articles

def create_rss(articles):
    fg = FeedGenerator()
    fg.title('Mainichi - Incident & Shakai')
    fg.description('Flux combiné et dédoublonné via GitHub Actions')
    fg.link(href='https://mainichi.jp', rel='alternate')
    fg.language('ja')

    # On ajoute chaque article unique au flux
    for url, data in articles.items():
        fe = fg.add_entry()
        fe.title(data['title'])
        fe.link(href=data['link'])
        fe.guid(data['link'], permalink=True)
        fe.pubDate(data['date'])

    fg.rss_file('rss.xml')

if __name__ == "__main__":
    print("Démarrage de la récupération...")
    articles_uniques = get_articles()
    print(f"{len(articles_uniques)} articles uniques trouvés.")
    create_rss(articles_uniques)
    print("Fichier rss.xml généré.")
