from src.db.session import engine
from src.db.models import Base

def init_db():
    Base.metadata.create_all(bind=engine)
