# backend/security.py

import hashlib
import hmac
import logging
import os
import secrets
import string
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import redis
from fastapi import HTTPException, status, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from jwt import ExpiredSignatureError
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from . import models
from .database import SessionLocal

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Şifre hashleme yapılandırması
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT yapılandırması
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logger.error("CRITICAL: SECRET_KEY environment variable is not set!")
    logger.error("Please set SECRET_KEY in your .env file or environment variables")
    logger.error("Example: SECRET_KEY=your-super-secret-key-here")
    raise ValueError("SECRET_KEY environment variable is required for security")

# SECRET_KEY güvenlik kontrolü
if len(SECRET_KEY) < 32:
    logger.error("CRITICAL: SECRET_KEY is too short! Minimum 32 characters required for security.")
    logger.error(f"Current length: {len(SECRET_KEY)}, Required: 32+")
    raise ValueError("SECRET_KEY must be at least 32 characters long for security")

# Production ortamında varsayılan SECRET_KEY kontrolü
if SECRET_KEY in ["your-super-secret-key-here", "change-this-in-production", "secret"]:
    logger.error("CRITICAL: Using default/weak SECRET_KEY in production!")
    logger.error("Please generate a strong SECRET_KEY using: python -c 'import secrets; print(secrets.token_urlsafe(64))'")
    raise ValueError("Default SECRET_KEY detected - security risk!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate limiting için Redis bağlantısı
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0
    )
    # Redis bağlantısını test et
    redis_client.ping()
    logger.info("Redis bağlantısı başarılı")
except Exception as e:
    logger.warning(f"Redis bağlantısı başarısız, memory storage kullanılacak: {e}")
    redis_client = None

# Rate limiter yapılandırması
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379" if redis_client else "memory://",
    default_limits=["1000/hour"]
)

# Rate limit aşıldığında özel response handler
def rate_limit_handler(request: Request, exc: Exception) -> Response:
    """Rate limit aşıldığında özel response döndürür"""
    # exc'yi RateLimitExceeded olarak cast et
    rate_limit_exc = exc if isinstance(exc, RateLimitExceeded) else None
    
    if rate_limit_exc:
        response = Response(
            content=f"Rate limit aşıldı: {rate_limit_exc.detail}. Lütfen daha sonra tekrar deneyin.",
            status_code=429,
            headers={
                "Retry-After": str(rate_limit_exc.retry_after) if rate_limit_exc.retry_after else "60",
                "X-RateLimit-Limit": str(rate_limit_exc.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(datetime.now(timezone.utc).timestamp()) + (rate_limit_exc.retry_after or 60))
            }
        )
    else:
        response = Response(
            content="Rate limit aşıldı. Lütfen daha sonra tekrar deneyin.",
            status_code=429,
            headers={"Retry-After": "60"}
        )
    
    return response

# HTTP Bearer token scheme
security = HTTPBearer()

class SecurityConfig:
    """Güvenlik yapılandırma sınıfı"""
    
    # Şifre gereksinimleri
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_NUMBERS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Session yapılandırması
    SESSION_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # API güvenlik
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File upload güvenlik
    ALLOWED_FILE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

class PasswordValidator:
    """Şifre doğrulama sınıfı"""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Şifre güvenlik gereksinimlerini kontrol eder"""
        errors = []
        
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            errors.append(f"Şifre en az {SecurityConfig.MIN_PASSWORD_LENGTH} karakter olmalıdır")
        
        if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            errors.append("Şifre en az bir büyük harf içermelidir")
        
        if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            errors.append("Şifre en az bir küçük harf içermelidir")
        
        if SecurityConfig.REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
            errors.append("Şifre en az bir rakam içermelidir")
        
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not any(c in string.punctuation for c in password):
            errors.append("Şifre en az bir özel karakter içermelidir")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": calculate_password_strength(password)
        }

def calculate_password_strength(password: str) -> str:
    """Şifre gücünü hesaplar"""
    score = 0
    
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1
    
    if score <= 2:
        return "Zayıf"
    elif score <= 4:
        return "Orta"
    else:
        return "Güçlü"

def hash_password(password: str) -> str:
    """Şifreyi hashler"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifreyi doğrular"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Access token oluşturur"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # JWT ID ekle (blacklisting için gerekli)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "type": "access", "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Refresh token oluşturur"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # JWT ID ekle (blacklisting için gerekli)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_token_jti(token: str) -> Optional[str]:
    """Token'dan JTI'yi çıkarır (doğrulama yapmadan)"""
    try:
        # Token'ı doğrulamadan sadece decode et
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload.get("jti")
    except JWTError as e:
        logger.warning(f"JWT decode hatası get_token_jti fonksiyonunda: {str(e)}")
        logger.warning(f"Token başlangıcı: {token[:20]}..." if len(token) > 20 else f"Token: {token}")
        return None

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Token'ı doğrular ve blacklist kontrolü yapar"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],options={"verify_exp": True})
        if payload.get("type") != token_type:
            return None
        
        # Blacklist kontrolü
        jti = payload.get("jti")
        if jti and is_token_blacklisted(jti):
            return None
            
        return payload
    except ExpiredSignatureError:
        logger.warning("Token süresi dolmuş")
        return None
    except JWTError:
        logger.warning("Geçersiz token")
        return None

def is_token_blacklisted(jti: str) -> bool:
    """Token'ın blacklist'te olup olmadığını kontrol eder"""
    db = SessionLocal()
    try:
        blacklisted = db.query(models.BlacklistedToken).filter(
            models.BlacklistedToken.token_jti == jti,
            models.BlacklistedToken.expires_at > datetime.now(timezone.utc)
        ).first()
        return blacklisted is not None
    finally:
        db.close()

def blacklist_token(token: str, user_id: Optional[int] = None, reason: str = "logout"):
    """Token'ı blacklist'e ekler"""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        token_type = payload.get("type", "access")
        expires_at = datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc)
        
        if not jti:
            return False
        
        db = SessionLocal()
        try:
            # Zaten blacklist'te mi kontrol et
            existing = db.query(models.BlacklistedToken).filter(
                models.BlacklistedToken.token_jti == jti
            ).first()
            
            if not existing:
                blacklisted_token = models.BlacklistedToken(
                    token_jti=jti,
                    user_id=user_id,
                    token_type=token_type,
                    expires_at=expires_at,
                    reason=reason
                )
                db.add(blacklisted_token)
                db.commit()
            
            return True
        finally:
            db.close()
            
    except JWTError as e:
        logger.error(f"JWT decode hatası blacklist_token fonksiyonunda: {str(e)}")
        logger.error(f"Token başlangıcı: {token[:20]}..." if len(token) > 20 else f"Token: {token}")
        logger.error(f"User ID: {user_id}, Reason: {reason}")
        return False

def cleanup_expired_blacklisted_tokens():
    """Süresi dolmuş blacklist token'larını temizler"""

    
    db = SessionLocal()
    try:
        expired_tokens = db.query(models.BlacklistedToken).filter(
            models.BlacklistedToken.expires_at <= datetime.now(timezone.utc)
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
        logger.info(f"Temizlenen süresi dolmuş blacklist token sayısı: {count}")
        return count
    finally:
        db.close()

class LoginAttemptTracker:
    """Giriş denemesi takip sınıfı"""
    
    @staticmethod
    def get_attempt_key(identifier: str) -> str:
        """Giriş denemesi anahtarı oluşturur"""
        return f"login_attempts:{identifier}"
    
    @staticmethod
    def get_lockout_key(identifier: str) -> str:
        """Kilitleme anahtarı oluşturur"""
        return f"lockout:{identifier}"
    
    @staticmethod
    def record_failed_attempt(identifier: str) -> int:
        """Başarısız giriş denemesini kaydeder"""
        if not redis_client:
            # DÜZELTME: Redis yoksa, saldırgana kilitlenme mekanizmasının olmadığını belli etmemeliyiz.
            # 0 döndürerek (ve hiçbir zaman kilitlemeyerek) sistemi çalışır tutuyoruz.
            # Güvenlik logu burada yeterlidir.
            logger.warning(f"Redis bağlantısı yok, {identifier} için kilitleme devre dışı.")
            return 0  # 0 döndür ki, endpoint'te MAX_LOGIN_ATTEMPTS kontrolünden geçsin.
        
        key = LoginAttemptTracker.get_attempt_key(identifier)
        attempts = redis_client.incr(key)
        redis_client.expire(key, SecurityConfig.LOCKOUT_DURATION_MINUTES * 60)
        
        if attempts >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
            lockout_key = LoginAttemptTracker.get_lockout_key(identifier)
            redis_client.setex(
                lockout_key, 
                SecurityConfig.LOCKOUT_DURATION_MINUTES * 60, 
                "locked"
            )
            logger.warning(f"Hesap kilitlendi: {identifier}")
        
        return attempts
    
    @staticmethod
    def clear_attempts(identifier: str):
        """Giriş denemelerini temizler"""
        if not redis_client:
            return
        
        attempt_key = LoginAttemptTracker.get_attempt_key(identifier)
        lockout_key = LoginAttemptTracker.get_lockout_key(identifier)
        redis_client.delete(attempt_key, lockout_key)
    
    @staticmethod
    def is_locked(identifier: str) -> bool:
        """Hesabın kilitli olup olmadığını kontrol eder"""
        if not redis_client:
            return False
        
        lockout_key = LoginAttemptTracker.get_lockout_key(identifier)
        return redis_client.exists(lockout_key)
    
    @staticmethod
    def get_remaining_attempts(identifier: str) -> int:
        """Kalan giriş denemesi sayısını döndürür"""
        if not redis_client:
            return SecurityConfig.MAX_LOGIN_ATTEMPTS
        
        key = LoginAttemptTracker.get_attempt_key(identifier)
        attempts = redis_client.get(key)
        if attempts:
            return max(0, SecurityConfig.MAX_LOGIN_ATTEMPTS - int(attempts))
        return SecurityConfig.MAX_LOGIN_ATTEMPTS

def get_db():
    """Veritabanı session'ı döndürür"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """Mevcut kullanıcıyı token'dan alır"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz kimlik bilgileri",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials, "access")
        if payload is None:
            raise credentials_exception
        
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hesap aktif değil"
        )
    
    return user

async def get_current_admin_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Admin yetkisi olan kullanıcıyı döndürür"""
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin yetkisi gerekli"
        )
    return current_user

def create_api_key() -> str:
    """API anahtarı oluşturur"""
    return secrets.token_urlsafe(32)

def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """API anahtarını doğrular"""
    return hmac.compare_digest(
        hashlib.sha256(api_key.encode()).hexdigest(),
        stored_hash
    )

def hash_api_key(api_key: str) -> str:
    """API anahtarını hashler"""
    return hashlib.sha256(api_key.encode()).hexdigest()

class SecurityHeaders:
    """Güvenlik başlıkları sınıfı"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Güvenlik başlıklarını döndürür"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }

def validate_file_upload(file_content: bytes, filename: str) -> bool:
    """Dosya yükleme güvenlik kontrolü"""
    # Dosya boyutu kontrolü
    if len(file_content) > SecurityConfig.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Dosya boyutu {SecurityConfig.MAX_FILE_SIZE // (1024*1024)}MB'dan büyük olamaz"
        )
    
    # Dosya uzantısı kontrolü
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in SecurityConfig.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"İzin verilen dosya türleri: {', '.join(SecurityConfig.ALLOWED_FILE_EXTENSIONS)}"
        )
    
    # Gelişmiş dosya içeriği kontrolü (magic bytes) - Daha uzun imzalar
    image_signatures = {
        # JPEG - 3 byte yeterli
        b'\xff\xd8\xff': 'jpg',
        # PNG - 8 byte tam imza
        b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a': 'png',
        # GIF87a veya GIF89a - 6 byte
        b'\x47\x49\x46\x38\x37\x61': 'gif87a',
        b'\x47\x49\x46\x38\x39\x61': 'gif89a',
        # WebP - 12 byte tam imza (RIFF + WebP)
        b'\x52\x49\x46\x46': 'riff_container',  # İlk 4 byte RIFF
    }
    
    # Özel WebP kontrolü (RIFF container içinde WebP olmalı)
    def is_valid_webp(content: bytes) -> bool:
        if len(content) < 12:
            return False
        return (content[:4] == b'\x52\x49\x46\x46' and 
                content[8:12] == b'\x57\x45\x42\x50')
    
    # PNG için tam 8 byte kontrol
    def is_valid_png(content: bytes) -> bool:
        if len(content) < 8:
            return False
        return content[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
    
    # GIF için 6 byte kontrol
    def is_valid_gif(content: bytes) -> bool:
        if len(content) < 6:
            return False
        return (content[:6] == b'\x47\x49\x46\x38\x37\x61' or 
                content[:6] == b'\x47\x49\x46\x38\x39\x61')
    
    # JPEG için 3 byte kontrol
    def is_valid_jpeg(content: bytes) -> bool:
        if len(content) < 3:
            return False
        return content[:3] == b'\xff\xd8\xff'
    
    # Format kontrolü
    is_valid_image = (
        is_valid_jpeg(file_content) or
        is_valid_png(file_content) or
        is_valid_gif(file_content) or
        is_valid_webp(file_content)
    )
    
    if not is_valid_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz dosya formatı - Dosya içeriği uzantısıyla uyuşmuyor"
        )
    
    return True

def sanitize_input(input_string: str, allow_html: bool = False) -> str:
    """Kullanıcı girdisini temizler ve XSS saldırılarına karşı korur"""
    if not input_string:
        return ""
    
    # Başındaki ve sonundaki boşlukları temizle
    cleaned = input_string.strip()
    
    if not allow_html:
        # HTML/XML karakterlerini escape et
        html_escape_table = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;",
        }
        
        for char, escape in html_escape_table.items():
            cleaned = cleaned.replace(char, escape)
        
        # Potansiyel JavaScript injection pattern'lerini temizle
        dangerous_patterns = [
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "onclick=",
            "onmouseover=",
            "onfocus=",
            "onblur=",
            "onchange=",
            "onsubmit=",
            "<script",
            "</script>",
            "eval(",
            "expression(",
            "url(",
            "import(",
        ]
        
        cleaned_lower = cleaned.lower()
        for pattern in dangerous_patterns:
            if pattern in cleaned_lower:
                # Pattern bulunursa, güvenli alternatifle değiştir
                cleaned = cleaned.replace(pattern, f"[FILTERED:{pattern.upper()}]")
                cleaned = cleaned.replace(pattern.upper(), f"[FILTERED:{pattern.upper()}]")
    
    # Null byte injection koruması
    cleaned = cleaned.replace('\x00', '')
    
    # Çok uzun girdi koruması (DoS saldırısı önleme)
    if len(cleaned) > 10000:  # 10KB limit
        cleaned = cleaned[:10000] + "...[TRUNCATED]"
    
    return cleaned

def validate_sql_input(input_string: str) -> bool:
    """SQL injection pattern'lerini kontrol eder (ek güvenlik katmanı)"""
    if not input_string:
        return True
    
    # Tehlikeli SQL pattern'leri (ORM kullanıyoruz ama ek güvenlik)
    dangerous_sql_patterns = [
        "union select",
        "drop table",
        "delete from",
        "insert into",
        "update set",
        "alter table",
        "create table",
        "exec(",
        "execute(",
        "sp_",
        "xp_",
        "--",
        "/*",
        "*/",
        "@@",
        "char(",
        "nchar(",
        "varchar(",
        "nvarchar(",
        "waitfor delay",
        "benchmark(",
    ]
    
    input_lower = input_string.lower()
    for pattern in dangerous_sql_patterns:
        if pattern in input_lower:
            logger.warning(f"Potansiyel SQL injection denemesi tespit edildi: {pattern}")
            return False
    
    return True

# Güvenlik olayları için audit log
class SecurityAuditLogger:
    """Güvenlik audit log sınıfı"""
    
    @staticmethod
    def log_security_event(event_type: str, user_id: Optional[int], details: Dict[str, Any], request: Request):
        """Güvenlik olayını loglar"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": get_remote_address(request),
            "user_agent": request.headers.get("user-agent"),
            "details": details
        }
        
        logger.info(f"SECURITY_EVENT: {log_entry}")
        
        # Redis'e de kaydet (opsiyonel)
        if redis_client:
            try:
                redis_client.lpush("security_events", str(log_entry))
                redis_client.ltrim("security_events", 0, 999)  # Son 1000 olayı tut
            except Exception as e:
                logger.error(f"Redis'e security event kaydedilemedi: {e}")