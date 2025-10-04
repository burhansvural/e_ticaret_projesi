# Değişiklik Günlüğü

Bu dosya, E-Ticaret Projesi'ndeki tüm önemli değişiklikleri ve güncellemeleri içerir.

## [2.3.0] - 30 Eylül 2025 - Pazartesi - Saat 07:17

### 🔒 Enterprise Seviye Güvenlik Tamamlandı

#### JWT Token Blacklisting Sistemi Implementasyonu
- **JWT ID (JTI) Sistemi**: 
  - Her access ve refresh token'a benzersiz JTI atanması
  - `get_token_jti()` fonksiyonu ile token'dan JTI çıkarma
  - Token doğrulama sırasında blacklist kontrolü
  - `BlacklistedToken` modeli ile veritabanı entegrasyonu

- **Anında Token İptali**:
  - Logout endpoint'inde hem access hem refresh token'ların blacklist'e eklenmesi
  - `blacklist_token()` fonksiyonu ile token iptal mekanizması
  - `is_token_blacklisted()` ile hızlı blacklist kontrolü
  - Token iptal nedeni tracking sistemi

#### Gelişmiş Session Güvenliği
- **Session Token Güvenliği İyileştirildi**:
  - Access token'ın kendisi yerine sadece JTI'sinin DB'ye kaydedilmesi
  - Veritabanı sızıntısı durumunda token güvenliğinin artırılması
  - `UserSession` modelinde güvenli session token saklama
  - IP adresi ve User-Agent tracking korunması

#### Otomatik Güvenlik Bakımı
- **Background Task Sistemi**:
  - `periodic_blacklist_cleanup()` fonksiyonu ile 24 saatlik temizlik döngüsü
  - FastAPI startup/shutdown event'leri ile task yönetimi
  - `cleanup_expired_blacklisted_tokens()` otomatik çağrılması
  - Asyncio ile non-blocking background işlemler

#### Endpoint Güvenlik Düzeltmeleri
- **Admin Authorization Eklendi**:
  - `/users/` endpoint'ine `get_current_admin_user` dependency eklenmesi
  - Kullanıcı listesi erişiminin sadece adminlerle sınırlandırılması
  - Güvenlik açığının kapatılması

- **Pydantic v2 Uyumluluğu**:
  - `schemas.py` dosyasında `regex` → `pattern` dönüşümü
  - `UserCreate.phone` ve `TwoFactorVerify.token` alanları güncellendi
  - Server başlatma hatalarının çözülmesi

#### Teknik İyileştirmeler
- **Import Optimizasyonu**:
  - `get_token_jti` fonksiyonunun main.py'ye import edilmesi
  - Security modülü entegrasyonunun tamamlanması
  - Tüm güvenlik fonksiyonlarının doğru şekilde erişilebilir olması

- **Error Handling**:
  - Background task'larda exception handling
  - Blacklist temizliği sırasında hata yönetimi
  - Logging ile detaylı hata takibi

### 🛡️ Güvenlik Metrikleri (Güncel)

```
🔐 JWT Security: JTI-based blacklisting ✅
🛡️ Session Management: Secure JTI storage ✅
⚡ Auto Cleanup: 24h scheduled maintenance ✅
🔒 Admin Security: Endpoint authorization ✅
📁 Token Security: Database-backed invalidation ✅
🌐 Compatibility: Pydantic v2 support ✅
📝 Background Tasks: Asyncio maintenance ✅
🚫 Zero Trust: All endpoints secured ✅
```

### 🔄 Migration Notes

#### Veritabanı Değişiklikleri
- `BlacklistedToken` tablosu zaten mevcut (v2.2.0'dan)
- `UserSession.session_token` alanı artık JTI değeri saklıyor
- Mevcut session'lar otomatik olarak uyumlu

#### API Değişiklikleri
- `/users/` endpoint artık admin yetkisi gerektiriyor
- Logout işlemi artık token'ları anında geçersiz kılıyor
- Background cleanup otomatik olarak çalışıyor

---

## [2.2.0] - 29 Eylül 2025 - Pazartesi - Saat 21:08

### 🔒 Güvenlik Katmanları Implementasyonu

#### Kapsamlı Backend Güvenlik Sistemi
- **JWT Token Sistemi**: 
  - Access token (30 dakika) ve refresh token (7 gün) sistemi
  - HS256 algoritması ile güvenli token imzalama
  - Token doğrulama ve yenileme mekanizması
  - Bearer token authentication

- **Gelişmiş Şifre Güvenliği**:
  - Bcrypt ile güçlü şifre hashleme
  - Şifre karmaşıklık kontrolü (büyük/küçük harf, rakam, özel karakter)
  - Şifre gücü hesaplama algoritması
  - Şifre geçmişi ve değişiklik takibi

- **Rate Limiting ve Brute Force Koruması**:
  - Redis tabanlı rate limiting sistemi
  - IP bazlı istek sınırlaması (1000/saat varsayılan)
  - Giriş denemesi takibi (5 deneme sonrası kilitleme)
  - 15 dakikalık hesap kilitleme sistemi
  - Şüpheli aktivite tespiti ve loglama

#### Güvenlik Middleware Sistemi
- **CORS Yapılandırması**: Güvenli cross-origin resource sharing
- **Güvenlik Headers**: XSS, CSRF, Clickjacking koruması
- **Request Validation**: Boyut kontrolü ve content-type doğrulama
- **IP Whitelisting**: Admin paneli için IP kısıtlaması
- **Suspicious User-Agent Detection**: Güvenlik tarayıcı tespiti

#### Dosya Güvenliği
- **Magic Bytes Validation**: Dosya içeriği doğrulama
- **File Size Limiting**: 5MB maksimum dosya boyutu
- **Safe File Naming**: UUID tabanlı güvenli dosya adlandırma
- **Extension Filtering**: İzin verilen dosya türleri kontrolü

#### Input Validation ve Sanitization
- **SQL Injection Koruması**: Tehlikeli karakter filtreleme
- **XSS Koruması**: HTML escape ve sanitization
- **Pydantic Validation**: Güçlü veri doğrulama şemaları
- **Email Validation**: RFC uyumlu e-posta doğrulama

#### Audit ve Loglama Sistemi
- **Security Event Logging**: Tüm güvenlik olaylarının kaydı
- **Failed Login Tracking**: Başarısız giriş denemelerinin takibi
- **API Access Logging**: Hassas endpoint erişim logları
- **User Activity Monitoring**: Kullanıcı aktivite takibi

### 🔧 Teknik Güvenlik Altyapısı

#### Yeni Güvenlik Modülleri
- **`backend/security.py`**: Ana güvenlik modülü
  - Password hashing ve validation
  - JWT token yönetimi
  - Rate limiting yapılandırması
  - Login attempt tracking
  - File upload validation
  - Input sanitization
  - Security audit logging

- **`backend/middleware.py`**: Güvenlik middleware'leri
  - SecurityMiddleware: Genel güvenlik kontrolleri
  - RequestLoggingMiddleware: İstek loglama
  - RateLimitMiddleware: Hız sınırlama
  - IPWhitelistMiddleware: IP kısıtlaması
  - ContentTypeValidationMiddleware: İçerik türü doğrulama

#### Veritabanı Güvenlik Modelleri
- **User Model Genişletildi**:
  - `is_admin`: Admin yetki kontrolü
  - `last_login`: Son giriş takibi
  - `failed_login_attempts`: Başarısız deneme sayısı
  - `locked_until`: Hesap kilitleme süresi
  - `password_changed_at`: Şifre değişiklik tarihi
  - `two_factor_enabled`: 2FA desteği
  - `created_by_ip`: Kayıt IP adresi
  - `last_login_ip`: Son giriş IP adresi

- **Yeni Güvenlik Tabloları**:
  - `APIKey`: API anahtarı yönetimi
  - `UserSession`: Oturum takibi
  - `SecurityLog`: Güvenlik olayları
  - `PasswordResetToken`: Şifre sıfırlama

#### Güvenlik Yapılandırması
- **SecurityConfig Sınıfı**: Merkezi güvenlik ayarları
- **Environment Variables**: Güvenli yapılandırma yönetimi
- **Redis Integration**: Dağıtık rate limiting ve session yönetimi

### 🛡️ API Güvenlik Endpoint'leri

#### Güvenli Authentication Endpoints
- `POST /users/register`: Rate limited kullanıcı kaydı
- `POST /users/login`: Brute force korumalı giriş
- `POST /users/refresh-token`: Token yenileme
- `POST /users/logout`: Güvenli çıkış

#### Güvenli File Upload
- `POST /upload-image/`: Güvenlik kontrollü dosya yükleme
- Magic bytes validation
- File size ve type kontrolü
- Güvenli dosya adlandırma

#### Admin Security Endpoints
- IP whitelist kontrolü
- Admin yetki doğrulama
- Audit log takibi

### 📊 Güvenlik Metrikleri

```
🔐 Authentication: JWT (30dk access, 7 gün refresh)
🛡️ Password Security: Bcrypt + Güçlü politika
⚡ Rate Limiting: Redis tabanlı, IP bazlı
🔒 Account Security: 5 deneme sonrası kilitleme
📁 File Security: Magic bytes + boyut kontrolü
🌐 CORS: Yapılandırılmış origin kontrolü
📝 Audit Logging: Tüm güvenlik olayları
🚫 Input Validation: SQL injection + XSS koruması
```

### 🔄 Güvenlik Konfigürasyonu

#### Environment Variables
- `SECRET_KEY`: JWT imzalama anahtarı
- `REDIS_HOST`: Redis sunucu adresi
- `REDIS_PORT`: Redis port numarası
- `ENVIRONMENT`: Çalışma ortamı (development/production)

#### Güvenlik Politikaları
- Minimum şifre uzunluğu: 8 karakter
- Maksimum giriş denemesi: 5
- Kilitleme süresi: 15 dakika
- Token süresi: 30 dakika (access), 7 gün (refresh)
- Maksimum dosya boyutu: 5MB

---

## [2.1.0] - 29 Eylül 2025 - Pazartesi

### 🍽️ Yeni Özellikler

#### Kapsamlı Sipariş Hazırlama Yönetimi Sistemi
- **Gelişmiş Hazırlama Yöneticisi**: Admin panelinde "🍽️ Hazırlama Yönet" butonu ile sipariş hazırlama kontrolü
- **Ürün Bazında Hazırlık Takibi**: Her ürün için ayrı hazırlık durumu yönetimi
- **Üç Durum Sistemi**: 
  - 🟢 **HAZIR**: Ürün hazırlandı
  - 🟠 **BEKLİYOR**: Ürün hazırlanıyor
  - 🔴 **HAZIRLANAMAZ**: Ürün hazırlanamıyor (stok yok, malzeme eksik vb.)
- **Detaylı Not Sistemi**: 
  - Hazırlama notları ekleme
  - Hazırlanamama nedeni belirtme
  - Validasyon kontrolü (hazırlanamaz seçilirse neden zorunlu)

#### Admin Panel Geliştirmeleri
- **Hazırlama Yöneticisi Modal'ı** (`admin_panel/main.py`):
  - 700x600px responsive modal tasarımı
  - Genel hazırlık durumu progress bar'ı
  - Scroll edilebilir ürün listesi
  - Her ürün için detaylı bilgi kartları
  - "Tümünü Hazır İşaretle" toplu işlem butonu
  - "Siparişi Hazır Olarak İşaretle" butonu (tüm ürünler hazır olduğunda aktif)

- **Ürün Hazırlama Dialog'u**:
  - Radio button ile durum seçimi (Hazır/Bekliyor/Hazırlanamaz)
  - Multi-line text field'lar (hazırlama notu ve hazırlanamama nedeni)
  - Ürün bilgileri gösterimi (ad, adet, birim fiyat, toplam)
  - Form validasyonu ve hata kontrolü

#### Müşteri Frontend Geliştirmeleri
- **Gelişmiş Sipariş Detayları** (`frontend/src/views/orders_view.py`):
  - Custom modal overlay sistemi (AlertDialog yerine)
  - 600x650px responsive modal tasarımı
  - Ürün bazında hazırlık durumu gösterimi
  - Renkli durum etiketleri (Yeşil/Turuncu/Kırmızı)
  - Hazırlama notları ve hazırlanamama nedenleri görünürlüğü
  - Hazırlık durumu özeti (Hazır/Bekliyor/Hazırlanamaz sayıları)

### 🔧 Teknik İyileştirmeler

#### Veri Yapısı Güncellemeleri
- **Sipariş Ürün Modeli Genişletildi**:
  - `preparation_status`: Boolean (ürün hazır mı?)
  - `cannot_prepare`: Boolean (ürün hazırlanamaz mı?)
  - `preparation_note`: String (hazırlama notu)
  - `cannot_prepare_reason`: String (hazırlanamama nedeni)

#### API Entegrasyonu
- **Thread-Safe İşlemler**: `page.run_thread()` ile güvenli API çağrıları
- **Error Handling**: Kapsamlı hata yönetimi ve kullanıcı geri bildirimleri
- **Debug Logging**: Detaylı konsol çıktıları ile geliştirme desteği

#### UI/UX İyileştirmeleri
- **Custom Modal Sistemi**: AlertDialog yerine overlay tabanlı modal sistemi
- **Responsive Tasarım**: Farklı ekran boyutlarına uyumlu tasarım
- **Visual Feedback**: Durum değişikliklerinde anlık görsel geri bildirim
- **Color-Coded Status**: Hazırlık durumlarına göre renk kodlaması

### 🐛 Bug Fixes

#### Veri Alanı Düzeltmeleri
- **Fiyat Alanı Sorunu**: `item['price']` yerine `item['price_per_item']` kullanımı düzeltildi
- **Ürün Bilgisi Gösterimi**: Sipariş ürünlerinde fiyat bilgilerinin doğru görüntülenmesi sağlandı
- **Modal Güvenilirliği**: Custom overlay sistemi ile modal açılma/kapanma sorunları çözüldü

### 🎯 Kullanıcı Deneyimi İyileştirmeleri

#### Admin Tarafında
- **Kolay Erişim**: Sipariş listesinden tek tıkla hazırlama yönetimine geçiş
- **Toplu İşlemler**: Tüm ürünleri tek seferde hazır işaretleme
- **Görsel Durum Takibi**: Progress bar ile genel hazırlık durumu
- **Detaylı Kontrol**: Her ürün için ayrı durum ve not yönetimi

#### Müşteri Tarafında
- **Şeffaflık**: Sipariş hazırlık durumunun detaylı görünümü
- **Bilgilendirme**: Hazırlama notları ve sorun açıklamaları
- **Görsel Takip**: Renkli etiketler ile kolay durum takibi
- **Özet Bilgi**: Genel hazırlık durumu sayısal gösterimi

### 🔄 Değişiklikler

#### Kod Organizasyonu
- **Modüler Yapı**: Hazırlama yönetimi için ayrı metodlar
- **Helper Functions**: `save_item_preparation()`, `mark_all_items_ready()`, `mark_order_ready()`
- **State Management**: Modal durumu ve form verilerinin güvenli yönetimi

#### Performans Optimizasyonları
- **Lazy Loading**: Ürün bilgilerinin ihtiyaç anında yüklenmesi
- **Efficient Rendering**: Sadece değişen bileşenlerin yeniden çizilmesi
- **Memory Management**: Modal kapatıldığında kaynakların temizlenmesi

---

## [2.0.0] - 2024-01-15

### 🎉 Yeni Özellikler

#### E-mail Doğrulama Sistemi
- **Güvenli Token Sistemi**: SHA-256 hash ile güvenli doğrulama token'ları oluşturma
- **HTML E-mail Şablonları**: Profesyonel görünümlü e-mail tasarımları (`backend/templates/email_verification.html`)
- **SMTP Entegrasyonu**: FastAPI-Mail ile e-mail gönderimi
- **Token Süresi Yönetimi**: 24 saatlik doğrulama token süresi
- **Yeniden Gönderme**: Doğrulama e-mailini yeniden gönderme özelliği
- **E-mail Doğrulama Sayfası**: Frontend'de özel doğrulama sayfası (`frontend/src/views/email_verification_view.py`)

#### Müşteri Kayıt ve Giriş Sistemi
- **Kapsamlı Kullanıcı Kaydı**: Ad, soyad, e-posta, telefon ve adres bilgileri ile kayıt
- **E-mail Doğrulama Zorunluluğu**: Kayıt sonrası e-mail doğrulama mecburiyeti
- **Güvenli Giriş Sistemi**: E-posta ve şifre ile kullanıcı girişi (sadece doğrulanmış hesaplar)
- **Şifre Güvenliği**: Bcrypt ile güçlü şifre hashleme
- **Oturum Yönetimi**: Kullanıcı giriş durumu takibi ve yönetimi

#### Frontend Geliştirmeleri
- **AuthView Sınıfı**: Giriş ve kayıt işlemleri için özel sayfa (`frontend/src/views/auth_view.py`)
- **Dinamik Header Menüsü**: Kullanıcı durumuna göre değişen navigasyon menüsü
- **Kullanıcı Profil Menüsü**: Giriş yapmış kullanıcılar için popup menü
- **Form Validasyonu**: Gerçek zamanlı form doğrulama ve hata gösterimi
- **Modern UI Tasarımı**: Kullanıcı dostu arayüz ve responsive tasarım
- **State Yönetimi**: `current_user` ile kullanıcı durumu takibi

#### Admin Panel Geliştirmeleri
- **Müşteri Yönetimi Sayfası**: Kayıtlı müşterilerin listesi ve yönetimi
- **Gerçek API Entegrasyonu**: Backend API ile canlı veri bağlantısı
- **Müşteri Tablosu**: ID, ad soyad, e-posta, telefon, kayıt tarihi ve durum bilgileri
- **Arama ve Filtreleme**: Müşteri arama ve durum filtreleme özellikleri
- **İşlem Butonları**: Müşteri detayları görüntüleme, düzenleme ve durum değiştirme

### 🔧 Backend API Geliştirmeleri

#### Yeni Endpoint'ler
- `POST /users/register` - Yeni kullanıcı kaydı
  - Parametreler: first_name, last_name, email, phone, address, password
  - Dönen veri: Kayıt durumu ve e-mail doğrulama bilgisi
- `POST /users/login` - Kullanıcı girişi
  - Parametreler: email, password
  - Dönen veri: Giriş durumu ve kullanıcı bilgileri (sadece doğrulanmış hesaplar)
- `POST /users/verify-email` - E-mail doğrulama
  - Parametreler: token
  - Dönen veri: Doğrulama durumu
- `POST /users/resend-verification` - Doğrulama e-mailini yeniden gönder
  - Parametreler: email
  - Dönen veri: Gönderim durumu
- `GET /users/` - Kullanıcı listesi (Admin için)
  - Parametreler: skip (varsayılan: 0), limit (varsayılan: 100)
  - Dönen veri: Kullanıcı listesi

#### Veri Modeli Güncellemeleri
- **User Modeli Genişletildi** (`backend/models.py`):
  - `phone` alanı eklendi (String, nullable)
  - `address` alanı eklendi (Text, nullable)
  - `password_hash` alanı eklendi (String, not null)
  - `created_at` alanı eklendi (DateTime, varsayılan: şu an)
  - `is_active` alanı eklendi (Boolean, varsayılan: True)
  - `is_verified` alanı eklendi (Boolean, varsayılan: False)
  - `verification_token` alanı eklendi (String, nullable)
  - `verification_token_expires` alanı eklendi (DateTime, nullable)

#### Şema Güncellemeleri
- **UserCreate Şeması** (`backend/schemas.py`):
  - `first_name`, `last_name`, `phone`, `address`, `password` alanları eklendi
- **User Şeması**: Telefon, adres ve doğrulama alanları eklendi
- **UserLogin Şeması**: Giriş için e-posta ve şifre
- **UserLoginResponse Şeması**: Giriş yanıtı için özel şema
- **EmailVerificationResponse Şeması**: E-mail doğrulama yanıtı
- **ResendVerificationResponse Şeması**: Yeniden gönderme yanıtı

#### Yeni Servisler
- **EmailService Sınıfı** (`backend/email_service.py`):
  - Token oluşturma ve doğrulama
  - HTML e-mail şablonu işleme
  - SMTP e-mail gönderimi
  - Token süresi yönetimi

### 🔄 Değişiklikler

#### Rota Yönetimi
- **Frontend App** (`frontend/src/app.py`):
  - `/auth` rotası eklendi
  - `current_user` state yönetimi eklendi
  - Rota geçişlerinde kullanıcı durumu kontrolü

#### UI/UX İyileştirmeleri
- **Ana Sayfa Header** (`frontend/src/views/main_view.py`):
  - Kullanıcı durumuna göre dinamik menü
  - Giriş yapmış kullanıcılar için profil menüsü
  - Çıkış yapma özelliği

### 🛠️ Teknik İyileştirmeler

#### Güvenlik
- Şifre hashleme sistemi (basit hash - geliştirme aşaması için)
- Form validasyonu ve güvenli veri işleme
- API endpoint'lerinde veri doğrulama

#### Kod Organizasyonu
- Sınıf tabanlı yapı korundu ve genişletildi
- Modüler tasarım ile yeniden kullanılabilir bileşenler
- Hata yönetimi ve kullanıcı geri bildirimleri

#### Performans
- Veritabanı sorguları optimize edildi
- Frontend'de state yönetimi iyileştirildi
- API yanıt süreleri optimize edildi

### 🔒 Geriye Uyumluluk
- Eski `POST /users/` endpoint'i korundu
- Mevcut veri yapıları genişletildi, değiştirilmedi
- Eski frontend rotaları çalışmaya devam ediyor

### 📝 Dokümantasyon
- README.md dosyası güncellendi
- API endpoint'leri dokümante edildi
- Yeni özellikler detaylandırıldı

---

## [1.0.0] - 2024-01-01

### 🎉 İlk Sürüm

#### Temel Özellikler
- **Ürün Yönetimi**: Ürün ekleme, düzenleme, silme ve listeleme
- **Sipariş Sistemi**: Sepet yönetimi ve sipariş oluşturma
- **Admin Paneli**: Ürün ve sipariş yönetimi için arayüz
- **Resim Yükleme**: Ürün resimleri için dosya yükleme
- **WebSocket**: Gerçek zamanlı güncellemeler

#### Teknoloji Yığını
- Backend: FastAPI, SQLAlchemy, Pydantic
- Frontend: Flet (Flutter for Python)
- Veritabanı: SQLite
- HTTP İstemcisi: Requests

#### API Endpoints
- Ürün CRUD işlemleri
- Sipariş oluşturma ve listeleme
- Resim yükleme
- WebSocket bağlantısı

---

## Gelecek Sürümler İçin Planlar

### v2.1.0 (Planlanan)
- JWT token tabanlı authentication
- E-posta doğrulama sistemi
- Kullanıcı profil düzenleme
- Şifre sıfırlama özelliği

### v2.2.0 (Planlanan)
- Gelişmiş admin paneli özellikleri
- Müşteri istatistikleri ve raporları
- Toplu müşteri işlemleri
- E-posta bildirimleri

### v3.0.0 (Planlanan)
- Çok dilli destek
- Tema sistemi
- Mobil uygulama desteği
- Gelişmiş güvenlik özellikleri