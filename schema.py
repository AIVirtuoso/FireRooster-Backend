from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserType(Base):
    __tablename__ = "usertype_table"
    id = Column(Integer, primary_key=True)
    tier = Column(String)
    price = Column(Float)
    state_limit = Column(Integer)
    county_limit = Column(Integer)
    scanner_limit = Column(Integer)

class User(Base):
    __tablename__ = "user_table"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    forgot_password_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    stripe_id = Column(String, nullable=True)
    
    user_type_id = Column(Integer, ForeignKey("usertype_table.id"), nullable=True)
    user_type = relationship("UserType")

class Audio(Base):
    __tablename__ = "audio_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String)
    context = Column(String)
    cleared_context = Column(String)
    scanner_id = Column(Integer)
    dateTime = Column(DateTime)

class Scanner(Base):
    __tablename__ = "scanner_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    state_id = Column(Integer)
    state_name = Column(String)
    county_id = Column(Integer)
    county_name = Column(String)
    scanner_id = Column(Integer)
    scanner_title = Column(String)
    listeners_count = Column(Integer)

class PurchasedScanner(Base):
    __tablename__ = "purchased_scanner_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    scanner_id = Column(Integer)
    
class Alert(Base):
    __tablename__ = "alert_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String)
    sub_category = Column(String)
    headline = Column(String)
    description = Column(String)
    address = Column(String)
    scanner_id = Column(Integer)
    dateTime = Column(DateTime)
    is_visited = Column(Integer)
    
class Address(Base):
    __tablename__ = "address_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String)
    score = Column(Float)
    alert_id = Column(Integer)
    type = Column(String)
    scanner_id = Column(Integer)
    dateTime = Column(DateTime)
    contact_info = Column(JSON)
    
class Variables(Base):
    __tablename__ = "variables_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(String)
    
class Category(Base):
    __tablename__ = "category_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String)
    sub_category = Column(String)
    is_selected = Column(Integer)

class FireDistrict(Base):
    __tablename__ = "fire_district_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String)
    county = Column(String)
    json_data = Column(JSON)
