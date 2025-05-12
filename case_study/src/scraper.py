import requests
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from src.models.campground import Campground
from src.db.models import CampgroundORM
from src.db.session import get_session


# Log ayarı
log_path = os.path.join(os.getcwd(), "scraper.log")
log_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=2)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# Retry destekli GET
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True
)
def get_with_retry(url, headers=None, params=None):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response

# Geopy reverse
geolocator = Nominatim(user_agent="campground-scraper")
def get_city_state_from_coords(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=5)
        address = location.raw.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village")
        state = address.get("state")
        return city, state
    except (GeocoderTimedOut, AttributeError):
        return None, None

# Scraping
US_BBOXES = [
    (-125, 48, -114, 50), (-114, 48, -100, 50), (-100, 48, -87, 50), (-87, 48, -74, 50),
    (-125, 36, -114, 48), (-114, 36, -100, 48), (-100, 36, -87, 48), (-87, 36, -74, 48),
    (-125, 24, -114, 36), (-114, 24, -100, 36)
]

def scrape_and_store():
    start = time.time()
    logging.info("Scraper çalışıyor...")

    url_base = "https://thedyrt.com/api/v6/locations/search-results"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    session = get_session()

    for bbox in US_BBOXES:
        for page in range(1, 6):
            params = {
                "filter[search][drive_time]": "any",
                "filter[search][air_quality]": "any",
                "filter[search][electric_amperage]": "any",
                "filter[search][max_vehicle_length]": "any",
                "filter[search][price]": "any",
                "filter[search][rating]": "any",
                "filter[search][bbox]": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
                "sort": "recommended",
                "page[number]": str(page),
                "page[size]": "100"
            }

            try:
                resp = get_with_retry(url_base, headers=headers, params=params)
                data = resp.json()
            except Exception as e:
                logging.error(f"BBOX {bbox} Sayfa {page} istek hatası: {e}")
                continue

            for item in data.get("data", []):
                detail_url = item.get("links", {}).get("self")
                if not detail_url:
                    continue
                try:
                    detail_resp = get_with_retry(detail_url, headers=headers)
                    detail_data = detail_resp.json()
                    raw = detail_data.get("data", {})
                    attrs = raw.get("attributes", {})
                    attrs["id"] = raw.get("id")
                    attrs["type"] = raw.get("type")
                    attrs["links"] = raw.get("links")
                    validated = Campground(**attrs)

                    city = validated.nearest_city_name
                    state = validated.administrative_area
                    if not city or not state:
                        city, state = get_city_state_from_coords(validated.latitude, validated.longitude)

                    obj = session.get(CampgroundORM, validated.id)
                    if not obj:
                        obj = CampgroundORM(id=validated.id)
                        session.add(obj)

                    obj.name = validated.name
                    obj.latitude = validated.latitude
                    obj.longitude = validated.longitude
                    obj.region = validated.region_name
                    obj.city = city
                    obj.operator = validated.operator
                    obj.price_low = str(validated.price_low) if validated.price_low is not None else None
                    obj.price_high = str(validated.price_high) if validated.price_high is not None else None
                    obj.rating = validated.rating
                    obj.reviews_count = validated.reviews_count
                    obj.photo_url = str(validated.photo_url) if validated.photo_url else None
                    obj.slug = validated.slug
                    obj.area = state
                    obj.photos_count = validated.photos_count
                    obj.bookable = validated.bookable

                except (requests.RequestException, ValidationError, KeyError) as e:
                    logging.warning(f"Kayit atlandi (bbox={bbox}): {e}")
                    continue

    try:
        session.commit()
        logging.info("Veritabanina basarili sekilde yazildi.")
    except Exception as e:
        session.rollback()
        logging.error(f"Commit hatasi: {e}")
    finally:
        session.close()

    logging.info("Scraper tamamlandi.")
    logging.info(f"craper sure: {round(time.time() - start, 2)} saniye")
