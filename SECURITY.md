# 🔒 E-Ticaret Backend Güvenlik Dokümantasyonu

## Güvenlik Özellikleri

### 1. **Kimlik Doğrulama ve Yetkilendirme**

#### JWT Token Sistemi
- **Access Token**: 30 dakika geçerlilik süresi
- **Refresh Token**: 7 gün geçerlilik süresi
- **HS256 algoritması** ile imzalanmış
- **Otomatik token yenileme** desteği

#### Şifre Güvenliği
- **Bcrypt hashleme** (cost factor: 12)
- **Minimum 8 karakter** gereksinimi
- **Büyük/küçük harf, rakam ve özel karakter** zorunluluğu
- **Şifre gücü analizi** ve geri bildirim

#### Hesap Güvenliği
- **5 başarısız girişten sonra hesap kilitleme**
- **15 dakika kilitleme süresi**
- **E-posta doğrulama** zorunluluğu
- **Şifre sıfırlama** token sistemi (1 saat geçerli)

### 2. **Rate Limiting ve DDoS Koruması**

#### API Rate Limits
- **Genel**: 1000 istek/saat
- **Login**: 10 istek/dakika
- **Kayıt**: 5 istek/dakika
- **Şifre sıfırlama**: 3 istek/saat
- **Dosya yükleme**: 10 istek/dakika

#### Redis Tabanlı Tracking
- **IP bazlı takip**
- **Kullanıcı bazlı takip**
- **Otomatik temizleme**

### 3. **Dosya Güvenliği**

#### Upload Güvenliği
- **Maksimum dosya boyutu**: 5MB
- **İzin verilen formatlar**: JPG, PNG, GIF, WebP
- **Magic byte kontrolü**
- **Güvenli dosya adlandırma** (UUID)
- **Dosya içeriği tarama**

#### Statik Dosya Güvenliği
- **Güvenli dizin yapısı**
- **Direct access koruması**
- **Content-Type doğrulama**

### 4. **Input Validation ve Sanitization**

#### Veri Doğrulama
- **Pydantic şemaları** ile tip kontrolü
- **Regex pattern** doğrulama
- **Uzunluk sınırları**
- **SQL injection** koruması
- **XSS koruması**

#### Sanitization
- **HTML escape**
- **Tehlikeli karakter temizleme**
- **Whitespace normalizasyonu**

### 5. **Güvenlik Headers**

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 6. **CORS Yapılandırması**

#### İzin Verilen Origins
- `http://localhost:3000`
- `http://127.0.0.1:3000`

#### İzin Verilen Methods
- GET, POST, PUT, DELETE, OPTIONS

#### İzin Verilen Headers
- Authorization, Content-Type, X-API-Key

### 7. **Audit Logging**

#### Güvenlik Olayları
- **Başarılı/başarısız girişler**
- **Şifre değişiklikleri**
- **Hesap kilitlemeleri**
- **Admin işlemleri**
- **Dosya yüklemeleri**
- **Şüpheli aktiviteler**

#### Log Formatı
```json
{
  "timestamp": "2025-01-XX",
  "event_type": "login_failed",
  "user_id": 123,
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "details": {"reason": "wrong_password"}
}
```

### 8. **Admin Güvenliği**

#### IP Whitelist
- **Admin endpoint'leri** için IP kısıtlaması
- **Yapılandırılabilir whitelist**
- **Otomatik engelleme**

#### Admin Yetkileri
- **Kullanıcı yönetimi**
- **Güvenlik log görüntüleme**
- **Sistem durumu kontrolü**

### 9. **Middleware Güvenliği**

#### Security Middleware
- **Request boyutu kontrolü** (10MB limit)
- **Şüpheli User-Agent** tespiti
- **İşlem süresi** takibi
- **Otomatik güvenlik header** ekleme

#### Request Logging
- **Hassas endpoint** takibi
- **Hata durumu** loglama
- **Performance monitoring**

### 10. **Environment Güvenliği**

#### Production Ayarları
- **Debug mode** kapatılması
- **API dokümantasyonu** gizlenmesi
- **Güvenli secret key** kullanımı
- **HTTPS zorunluluğu**

#### Secrets Management
- **Environment variables** kullanımı
- **Secret rotation** desteği
- **Encrypted storage**

## Güvenlik Endpoint'leri

### Kimlik Doğrulama
```http
POST /users/register          # Kullanıcı kaydı
POST /users/login             # Giriş
POST /auth/logout             # Çıkış
GET  /auth/me                 # Kullanıcı bilgileri
```

### Şifre Yönetimi
```http
POST /auth/change-password         # Şifre değiştirme
POST /auth/request-password-reset  # Şifre sıfırlama isteği
POST /auth/reset-password          # Şifre sıfırlama
```

### Admin Endpoint'leri
```http
GET  /admin/security-logs          # Güvenlik logları
GET  /admin/users                  # Kullanıcı listesi
PUT  /admin/users/{id}/toggle-active  # Kullanıcı aktiflik
```

### Sistem
```http
GET  /health                       # Sistem durumu
```

## Güvenlik Kontrol Listesi

### Deployment Öncesi
- [ ] Secret key'ler değiştirildi
- [ ] Debug mode kapatıldı
- [ ] HTTPS yapılandırıldı
- [ ] Firewall kuralları ayarlandı
- [ ] Database güvenliği sağlandı
- [ ] Backup sistemi kuruldu
- [ ] Monitoring aktif
- [ ] Log rotation ayarlandı

### Düzenli Kontroller
- [ ] Güvenlik logları incelendi
- [ ] Başarısız giriş denemeleri kontrol edildi
- [ ] Sistem performansı izlendi
- [ ] Güvenlik güncellemeleri yapıldı
- [ ] Backup'lar test edildi

## Güvenlik İhlali Durumunda

### Acil Müdahale
1. **Sistemi izole et**
2. **Logları koru**
3. **Etkilenen kullanıcıları bilgilendir**
4. **Şifreleri sıfırla**
5. **Güvenlik açığını kapat**
6. **Forensik analiz yap**

### İletişim
- **Güvenlik ekibi**: security@company.com
- **Acil durum**: +90 XXX XXX XXXX

## Güvenlik Güncellemeleri

### v2.0.0 (2025-01-XX)
- JWT token sistemi eklendi
- Rate limiting implementasyonu
- Güvenlik middleware'leri
- Audit logging sistemi
- Dosya upload güvenliği
- Admin güvenlik özellikleri

---

**Not**: Bu dokümantasyon düzenli olarak güncellenmektedir. Son güncelleme: 2025-01-XX