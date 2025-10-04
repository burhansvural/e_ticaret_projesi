# backend/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Veritabanı Dosyasının Yolu
# Proje ana dizininde "ecommerce.db" adında bir dosya oluşturacak.
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecommerce.db"

# 2. SQLAlchemy motorunu oluştur
# 'check_same_thread': False parametresi sadece SQLite için gereklidir.
# FastAPI'nin yapısı gereği farklı thread'ler DB ile etkileşime girebilir.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Veritabanı oturumları (session) için bir fabrika oluştur
# Her bir istek için bağımsız bir veritabanı oturumu açacağız.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Modellerimizin miras alacağı bir ana (Base) sınıf oluştur
# Veritabanı tablolarımızı Python sınıfları olarak tanımlamak için bunu kullanacağız.
Base = declarative_base()