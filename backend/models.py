import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base

# Product adında bir Python sınıfı oluşturuyoruz.
# Bu sınıf, veritabanındaki "products" tablosuna karşılık gelecek.
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # İlişki
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    # Tablodaki sütunları tanımlıyoruz
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True) # nullable=True, bu alanın boş olabileceği anlamına gelir.
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    stock_quantity = Column(Integer, default=0, nullable=False)
    unit = Column(String, default="adet", nullable=False)  # kg, litre, adet, gram vb.
    
    # İlişki
    category = relationship("Category", back_populates="products")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending, preparing, ready, shipped, delivered, cancelled
    notes = Column(Text, nullable=True)  # Admin notları
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # İlişkileri kur
    owner = relationship("User")  # back_populates="orders" User modeline eklenecek
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    price_per_item = Column(Float, nullable=False)

    # İlişkileri kur
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


# User modelini de güncellemeliyiz
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        # Aynı email hem admin hem user olarak kayıt olabilir
        # Unique constraint: email + is_admin kombinasyonu unique olmalı
        UniqueConstraint('email', 'is_admin', name='uix_email_is_admin'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)  # unique=True kaldırıldı
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)  # E-mail doğrulanana kadar pasif
    is_verified = Column(Boolean, default=False)  # E-mail doğrulama durumu
    is_admin = Column(Boolean, default=False)  # Admin yetkisi
    verification_token = Column(String, nullable=True)  # E-mail doğrulama token'ı
    verification_token_expires = Column(DateTime, nullable=True)  # Token son kullanma tarihi
    
    # Güvenlik alanları
    last_login = Column(DateTime, nullable=True)  # Son giriş tarihi
    failed_login_attempts = Column(Integer, default=0)  # Başarısız giriş denemeleri
    locked_until = Column(DateTime, nullable=True)  # Hesap kilitleme süresi
    password_changed_at = Column(DateTime, default=datetime.datetime.utcnow)  # Şifre değiştirilme tarihi
    two_factor_enabled = Column(Boolean, default=False)  # 2FA aktif mi
    two_factor_secret = Column(String, nullable=True)  # 2FA secret key
    
    # Audit alanları
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_by_ip = Column(String, nullable=True)  # Kayıt IP adresi
    last_login_ip = Column(String, nullable=True)  # Son giriş IP adresi

    # User'dan Order'lara olan ilişki
    orders = relationship("Order", back_populates="owner")
    api_keys = relationship("APIKey", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")


class APIKey(Base):
    """API anahtarları tablosu"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)  # API anahtarı adı
    key_hash = Column(String, nullable=False)  # Hash'lenmiş API anahtarı
    is_active = Column(Boolean, default=True)
    permissions = Column(String, nullable=True)  # JSON formatında izinler
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # İlişki
    user = relationship("User", back_populates="api_keys")


class UserSession(Base):
    """Kullanıcı oturumları tablosu"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    refresh_token = Column(String, unique=True, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)
    
    # İlişki
    user = relationship("User", back_populates="sessions")


class SecurityLog(Base):
    """Güvenlik olayları log tablosu"""
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String, nullable=False)  # login, logout, failed_login, password_change, etc.
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(Text, nullable=True)  # JSON formatında ek bilgiler
    severity = Column(String, default="info")  # info, warning, error, critical
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PasswordResetToken(Base):
    """Şifre sıfırlama token'ları tablosu"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    used_at = Column(DateTime, nullable=True)


class BlacklistedToken(Base):
    """Blacklist edilmiş token'lar tablosu"""
    __tablename__ = "blacklisted_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token_jti = Column(String, unique=True, nullable=False, index=True)  # JWT ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    token_type = Column(String, nullable=False)  # access, refresh
    blacklisted_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # Token'ın orijinal süresi
    reason = Column(String, nullable=True)  # logout, password_change, admin_action, etc.