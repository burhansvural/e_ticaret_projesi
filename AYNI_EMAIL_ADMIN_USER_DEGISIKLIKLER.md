# Aynı Email ile Admin ve User Kaydı - Değişiklikler

## 📋 Özet
Bu değişiklikler, aynı email adresinin hem admin hem de normal kullanıcı olarak kayıt olabilmesini sağlar.

## 🎯 Yapılan Değişiklikler

### 1. **Backend Models** (`backend/models.py`)
- ✅ Email alanındaki `unique=True` constraint'i kaldırıldı
- ✅ `__table_args__` ile `(email, is_admin)` composite unique constraint eklendi
- ✅ Artık aynı email farklı `is_admin` değerleri ile kayıt olabilir

```python
__table_args__ = (
    UniqueConstraint('email', 'is_admin', name='uq_email_is_admin'),
)
```

### 2. **Pending Registrations Redis** (`backend/pending_registrations_redis.py`)
- ✅ `PendingRegistration` sınıfına `is_admin` parametresi eklendi
- ✅ `to_dict()` ve `from_dict()` metodları güncellendi
- ✅ Redis key'leri artık email + is_admin kombinasyonunu içeriyor:
  - Admin: `pending_registration:user@example.com_admin`
  - User: `pending_registration:user@example.com_user`
- ✅ Tüm metodlar (`add_registration`, `get_registration`, `verify_and_remove`, vb.) `is_admin` parametresini destekliyor

### 3. **Backend API Endpoints** (`backend/main.py`)

#### Kayıt Endpoint'i (`/users/register`)
- ✅ `is_admin` bilgisi request'ten alınıyor
- ✅ Email kontrolü artık `email + is_admin` kombinasyonuna göre yapılıyor
- ✅ Hata mesajları kullanıcı tipini belirtiyor ("admin" veya "kullanıcı")
- ✅ Pending registration oluşturulurken `is_admin` bilgisi ekleniyor

#### Email Doğrulama Endpoint'i (`/users/verify-email`)
- ✅ `is_admin` bilgisi request'ten alınıyor
- ✅ Doğrulama sırasında `is_admin` parametresi kullanılıyor
- ✅ Veritabanına kayıt sırasında `is_admin` bilgisi ekleniyor
- ✅ Güvenlik logları `is_admin` bilgisini içeriyor

#### Login Endpoint'i (`/users/login`)
- ✅ Kullanıcı sorgusu artık `email + is_admin` kombinasyonuna göre yapılıyor
- ✅ Hata mesajları kullanıcı tipini belirtiyor
- ✅ Güvenlik logları `is_admin` bilgisini içeriyor

### 4. **Backend Schemas** (`backend/schemas.py`)

#### UserLogin Schema
- ✅ `is_admin: bool = False` alanı eklendi
- ✅ Varsayılan değer `False` (normal kullanıcı girişi)

#### EmailVerificationRequest Schema
- ✅ `is_admin: bool = False` alanı eklendi
- ✅ Varsayılan değer `False` (normal kullanıcı doğrulaması)

### 5. **Admin Panel** (`admin_panel/main.py`)

#### Login İşlemi
- ✅ Login request'ine `"is_admin": True` eklendi
- ✅ Admin paneli artık sadece admin hesapları ile giriş yapıyor

#### Email Doğrulama
- ✅ Doğrulama request'ine `"is_admin": True` eklendi
- ✅ Admin kayıtları doğru şekilde doğrulanıyor

## 🗄️ Veritabanı Migration

### Migration Script: `migrate_email_admin_constraint.py`
Veritabanı şemasını güncellemek için migration script'i oluşturuldu.

**Çalıştırma:**
```bash
python migrate_email_admin_constraint.py
```

**Ne Yapar:**
1. ✅ Mevcut veritabanının yedeğini alır
2. ✅ Yeni tablo yapısını oluşturur (composite unique constraint ile)
3. ✅ Mevcut verileri yeni tabloya kopyalar
4. ✅ Eski tabloyu siler ve yeni tabloyu yerine koyar

**⚠️ ÖNEMLİ:** Migration'ı çalıştırmadan önce:
- Backend'i durdurun
- Veritabanının yedeğini alın (script otomatik yedek alır ama ekstra yedek önerilir)

## 🧪 Test Senaryoları

### Senaryo 1: Aynı Email ile Admin ve User Kaydı
```
1. user@example.com ile normal kullanıcı kaydı yap
2. user@example.com ile admin kaydı yap
3. Her iki kayıt da başarılı olmalı
```

### Senaryo 2: Aynı Tip ile Tekrar Kayıt
```
1. user@example.com ile admin kaydı yap
2. user@example.com ile tekrar admin kaydı yapmaya çalış
3. "Bu e-posta adresi zaten admin olarak kayıtlı" hatası alınmalı
```

### Senaryo 3: Login İşlemleri
```
1. user@example.com ile hem admin hem user hesabı oluştur
2. Admin panel'den giriş yap (is_admin=true ile)
3. Normal kullanıcı uygulamasından giriş yap (is_admin=false ile)
4. Her iki giriş de başarılı olmalı ve doğru hesaba yönlendirmeli
```

## 📝 Kullanım Örnekleri

### Admin Kaydı (Admin Panel)
```python
# Admin panel otomatik olarak is_admin=True gönderir
{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "first_name": "Admin",
    "last_name": "User",
    "is_admin": True  # Admin kaydı
}
```

### Normal Kullanıcı Kaydı
```python
# Normal kullanıcı uygulaması is_admin=False gönderir (veya hiç göndermez)
{
    "email": "admin@example.com",  # Aynı email olabilir!
    "password": "SecurePass123!",
    "first_name": "Normal",
    "last_name": "User",
    "is_admin": False  # Normal kullanıcı kaydı
}
```

### Admin Login (Admin Panel)
```python
{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "is_admin": True  # Admin hesabına giriş
}
```

### Normal Kullanıcı Login
```python
{
    "email": "admin@example.com",  # Aynı email!
    "password": "SecurePass123!",
    "is_admin": False  # Normal kullanıcı hesabına giriş
}
```

## 🔒 Güvenlik Notları

1. **Ayrı Hesaplar**: Aynı email ile oluşturulan admin ve user hesapları tamamen ayrı hesaplardır
2. **Ayrı Şifreler**: Her hesabın kendi şifresi vardır
3. **Ayrı Doğrulama**: Her hesap ayrı ayrı email doğrulaması gerektirir
4. **Güvenlik Logları**: Tüm işlemler `is_admin` bilgisi ile loglanır
5. **Redis Separation**: Pending registrations Redis'te ayrı key'lerle saklanır

## ⚠️ Dikkat Edilmesi Gerekenler

1. **Migration Zorunlu**: Mevcut veritabanını kullanıyorsanız migration script'ini çalıştırmalısınız
2. **Yedek Alın**: Migration öncesi mutlaka veritabanı yedeği alın
3. **Backend Restart**: Migration sonrası backend'i yeniden başlatın
4. **Frontend Uyumluluğu**: Normal kullanıcı frontend'i de `is_admin=false` göndermelidir
5. **Login Ayrımı**: Login sırasında doğru `is_admin` değeri gönderilmelidir

## 🚀 Deployment Adımları

1. **Backend'i Durdur**
   ```bash
   # Backend process'ini durdur
   ```

2. **Veritabanı Yedeği Al**
   ```bash
   cp ecommerce.db ecommerce.db.backup_$(date +%Y%m%d_%H%M%S)
   ```

3. **Migration'ı Çalıştır**
   ```bash
   python migrate_email_admin_constraint.py
   ```

4. **Backend'i Başlat**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

5. **Test Et**
   - Admin panel ile admin kaydı yap
   - Aynı email ile normal kullanıcı kaydı yap
   - Her iki hesapla da giriş yap

## 📊 Değişiklik İstatistikleri

- **Değiştirilen Dosyalar**: 5
- **Yeni Dosyalar**: 2 (migration script + bu dokümantasyon)
- **Toplam Satır Değişikliği**: ~150 satır
- **Yeni Özellikler**: Composite unique constraint, is_admin parametresi
- **Geriye Uyumluluk**: Varsayılan değerler ile sağlandı

## 🐛 Bilinen Sorunlar ve Çözümler

### Sorun: "UNIQUE constraint failed"
**Çözüm**: Migration script'ini çalıştırın

### Sorun: "Doğrulama kodu geçersiz"
**Çözüm**: Doğrulama sırasında doğru `is_admin` değeri gönderildiğinden emin olun

### Sorun: "Geçersiz kullanıcı adı/şifre"
**Çözüm**: Login sırasında doğru `is_admin` değeri gönderildiğinden emin olun

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Migration yedek dosyasını kontrol edin
2. Backend loglarını inceleyin
3. Redis'in çalıştığından emin olun
4. Veritabanı constraint'lerini kontrol edin

---

**Son Güncelleme**: 2024
**Versiyon**: 1.0
**Durum**: ✅ Tamamlandı ve Test Edilmeye Hazır