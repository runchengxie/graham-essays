import urllib.request
from urllib.parse import urljoin
import time
import os.path
import html2text
import regex as re
from htmldate import find_date
import csv
import requests
from bs4 import BeautifulSoup
import os

"""
Download a collection of Paul Graham essays in EPUB & Markdown.
"""

h = html2text.HTML2Text()
h.ignore_images = True
h.ignore_tables = True
h.escape_all = True
h.reference_links = True
h.mark_code = True

ART_NO = 0  # Initialize to 0 so the first entry is 001
FILE = "./essays.csv"

if os.path.isfile(FILE):
    os.remove(FILE)

if not os.path.exists("./essays"):
    os.makedirs("./essays")


def parse_main_page(base_url: str, articles_url: str):
    assert base_url.endswith(
        "/"), f"Base URL must end with a slash: {base_url}"
    response = requests.get(base_url + articles_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all relevant 'td' elements
    td_cells = soup.select("table > tr > td > table > tr > td")
    chapter_links = []

    for td in td_cells:
        # use the heuristic that page links are an <a> inside a <font> with a small (bullet) image alongside
        img = td.find("img")
        if img and int(img.get("width", 0)) <= 15 and int(img.get("height", 0)) <= 15:
            a_tag = td.find("font").find("a") if td.find("font") else None
            if a_tag:
                chapter_links.append(
                    {"link": urljoin(
                        base_url, a_tag["href"]), "title": a_tag.text}
                )

    return chapter_links


toc = list(reversed(parse_main_page("https://paulgraham.com/", "articles.html")))

# rss = feedparser.parse("http://www.aaronsw.com/2002/feeds/pgessays.rss")
# toc = reversed(rss.entries)


def update_links_in_md(joined):
    matches = re.findall(rb"\[\d+\]", joined)

    if not matches:
        return joined

    for match in set(matches):

        def update_links(match):
            counter[0] += 1
            note_name = f"{title}_note{note_number}"
            if counter[0] == 1:
                return bytes(f"[{note_number}](#{note_name})", "utf-8")
            elif counter[0] == 2:
                return bytes(f"<a name={note_name}>[{note_number}]</a>", "utf-8")

        counter = [0]

        note_number = int(match.decode().strip("[]"))
        match_regex = match.replace(b"[", rb"\[").replace(b"]", rb"\]")

        joined = re.sub(match_regex, update_links, joined)

    return joined


# Write the header to the CSV file only once
with open(FILE, "a+", newline="\n") as f:
    fieldnames = ["Article no.", "Title", "Date", "URL"]
    csvwriter = csv.DictWriter(f, fieldnames=fieldnames)
    csvwriter.writeheader()

for entry in toc:
    ART_NO += 1
    URL = entry["link"]
    if "http://www.paulgraham.com/https://" in URL:
        URL = URL.replace("http://www.paulgraham.com/https://", "https://")
    TITLE = entry["title"]

    try:
        try:
            with urllib.request.urlopen(URL) as website:
                content = website.read().decode("utf-8")
        except UnicodeDecodeError:
            with urllib.request.urlopen(URL) as website:
                content = website.read().decode("latin-1")

        parsed = h.handle(content)
        title = "_".join(TITLE.split(" ")).lower()
        title = re.sub(r"[\W\s]+", "", title)
        DATE = find_date(URL)
        with open(f"./essays/{str(ART_NO).zfill(3)}_{title}.md", "wb+") as file:
            file.write(f"# {str(ART_NO).zfill(3)} {TITLE}\n\n".encode())
            parsed = parsed.replace("[](index.html)  \n  \n", "")

            parsed = [
                (
                    p.replace("\n", " ")
                    if re.match(r"^[\p{Z}\s]*(?:[^\p{Z}\s][\p{Z}\s]*){5,100}$", p)
                    else "\n" + p + "\n"
                )
                for p in parsed.split("\n")
            ]

            encoded = " ".join(parsed).encode()
            update_with_links = update_links_in_md(encoded)
            file.write(update_with_links)

            print(f"✅ {str(ART_NO).zfill(3)} {TITLE}")

            with open(FILE, "a+", newline="\n") as f:
                csvwriter = csv.writer(
                    f, quoting=csv.QUOTE_MINIMAL, delimiter=",", quotechar='"'
                )

                line = [str(ART_NO).zfill(3), TITLE, DATE, URL]

                csvwriter.writerow(line)

    except Exception as e:
        print(f"❌ {str(ART_NO).zfill(3)} {entry['title']}, ({e})")
    time.sleep(0.05)  # half sec/article is ~2min, be nice with servers!
