"""
Geçici kayıt sistemi - Redis ile Production-Ready implementasyon
Kullanıcılar doğrulama kodunu girmeden önce Redis'te saklanır
"""
from datetime import datetime, timedelta
from typing import Optional
import json
import redis
from redis.exceptions import RedisError
import logging

logger = logging.getLogger(__name__)


class PendingRegistration:
    """Bekleyen kayıt bilgisi"""
    def __init__(self, email: str, hashed_password: str, first_name: str, 
                 last_name: str, phone: Optional[str], address: Optional[str],
                 verification_code: str, created_by_ip: str,
                 is_admin: bool = False,
                 created_at: Optional[datetime] = None,
                 expires_at: Optional[datetime] = None):
        self.email = email
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.address = address
        self.verification_code = verification_code
        self.created_by_ip = created_by_ip
        self.is_admin = is_admin
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at or (datetime.now() + timedelta(hours=24))
    
    def is_expired(self) -> bool:
        """Kayıt süresi dolmuş mu?"""
        return datetime.now() > self.expires_at
    
    def verify_code(self, code: str) -> bool:
        """Doğrulama kodunu kontrol et"""
        return self.verification_code == code and not self.is_expired()
    
    def to_dict(self) -> dict:
        """Dict'e çevir (Redis'e kaydetmek için)"""
        return {
            "email": self.email,
            "hashed_password": self.hashed_password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "address": self.address,
            "verification_code": self.verification_code,
            "created_by_ip": self.created_by_ip,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PendingRegistration':
        """Dict'ten oluştur (Redis'ten okumak için)"""
        return cls(
            email=data["email"],
            hashed_password=data["hashed_password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone"),
            address=data.get("address"),
            verification_code=data["verification_code"],
            created_by_ip=data["created_by_ip"],
            is_admin=data.get("is_admin", False),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"])
        )


class RedisPendingRegistrationManager:
    """Redis ile bekleyen kayıtları yönet - Production Ready"""
    
    # Redis key prefix
    KEY_PREFIX = "pending_registration:"
    
    # TTL (Time To Live) - 24 saat
    TTL_SECONDS = 24 * 60 * 60
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Redis bağlantısını başlat
        
        Args:
            redis_url: Redis bağlantı URL'i (örn: redis://localhost:6379/0)
        """
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Bağlantıyı test et
            self.redis_client.ping()
            logger.info("✅ Redis bağlantısı başarılı")
        except RedisError as e:
            logger.error(f"❌ Redis bağlantı hatası: {e}")
            raise
    
    def _get_key(self, email: str, is_admin: bool = False) -> str:
        """Email ve is_admin için Redis key oluştur"""
        admin_suffix = "_admin" if is_admin else "_user"
        return f"{self.KEY_PREFIX}{email.lower()}{admin_suffix}"
    
    def add_registration(self, registration: PendingRegistration) -> bool:
        """
        Yeni bekleyen kayıt ekle
        
        Args:
            registration: PendingRegistration nesnesi
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            key = self._get_key(registration.email, registration.is_admin)
            data = json.dumps(registration.to_dict())
            
            # Redis'e kaydet ve TTL ayarla
            self.redis_client.setex(
                key,
                self.TTL_SECONDS,
                data
            )
            
            admin_type = "admin" if registration.is_admin else "user"
            logger.info(f"✅ Pending registration eklendi: {registration.email} ({admin_type})")
            return True
            
        except RedisError as e:
            logger.error(f"❌ Redis kayıt hatası: {e}")
            return False
    
    def get_registration(self, email: str, is_admin: bool = False) -> Optional[PendingRegistration]:
        """
        Email ve is_admin'e göre bekleyen kaydı getir
        
        Args:
            email: Kullanıcı email adresi
            is_admin: Admin kaydı mı?
            
        Returns:
            PendingRegistration veya None
        """
        try:
            key = self._get_key(email, is_admin)
            data = self.redis_client.get(key)
            
            if not data:
                return None
            
            registration = PendingRegistration.from_dict(json.loads(data))
            
            # Süresi dolmuş mu kontrol et
            if registration.is_expired():
                self.remove_registration(email, is_admin)
                return None
            
            return registration
            
        except (RedisError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"❌ Redis okuma hatası: {e}")
            return None
    
    def remove_registration(self, email: str, is_admin: bool = False) -> bool:
        """
        Bekleyen kaydı sil
        
        Args:
            email: Kullanıcı email adresi
            is_admin: Admin kaydı mı?
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            key = self._get_key(email, is_admin)
            result = self.redis_client.delete(key)
            
            if result:
                admin_type = "admin" if is_admin else "user"
                logger.info(f"✅ Pending registration silindi: {email} ({admin_type})")
            
            return bool(result)
            
        except RedisError as e:
            logger.error(f"❌ Redis silme hatası: {e}")
            return False
    
    def verify_and_remove(self, email: str, code: str, is_admin: bool = False) -> Optional[PendingRegistration]:
        """
        Kodu doğrula ve kaydı sil
        
        Args:
            email: Kullanıcı email adresi
            code: Doğrulama kodu
            is_admin: Admin kaydı mı?
            
        Returns:
            PendingRegistration veya None
        """
        try:
            registration = self.get_registration(email, is_admin)
            
            if not registration:
                admin_type = "admin" if is_admin else "user"
                logger.warning(f"⚠️ Pending registration bulunamadı: {email} ({admin_type})")
                return None
            
            if not registration.verify_code(code):
                admin_type = "admin" if is_admin else "user"
                logger.warning(f"⚠️ Geçersiz doğrulama kodu: {email} ({admin_type})")
                return None
            
            # Doğrulama başarılı, kaydı sil
            self.remove_registration(email, is_admin)
            admin_type = "admin" if is_admin else "user"
            logger.info(f"✅ Doğrulama başarılı: {email} ({admin_type})")
            
            return registration
            
        except Exception as e:
            logger.error(f"❌ Doğrulama hatası: {e}")
            return None
    
    def update_verification_code(self, email: str, new_code: str, is_admin: bool = False) -> bool:
        """
        Doğrulama kodunu güncelle (resend için)
        
        Args:
            email: Kullanıcı email adresi
            new_code: Yeni doğrulama kodu
            is_admin: Admin kaydı mı?
            
        Returns:
            bool: Başarılı ise True
        """
        try:
            registration = self.get_registration(email, is_admin)
            
            if not registration:
                return False
            
            # Yeni kod ile güncelle
            registration.verification_code = new_code
            
            # TTL'i sıfırla (24 saat daha)
            registration.expires_at = datetime.now() + timedelta(hours=24)
            
            return self.add_registration(registration)
            
        except Exception as e:
            logger.error(f"❌ Kod güncelleme hatası: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        İstatistikleri getir
        
        Returns:
            dict: Toplam pending registration sayısı ve email listesi
        """
        try:
            # Tüm pending registration key'lerini getir
            pattern = f"{self.KEY_PREFIX}*"
            keys = list(self.redis_client.scan_iter(match=pattern))
            
            # Email'leri çıkar
            emails = [key.replace(self.KEY_PREFIX, "") for key in keys]
            
            return {
                "total_pending": len(emails),
                "emails": emails,
                "redis_connected": True
            }
            
        except RedisError as e:
            logger.error(f"❌ Redis stats hatası: {e}")
            return {
                "total_pending": 0,
                "emails": [],
                "redis_connected": False,
                "error": str(e)
            }
    
    def cleanup_expired(self) -> int:
        """
        Süresi dolmuş kayıtları temizle
        
        Returns:
            int: Temizlenen kayıt sayısı
        """
        try:
            pattern = f"{self.KEY_PREFIX}*"
            keys = list(self.redis_client.scan_iter(match=pattern))
            
            cleaned = 0
            for key in keys:
                email = key.replace(self.KEY_PREFIX, "")
                registration = self.get_registration(email)
                
                # get_registration zaten expired olanları siler
                if not registration:
                    cleaned += 1
            
            if cleaned > 0:
                logger.info(f"✅ {cleaned} expired registration temizlendi")
            
            return cleaned
            
        except RedisError as e:
            logger.error(f"❌ Cleanup hatası: {e}")
            return 0
    
    def health_check(self) -> dict:
        """
        Redis sağlık kontrolü
        
        Returns:
            dict: Sağlık durumu bilgileri
        """
        try:
            # Ping testi
            ping_result = self.redis_client.ping()
            
            # Info bilgisi
            info = self.redis_client.info()
            
            return {
                "status": "healthy",
                "ping": ping_result,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
            
        except RedisError as e:
            logger.error(f"❌ Health check hatası: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global instance - Environment variable'dan Redis URL al
import os
from dotenv import load_dotenv

load_dotenv()

# Redis URL'i environment variable'dan al, yoksa localhost kullan
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    pending_registration_manager = RedisPendingRegistrationManager(REDIS_URL)
except RedisError as e:
    logger.error(f"❌ Redis başlatılamadı: {e}")
    logger.warning("⚠️ Fallback olarak in-memory manager kullanılacak")
    # Fallback: In-memory manager kullan
    from backend.pending_registrations import PendingRegistrationManager
    pending_registration_manager = PendingRegistrationManager()