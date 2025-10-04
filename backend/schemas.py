# backend/schemas.py
import datetime
from typing import Optional, List
from pydantic import BaseModel, validator, Field, EmailStr
import re


# Kategori şemaları
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: str
    description: Optional[str] = None

class Category(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

# Ürün oluşturulurken API'ye gönderilecek veri modeli
# ID veritabanı tarafından otomatik oluşturulacağı için burada yok.
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    stock_quantity: Optional[int] = 0
    unit: Optional[str] = "adet"

# Ürün güncellenirken API'ye gönderilecek veri modeli
class ProductUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    stock_quantity: Optional[int] = None
    unit: Optional[str] = None


# Veritabanından ürün okunurken veya API'den döndürülürken kullanılacak model
class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    stock_quantity: Optional[int] = 0
    unit: Optional[str] = "adet"

    # Bu ayar, Pydantic modelinin SQLAlchemy ORM nesneleriyle
    # uyumlu çalışmasını sağlar. (örn: product.name gibi erişime izin verir)
    class Config:
        from_attributes = True

# Kullanıcı oluştururken API'ye gönderilecek veri
class UserCreate(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    address: Optional[str] = Field(None, max_length=500)
    is_admin: bool = False  # Admin kaydı için kullanılır
    
    @validator('email')
    def validate_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Geçerli bir e-posta adresi giriniz')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Şifre en az bir özel karakter içermelidir')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v.replace(' ', '').isalpha():
            raise ValueError('İsim sadece harf içerebilir')
        return v.strip().title()

# API'den kullanıcı bilgisi döndürürken kullanılacak model
class User(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_admin: bool = False
    last_login: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Kullanıcı giriş için
class UserLogin(BaseModel):
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)
    is_admin: bool = False  # Varsayılan olarak normal kullanıcı girişi
    
    @validator('email')
    def validate_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Geçerli bir e-posta adresi giriniz')
        return v.lower()

# JWT Token yanıtı
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# Başarılı giriş yanıtı
class UserLoginResponse(BaseModel):
    user: User
    tokens: TokenResponse
    message: str

# Şifre değiştirme
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Şifre en az bir özel karakter içermelidir')
        return v

# Şifre sıfırlama isteği
class PasswordResetRequest(BaseModel):
    email: EmailStr

# Şifre sıfırlama
class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', v):
            raise ValueError('Şifre en az bir özel karakter içermelidir')
        return v

# API Key şemaları
class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    permissions: Optional[List[str]] = None
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)

class APIKey(BaseModel):
    id: int
    name: str
    key_preview: str  # Sadece ilk 8 karakter
    is_active: bool
    permissions: Optional[str] = None
    last_used: Optional[datetime.datetime] = None
    expires_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

class APIKeyResponse(BaseModel):
    api_key: APIKey
    key: str  # Tam anahtar sadece oluşturma sırasında döndürülür

# 2FA şemaları
class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str

class TwoFactorVerify(BaseModel):
    token: str = Field(..., pattern=r'^\d{6}$')

# Güvenlik log şemaları
class SecurityLogCreate(BaseModel):
    event_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None
    severity: str = "info"

class SecurityLog(BaseModel):
    id: int
    user_id: Optional[int] = None
    event_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None
    severity: str
    created_at: datetime.datetime
    
    class Config:
        from_attributes = True

# E-mail doğrulama kodu gönderme
class EmailVerificationRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., pattern=r'^\d{6}$', description="6 haneli doğrulama kodu")
    is_admin: bool = False  # Varsayılan olarak normal kullanıcı doğrulaması

# E-mail doğrulama yanıtı
class EmailVerificationResponse(BaseModel):
    message: str
    success: bool

# E-mail doğrulama token'ı gönderme yanıtı
class ResendVerificationResponse(BaseModel):
    message: str
    success: bool

# Sipariş oluştururken her bir ürünün bilgisi
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

# Sipariş oluştururken API'ye gönderilecek ana veri
class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

# API'den sipariş detaylarını döndürürken
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price_per_item: float
    class Config: from_attributes = True

class Order(BaseModel):
    id: int
    owner_id: Optional[int] = None
    created_date: datetime.datetime
    total_price: float
    status: str = "pending"
    notes: Optional[str] = None
    updated_at: datetime.datetime
    items: list[OrderItem] = []
    class Config: from_attributes = True

# Sipariş durumu güncelleme için
class OrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

# Refresh token için schema
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Token refresh yanıtı
class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

# Logout request schema
class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None