
# 🏕 The Dyrt Kamp Alanı Scraper Projesi

Bu proje, [The Dyrt](https://thedyrt.com/search) sitesinden **ABD genelindeki tüm kamp alanı verilerini** çekmek, doğrulamak ve PostgreSQL veritabanında saklamak için geliştirilmiş bir veri kazıyıcı (scraper) sistemidir.

---

## 🚀 Özellikler

- ✅ **FastAPI** ile web arayüzü ve API endpoint'leri
- ✅ **SQLAlchemy ORM** ile PostgreSQL veritabanı bağlantısı
- ✅ **Pydantic** ile veri doğrulama (JSON → Python sınıfı)
- ✅ **APScheduler** ile 2 saatte bir otomatik veri çekme
- ✅ **Retry / Hata Yönetimi** (`tenacity`) ile sağlamlık
- ✅ **Geopy** ile koordinatlardan şehir ve eyalet bulma
- ✅ **Docker & Docker Compose** desteği
- ✅ **Log dosyası** ile günlük kayıt

---

## 📁 Proje Yapısı

```
📦 src/
 ┣ 📜 scraper.py        → Ana veri çekme (scrape) mantığı
 ┣ 📜 main.py           → FastAPI ve scheduler başlatıcısı
 ┣ 📜 models.py         → SQLAlchemy ORM modeli
 ┣ 📜 schemas.py        → JSON çıktısı için Pydantic modeli
 ┣ 📜 campground.py     → Giriş doğrulama için Pydantic modeli
 ┣ 📜 session.py        → Veritabanı bağlantı fonksiyonu
 ┣ 📜 init_db.py        → Veritabanı tablolarını oluşturur
📜 requirements.txt     → Gerekli Python paketleri
📜 docker-compose.yml   → PostgreSQL + scraper servisi
📜 Dockerfile           → Scraper container tanımı
📜 scraper.log          → Log dosyası
```

---

## 🔧 Kurulum

### 1. Depoyu Klonlayın

```bash
git clone https://github.com/kendi-repo-urlun/campground-scraper.git
cd campground-scraper
```

### 2. Ortam Değişkeni Ayarı

`.env` dosyasını oluşturun:

```
DB_HOST=postgres
```

### 3. Docker Compose ile çalıştırın

```bash
docker-compose up --build
```

---

## 🖥 FastAPI Arayüzü

API çalıştığında FastAPI arayüzüne şuradan ulaşabilirsiniz:

📍 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### ➕ Endpoint'ler

| Yöntem | URL | Açıklama |
|--------|-----|----------|
| GET | `/ping` | Sunucu çalışıyor mu kontrolü |
| POST | `/trigger` | Scraper’ı manuel çalıştırma |
| GET | `/campgrounds` | Tüm kamp verilerini JSON olarak getirir |

---

## 🔎 JSON Çıktısı Örneği

`/campgrounds` endpoint'ine GET isteği attığınızda aşağıdaki gibi bir JSON döner:

```json
[
  {
    "id": "ZZZ...==",
    "name": "Hidden Village RV Park & Campground",
    "latitude": 48.91,
    "longitude": -122.48,
    "region": "Washington",
    "city": null,
    "operator": null,
    "price_low": "0.0",
    "price_high": "0.0",
    "rating": 5.0,
    "reviews_count": 1,
    "photo_url": null,
    "slug": "hidden-village-rv-park-and-campground",
    "area": "Washington",
    "photos_count": 0,
    "bookable": false
  }
]
```

Veriler `schemas.py` dosyasındaki `CampgroundOut` modeli ile formatlanır.

---

## 🗓 Zamanlayıcı (Scheduler)

Scraper otomatik olarak **10 dakikada bir** çalışır. Bunun dışında manuel tetikleme de yapılabilir.

- Arka planda `APScheduler` ile ayarlanır.
- Maksimum bir örnek çalışabilir (`max_instances=1`).

---

## 🧪 Log Takibi

Loglar `scraper.log` dosyasına yazılır:

```bash
tail -f scraper.log
```

Örnek:

```
[2025-05-12 13:40:12,005] [INFO] ✅ Veritabanina basarili sekilde yazildi.
[2025-05-12 13:40:12,005] [INFO] Scraper tamamlandi.
```

---

## 💾 Veritabanı Şeması

```sql
CREATE TABLE campgrounds (
  id TEXT PRIMARY KEY,
  name TEXT,
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  region TEXT,
  city TEXT,
  operator TEXT,
  price_low TEXT,
  price_high TEXT,
  rating FLOAT,
  reviews_count INT,
  photo_url TEXT,
  slug TEXT,
  area TEXT,
  photos_count INT,
  bookable BOOLEAN
);
```

---

## 📜 Gereksinimler

`requirements.txt` üzerinden kuruludur:

```bash
pip install -r requirements.txt
```

Paketler:

- fastapi
- uvicorn
- pydantic
- requests
- tenacity
- geopy
- sqlalchemy
- apscheduler
- psycopg2-binary

---

