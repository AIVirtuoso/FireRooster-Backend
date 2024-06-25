from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserType(Base):
    __tablename__ = "usertype_table"
    id = Column(Integer, primary_key=True, index=True)
    tier = Column(String, index=True)
    price = Column(Float)
    state_limit = Column(Integer)
    county_limit = Column(Integer)
    scanner_limit = Column(Integer)

class User(Base):
    __tablename__ = "user_table"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    forgot_password_token = Column(String, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    stripe_id = Column(String, index=True, nullable=True)
    
    user_type_id = Column(Integer, ForeignKey("usertype_table.id"), nullable=True)
    user_type = relationship("UserType")

class Audio(Base):
    __tablename__ = "audio_table"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String, index=True)
    context = Column(String, index=True)
    scanner_id = Column(Integer, index=True)

class Scanner(Base):
    __tablename__ = "scanner_table"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    state_id = Column(Integer, index=True)
    state_name = Column(String, index=True)
    county_id = Column(Integer, index=True)
    county_name = Column(String, index=True)
    scanner_id = Column(Integer, index=True)
    scanner_title = Column(String, index=True)
    listeners_count = Column(String, index=True)

class PurchasedScanner(Base):
    __tablename__ = "purchased_scanner_table"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    scanner_id = Column(Integer, index=True)