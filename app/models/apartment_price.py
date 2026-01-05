import uuid
import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime

from app.db.base_class import Base
from app.core.config import settings


class ApartmentPrice(Base):
    __tablename__ = "apartment_price"
    __table_args__ = {'schema': settings.DATABASE_SCHEMA}

    id = Column(String(64), primary_key=True, default=str(uuid.uuid4()))
    client_id = Column(String(255))
    client_message_id = Column(String(64))
    province_code = Column(String(200))
    district_code = Column(String(200))
    ward_code = Column(String(200))
    street = Column(String(2000))
    project_name = Column(String(2000))
    apartment_name = Column(String(1000))
    n_bedrooms = Column(Integer)
    area = Column(Float)
    result = Column(Integer)
    price = Column(Float)
    price_min = Column(Float)
    price_max = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
