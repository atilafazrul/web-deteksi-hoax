import re
import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

def fetch_html_from_url(url: str, timeout: int = 12) -> str:
    """Download web page HTML safely with browser-like headers."""
    # Ensure scheme
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=")[-1].split(";")[0].strip()
        raw_data = response.read()
        try:
            return raw_data.decode(charset, errors="replace")
        except Exception:
            return raw_data.decode("utf-8", errors="replace")

def extract_article_from_url(url: str, timeout: int = 12) -> dict:
    """
    Extract structured news content from an Indonesian or global news URL.
    Returns:
    {
        'url': url,
        'domain': domain,
        'title': title,
        'author': author,
        'date': date,
        'image': image_url,
        'full_text': str,
        'paragraphs': list[str],
        'sentences': list[str],
        'status': 'success' | 'error',
        'error_msg': str (if error)
    }
    """
    try:
        html = fetch_html_from_url(url, timeout=timeout)
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        soup = BeautifulSoup(html, "html.parser")

        # Check if URL is an index / category / homepage feed
        path_clean = parsed_url.path.strip("/")
        category_paths = {"", "world", "news", "indonesia", "nasional", "internasional", "sport", "sports", "tech", "technology", "business", "politics"}
        if path_clean.lower() in category_paths:
            return {
                "status": "error",
                "error_msg": (
                    f"Tautan '{url}' adalah halaman rubrik / kumpulan berita ('{path_clean or 'Beranda'}'), "
                    "bukan satu artikel berita spesifik. Silakan klik salah satu artikel di halaman tersebut, "
                    "lalu salin dan tempelkan tautan artikel berita tunggalnya."
                ),
                "url": url,
                "domain": domain
            }

        # 1. Clean out irrelevant tags
        for unwanted in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer", "aside"]):
            unwanted.decompose()

        # 2. Extract Metadata from OpenGraph / Meta tags
        og_title = soup.find("meta", property="og:title")
        meta_title = og_title["content"].strip() if og_title and og_title.get("content") else ""

        og_desc = soup.find("meta", property="og:description")
        meta_desc = og_desc["content"].strip() if og_desc and og_desc.get("content") else ""

        og_img = soup.find("meta", property="og:image")
        image_url = og_img["content"].strip() if og_img and og_img.get("content") else ""

        og_site = soup.find("meta", property="og:site_name")
        site_name = og_site["content"].strip() if og_site and og_site.get("content") else domain

        # Date & Author detection
        date_str = ""
        date_meta = (
            soup.find("meta", property="article:published_time") or
            soup.find("meta", attrs={"name": "pubdate"}) or
            soup.find("meta", attrs={"name": "date"}) or
            soup.find("time")
        )
        if date_meta:
            date_str = date_meta.get("content") or date_meta.get_text(strip=True) or ""

        author_str = ""
        author_meta = (
            soup.find("meta", attrs={"name": "author"}) or
            soup.find("meta", property="article:author")
        )
        if author_meta:
            author_str = author_meta.get("content") or author_meta.get_text(strip=True) or ""

        # Title detection
        h1_tag = soup.find("h1")
        title = ""
        if h1_tag:
            title = h1_tag.get_text(strip=True)
        elif meta_title:
            title = meta_title
        elif soup.title:
            title = soup.title.get_text(strip=True)

        # 3. Domain-specific content extractors
        body_node = None
        if "detik.com" in domain:
            body_node = soup.find("div", class_=re.compile(r"detail__body-text|itp_bodycontent"))
            if not date_str:
                d = soup.find("div", class_="detail__date")
                if d: date_str = d.get_text(strip=True)
            if not author_str:
                a = soup.find("div", class_="detail__author")
                if a: author_str = a.get_text(strip=True)

        elif "kompas.com" in domain:
            body_node = soup.find("div", class_="read__content")
            if not date_str:
                d = soup.find("div", class_="read__time")
                if d: date_str = d.get_text(strip=True)
            if not author_str:
                a = soup.find("div", class_="credit-title-name")
                if a: author_str = a.get_text(strip=True)

        elif "cnnindonesia.com" in domain:
            body_node = soup.find("div", class_=re.compile(r"detail-text|body-content"))

        elif "liputan6.com" in domain:
            body_node = soup.find("div", class_=re.compile(r"article-content-body"))

        elif "turnbackhoax.id" in domain:
            body_node = soup.find("div", class_=re.compile(r"entry-content"))
            if not date_str:
                t = soup.find("time", class_="entry-date")
                if t: date_str = t.get_text(strip=True)

        elif "antaranews.com" in domain:
            body_node = soup.find("div", class_="post-content")

        elif "tempo.co" in domain:
            body_node = soup.find("div", class_=re.compile(r"detail-in|artikel"))

        # Fallback to general article heuristics
        if not body_node:
            body_node = soup.find("article") or soup.find("main")

        # Extract paragraphs
        paragraphs = []
        boilerplate = [
            "enable JavaScript", "HTML5 video", "Sign up for our newsletter",
            "Click here to subscribe", "Cookie preferences", "All rights reserved",
            "Baca juga:", "Simak juga:", "Copyright"
        ]
        if body_node:
            # Clean up ad boxes or read also widgets inside body
            for unwanted_child in body_node.find_all(["div", "span", "p"], class_=re.compile(r"ads|banner|baca-juga|share|social|related|tag", re.I)):
                unwanted_child.decompose()
            for p in body_node.find_all("p"):
                txt = p.get_text(strip=True)
                if len(txt) > 25 and not any(bp in txt for bp in boilerplate):
                    paragraphs.append(txt)

        # Fallback if body_node yielded empty paragraphs
        if not paragraphs:
            for p in soup.find_all("p"):
                txt = p.get_text(strip=True)
                if len(txt) > 35 and not any(bp in txt for bp in boilerplate):
                    paragraphs.append(txt)

        full_text = "\n\n".join(paragraphs).strip()
        if not full_text and meta_desc:
            full_text = meta_desc
            paragraphs = [meta_desc]

        # Sentence tokenizer
        sentences = split_into_sentences(full_text)

        if not full_text:
            return {
                "status": "error",
                "error_msg": "Tidak dapat mengekstrak teks berita dari URL tersebut. Halaman mungkin membutuhkan login, captcha, atau berbasis JavaScript murni (SPA).",
                "url": url,
                "domain": domain
            }

        return {
            "status": "success",
            "url": url,
            "domain": domain,
            "site_name": site_name,
            "title": title or "Berita Tanpa Judul",
            "author": author_str or "Redaksi",
            "date": date_str or "Tanggal tidak terdeteksi",
            "image": image_url,
            "full_text": full_text,
            "paragraphs": paragraphs,
            "sentences": sentences
        }

    except Exception as e:
        err_str = str(e)
        if "403" in err_str or "Forbidden" in err_str:
            friendly_msg = (
                "Situs web ini memproteksi halamannya dengan sistem keamanan anti-bot (HTTP 403 Forbidden). "
                "Silakan buka tautan langsung di browser Anda, lalu salin (copy) judul & isi artikelnya, "
                "dan tempelkan ke tab 'Salin & Tempel Naskah' di atas untuk tetap dapat memverifikasinya."
            )
        elif "404" in err_str or "Not Found" in err_str:
            friendly_msg = "Halaman berita tidak ditemukan (HTTP 404 Not Found). Mohon periksa kembali apakah alamat tautan berita sudah lengkap dan masih aktif."
        else:
            friendly_msg = f"Gagal mengakses URL secara otomatis ({err_str}). Silakan gunakan tab 'Salin & Tempel Naskah' untuk memeriksa artikel secara langsung."

        return {
            "status": "error",
            "error_msg": friendly_msg,
            "url": url
        }

def split_into_sentences(text: str) -> list:
    """Split text into sentences while respecting abbreviations."""
    if not text:
        return []
    # Replace newlines with spaces temporarily
    cleaned = re.sub(r'\s+', ' ', text).strip()
    # Sentence splitting regex on Indonesian punctuation
    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\(\[])', cleaned)
    final_sentences = []
    for s in raw_sentences:
        s = s.strip()
        if len(s) > 10:
            final_sentences.append(s)
    if not final_sentences and text:
        final_sentences = [text.strip()]
    return final_sentences

