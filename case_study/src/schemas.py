from pydantic import BaseModel
from typing import Optional

class CampgroundOut(BaseModel):
    id: str
    name: Optional[str]
    latitude: float
    longitude: float
    region: Optional[str]
    city: Optional[str]
    operator: Optional[str]
    price_low: Optional[str]
    price_high: Optional[str]
    rating: Optional[float]
    reviews_count: Optional[int]
    photo_url: Optional[str]
    slug: Optional[str]
    area: Optional[str]
    photos_count: Optional[int]
    bookable: Optional[bool]

    class Config:
        orm_mode = True
