from sqlalchemy import Column, String, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CampgroundORM(Base):
    __tablename__ = "campgrounds"

    id = Column(String, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    region = Column(String)
    city = Column(String)
    operator = Column(String)
    price_low = Column(String)
    price_high = Column(String)
    rating = Column(Float)
    reviews_count = Column(Integer)
    photo_url = Column(String)
    slug = Column(String)
    area = Column(String)
    photos_count = Column(Integer)
    bookable = Column(Boolean)
