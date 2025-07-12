import requests
from bs4 import BeautifulSoup
import os
import datetime
import time

# UPRAVENO: Cesty ke složkám a souborům
DIR = "nabidky_prace"
JOBS_FILE = os.path.join(DIR, "jobs.html")      # UPRAVENO
ID_FILE = os.path.join(DIR, "ids.txt")         # UPRAVENO
LOG_FILE = os.path.join(DIR, "error_log.txt")  # UPRAVENO

# NOVÉ: Vytvoření složky pokud neexistuje
os.makedirs(DIR, exist_ok=True)                # UPRAVENO

def log_error(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()} - {msg}\n")    # UPRAVENO

def get_page(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        else:
            log_error(f"Chyba HTTP {response.status_code} u {url}")
            return None
    except Exception as e:
        log_error(f"Výjimka při načítání {url}: {e}")
        return None

def get_id_from(url):
    # UPRAVENO: Ošetření různých struktur URL
    try:
        return url.split("/")[4]
    except Exception:
        return url

def main():
    # UPRAVENO: Použití konkrétní URL s výsledky hledání
    url = "https://www.jobs.cz/prace/?q%5B%5D=junior%20python"   # UPRAVENO

    soup = get_page(url)
    if not soup:
        print("Nepodařilo se načíst hlavní stránku.")
        return

    # UPRAVENO: Selektor pro odkazy na pracovní nabídky
    job_links = soup.find_all('a', class_='link-primary SearchResultCard__titleLink')  # UPRAVENO
    urls = [a.get('href') for a in job_links if a.get('href')]
    if not urls:
        print("Nebyly nalezeny žádné odkazy na nabídky.")
        return

    # NOVÉ: Načtení již zpracovaných ID
    if os.path.exists(ID_FILE):
        with open(ID_FILE, "r", encoding="utf-8") as f:
            ids = set(line.strip() for line in f)
    else:
        ids = set()

    count = 0
    for link in urls:
        id = get_id_from(link)
        if id in ids:
            continue

        # NOVÉ: Pauza mezi požadavky (šetrnost k serveru)
        time.sleep(2)

        offer_soup = get_page(link)
        if not offer_soup:
            continue

        # UPRAVENO: Uložení celého textu inzerátu jako fallback
        text = offer_soup.get_text(separator="\n", strip=True)

        # UPRAVENO: Zápis do jednoho souboru, každý inzerát oddělen
        with open(JOBS_FILE, "a", encoding="utf-8") as f:
            f.write("################################\n") #ODDĚLOVAČ
            f.write(f"ID: {id}\nURL: {link}\n{text}\n\n")

        # UPRAVENO: Zápis ID, aby se inzerát nestahoval znovu
        with open(ID_FILE, "a", encoding="utf-8") as f:
            f.write(id + "\n")
        ids.add(id)
        count += 1

    print(f"Hotovo! Uloženo {count} nových nabídek.")   # UPRAVENO

if __name__ == "__main__":
    main()
