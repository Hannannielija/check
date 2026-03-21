"""
Booking.com Hotel Scraper - Contoh untuk pembelajaran
Teknik: curl_cffi (anti-bot) + JSON-LD (stabil) + CSS fallback
"""

import json
import random
import re
import time
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

try:
    from curl_cffi import requests
    CURL_AVAILABLE = True
    print("✅ Menggunakan curl_cffi (mode anti-bot)")
except ImportError:
    import requests
    CURL_AVAILABLE = False
    print("⚠️  curl_cffi tidak tersedia, pakai requests biasa")

# ─────────────────────────────────────────
# KONFIGURASI
# ─────────────────────────────────────────

HOTEL_URL = "https://www.booking.com/hotel/id/arena-villa.id.html"
OUTPUT_FILE = "data/hotel_data.json"

PROXIES = [
    # "123.45.67.89:8080",   ← isi dengan proxy kamu
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

BROWSER_IMPERSONATIONS = ["chrome110", "chrome116", "chrome120", "chrome124"]


# ─────────────────────────────────────────
# ROTATING PROXY & HEADERS
# ─────────────────────────────────────────

def get_random_proxy():
    if not PROXIES:
        return None
    proxy = random.choice(PROXIES)
    return {"http": f"http://{proxy}", "https": f"http://{proxy}"}


def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "upgrade-insecure-requests": "1",
    }


# ─────────────────────────────────────────
# FETCH HALAMAN
# ─────────────────────────────────────────

def fetch_page(url, retries=3):
    for attempt in range(1, retries + 1):
        print(f"[Attempt {attempt}/{retries}] Mengambil halaman...")
        proxy = get_random_proxy()
        headers = get_random_headers()

        try:
            if CURL_AVAILABLE:
                impersonate = random.choice(BROWSER_IMPERSONATIONS)
                response = requests.get(
                    url, headers=headers, proxies=proxy,
                    impersonate=impersonate, timeout=20,
                )
            else:
                response = requests.get(url, headers=headers, proxies=proxy, timeout=20)

            response.raise_for_status()
            html = response.text

            if "captcha" in html.lower() or len(html) < 5000:
                raise ValueError("Halaman tidak valid (mungkin CAPTCHA)")

            print(f"✅ Berhasil! Ukuran HTML: {len(html):,} karakter")
            return html

        except Exception as e:
            print(f"❌ Gagal: {e}")
            if attempt < retries:
                wait = random.uniform(5, 12)
                print(f"⏳ Tunggu {wait:.1f}s sebelum retry...")
                time.sleep(wait)

    raise RuntimeError("Semua percobaan gagal.")


# ─────────────────────────────────────────
# PARSE DATA — 2 LAPIS FALLBACK
# ─────────────────────────────────────────

def parse_via_json_ld(soup):
    """
    LAPISAN 1 — Paling stabil.
    Booking.com menyimpan data di JSON-LD (schema.org) di dalam <script>.
    Format ini jarang berubah walau tampilan web ganti total.
    """
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                agg = item.get("aggregateRating", {})
                if agg:
                    rating = str(agg.get("ratingValue", ""))
                    count  = str(agg.get("reviewCount") or agg.get("ratingCount", ""))
                    if rating:
                        print("  → Sumber: JSON-LD ✅")
                        return rating, f"{count} ulasan" if count else "N/A"
        except Exception:
            continue
    return None, None


def parse_via_regex(soup):
    """
    LAPISAN 2 — Fallback regex di seluruh teks halaman.
    Cari pola angka rating (7.0–10.0) dan kata 'ulasan/review'.
    """
    text = soup.get_text()

    rating = None
    match = re.search(r'\b([7-9]\.\d|10\.0)\b', text)
    if match:
        rating = match.group(1)

    review_count = None
    m = re.search(r'(\d[\d.,]+)\s*(ulasan|review|penilaian)', text, re.I)
    if m:
        review_count = f"{m.group(1)} {m.group(2)}"

    if rating:
        print("  → Sumber: regex fallback ✅")
    return rating, review_count


def parse_hotel_data(html):
    soup = BeautifulSoup(html, "lxml")
    rating, review_count = parse_via_json_ld(soup)
    if not rating:
        rating, review_count = parse_via_regex(soup)
    return {
        "rating": rating or "Tidak ditemukan",
        "review_count": review_count or "Tidak ditemukan",
    }


# ─────────────────────────────────────────
# SIMPAN DATA
# ─────────────────────────────────────────

def load_existing_data(filepath):
    path = Path(filepath)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"hotel_url": HOTEL_URL, "history": []}


def save_data(filepath, data):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 Data disimpan ke {filepath}")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    print("=" * 50)
    print("🏨 Booking.com Hotel Scraper")
    print("=" * 50)

    html = fetch_page(HOTEL_URL)
    scraped = parse_hotel_data(html)

    print(f"\n📊 Hasil scraping:")
    print(f"   Rating       : {scraped['rating']}")
    print(f"   Jumlah Ulasan: {scraped['review_count']}")

    entry = {
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "rating": scraped["rating"],
        "review_count": scraped["review_count"],
    }

    all_data = load_existing_data(OUTPUT_FILE)
    all_data["history"].append(entry)
    all_data["last_updated"] = entry["scraped_at"]
    save_data(OUTPUT_FILE, all_data)
    print("\n✅ Selesai!")


if __name__ == "__main__":
    main()
