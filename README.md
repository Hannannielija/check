# 🏨 Booking.com Hotel Scraper

Contoh sederhana web scraping rating & ulasan hotel dari Booking.com,
berjalan otomatis setiap minggu via **GitHub Actions**, dengan hasil disimpan ke **JSON**.

---

## 📁 Struktur Project

```
booking-scraper/
├── .github/
│   └── workflows/
│       └── scrape.yml      ← Jadwal otomatis GitHub Actions
├── data/
│   └── hotel_data.json     ← Hasil scraping tersimpan di sini
├── scraper.py              ← Script utama
├── requirements.txt        ← Dependensi Python
└── README.md
```

---

## 🚀 Cara Pakai

### 1. Fork / Clone repo ini
```bash
git clone https://github.com/USERNAME/booking-scraper.git
cd booking-scraper
```

### 2. Install dependensi (untuk tes lokal)
```bash
pip install -r requirements.txt
```

### 3. Tes jalankan scraper secara lokal
```bash
python scraper.py
```

### 4. Push ke GitHub
GitHub Actions akan otomatis berjalan setiap **Senin pukul 07:00 WIB**.
Bisa juga dijalankan manual: **Actions → 🏨 Scrape Hotel Rating → Run workflow**

---

## ⚙️ Cara Kerja

```
GitHub Actions (tiap Senin)
        │
        ▼
  scraper.py dijalankan
        │
        ├─ Pilih proxy & User-Agent secara ACAK  ← Rotating Proxy
        │
        ├─ Request ke Booking.com
        │
        ├─ Parse HTML → ambil rating & ulasan
        │
        └─ Simpan ke data/hotel_data.json  ← Append ke history
                │
                ▼
        Git commit & push otomatis
```

---

## 🔄 Rotating Proxy

Buka `scraper.py` dan isi daftar `PROXIES`:

```python
PROXIES = [
    "123.45.67.89:8080",
    "98.76.54.32:3128",
    # tambahkan lebih banyak...
]
```

> 💡 **Tips**: Proxy gratis sering tidak stabil. Untuk produksi, gunakan
> layanan proxy berbayar seperti Bright Data, Oxylabs, atau Smartproxy.

---

## 📊 Format Output JSON

```json
{
  "hotel_url": "https://www.booking.com/hotel/id/arena-villa.id.html",
  "last_updated": "2026-03-17T00:00:00Z",
  "history": [
    {
      "scraped_at": "2026-03-17T00:00:00Z",
      "rating": "8.5",
      "review_count": "234 ulasan"
    }
  ]
}
```

Setiap kali scraper berjalan, data baru di-**append** ke array `history`
sehingga kamu bisa melihat perubahan rating dari waktu ke waktu.

---

## ⚠️ Catatan Penting

- **Hanya untuk pembelajaran** — selalu patuhi Terms of Service website yang di-scrape.
- Booking.com sering mengubah struktur HTML-nya; selector mungkin perlu disesuaikan.
- Jika scraping sering gagal, coba tambahkan delay lebih panjang atau gunakan proxy berbayar.

---

## 📚 Yang Bisa Dipelajari dari Project Ini

| Konsep | Di mana |
|---|---|
| HTTP Request dengan `requests` | `scraper.py` → `fetch_page()` |
| Parse HTML dengan `BeautifulSoup` | `scraper.py` → `parse_hotel_data()` |
| Rotating proxy & User-Agent | `scraper.py` → `get_random_proxy()` |
| Retry otomatis jika gagal | `scraper.py` → loop `retries` |
| Simpan & append data ke JSON | `scraper.py` → `save_data()` |
| Penjadwalan otomatis (cron) | `.github/workflows/scrape.yml` |
| Auto commit dari CI/CD | `.github/workflows/scrape.yml` |
