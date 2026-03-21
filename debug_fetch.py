"""
Script debug: fetch halaman dan simpan HTML-nya ke file.
Kita bisa lihat HTML apa yang dikembalikan Booking.com ke GitHub Actions.
"""

import random
import sys

try:
    from curl_cffi import requests
    print("✅ curl_cffi tersedia")
except ImportError:
    import requests
    print("⚠️  pakai requests biasa")

URL = "https://www.booking.com/hotel/id/arena-villa.id.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}

try:
    from curl_cffi import requests as cr
    r = cr.get(URL, headers=headers, impersonate="chrome120", timeout=20)
except Exception:
    import requests as rq
    r = rq.get(URL, headers=headers, timeout=20)

print(f"Status      : {r.status_code}")
print(f"URL akhir   : {r.url}")
print(f"Ukuran HTML : {len(r.text):,} karakter")

# Simpan HTML lengkap untuk diinspeksi
with open("debug_output.html", "w", encoding="utf-8") as f:
    f.write(r.text)

print("✅ HTML disimpan ke debug_output.html")

# Print 50 baris pertama sebagai preview di log Actions
lines = r.text.splitlines()[:50]
print("\n── Preview 50 baris pertama ──")
for line in lines:
    print(line)
