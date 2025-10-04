"""
Geçici kayıt sistemi - Kullanıcılar doğrulama kodunu girmeden önce burada saklanır
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import threading

class PendingRegistration:
    """Bekleyen kayıt bilgisi"""
    def __init__(self, email: str, hashed_password: str, first_name: str, 
                 last_name: str, phone: Optional[str], address: Optional[str],
                 verification_code: str, created_by_ip: str):
        self.email = email
        self.hashed_password = hashed_password
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.address = address
        self.verification_code = verification_code
        self.created_by_ip = created_by_ip
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(hours=24)
    
    def is_expired(self) -> bool:
        """Kayıt süresi dolmuş mu?"""
        return datetime.now() > self.expires_at
    
    def verify_code(self, code: str) -> bool:
        """Doğrulama kodunu kontrol et"""
        return self.verification_code == code and not self.is_expired()


class PendingRegistrationManager:
    """Bekleyen kayıtları yönet"""
    
    def __init__(self):
        self._registrations: Dict[str, PendingRegistration] = {}
        self._lock = threading.Lock()
    
    def add_registration(self, registration: PendingRegistration):
        """Yeni bekleyen kayıt ekle"""
        with self._lock:
            # Eski kaydı temizle
            self._cleanup_expired()
            # Yeni kaydı ekle
            self._registrations[registration.email.lower()] = registration
    
    def get_registration(self, email: str) -> Optional[PendingRegistration]:
        """Email'e göre bekleyen kaydı getir"""
        with self._lock:
            self._cleanup_expired()
            return self._registrations.get(email.lower())
    
    def remove_registration(self, email: str):
        """Bekleyen kaydı sil"""
        with self._lock:
            email_lower = email.lower()
            if email_lower in self._registrations:
                del self._registrations[email_lower]
    
    def verify_and_remove(self, email: str, code: str) -> Optional[PendingRegistration]:
        """Kodu doğrula ve kaydı sil"""
        with self._lock:
            self._cleanup_expired()
            registration = self._registrations.get(email.lower())
            
            if registration and registration.verify_code(code):
                # Doğrulama başarılı, kaydı sil ve döndür
                del self._registrations[email.lower()]
                return registration
            
            return None
    
    def _cleanup_expired(self):
        """Süresi dolmuş kayıtları temizle"""
        expired_emails = [
            email for email, reg in self._registrations.items()
            if reg.is_expired()
        ]
        for email in expired_emails:
            del self._registrations[email]
    
    def get_stats(self) -> dict:
        """İstatistikleri getir"""
        with self._lock:
            self._cleanup_expired()
            return {
                "total_pending": len(self._registrations),
                "emails": list(self._registrations.keys())
            }


# Global instance
pending_registration_manager = PendingRegistrationManager()