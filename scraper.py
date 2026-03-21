import json, os, requests
from datetime import datetime
from pathlib import Path

HOTEL_URL   = "https://www.booking.com/hotel/id/arena-villa.id.html"
OUTPUT_FILE = "data/hotel_data.json"
APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
ACTOR_ID    = "voyager~booking-scraper"

def run_apify(url):
    if not APIFY_TOKEN:
        raise ValueError("APIFY_TOKEN tidak ditemukan di GitHub Secrets!")
    print("Mengirim job ke Apify...")
    r = requests.post(
        f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items",
        json={"startUrls": [{"url": url}], "maxItems": 1},
        params={"token": APIFY_TOKEN},
        timeout=300,
    )
    print(f"Status: {r.status_code}")
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Apify error: {r.text[:300]}")
    items = r.json()
    if not items:
        raise RuntimeError("Data kosong dari Apify")
    return items[0]

def main():
    print("Booking.com Scraper via Apify")
    item = run_apify(HOTEL_URL)
    print("Raw data:", json.dumps(item, ensure_ascii=False, indent=2)[:800])

    rating = str(item.get("rating") or item.get("reviewScore") or "Tidak ditemukan")
    review_count = item.get("reviews") or item.get("numberOfReviews") or "Tidak ditemukan"
    review_str = f"{review_count} ulasan" if review_count != "Tidak ditemukan" else review_count

    print(f"Rating: {rating}")
    print(f"Ulasan: {review_str}")

    path = Path(OUTPUT_FILE)
    data = json.loads(path.read_text()) if path.exists() else {"hotel_url": HOTEL_URL, "history": []}
    data["history"].append({"scraped_at": datetime.utcnow().isoformat()+"Z", "rating": rating, "review_count": review_str})
    data["last_updated"] = data["history"][-1]["scraped_at"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print("Selesai!")

if __name__ == "__main__":
    main()
