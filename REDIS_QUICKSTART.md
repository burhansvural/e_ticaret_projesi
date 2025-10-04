# 🚀 Redis Quick Start Guide

## 5 Dakikada Redis ile Başlayın!

---

## 📋 Gereksinimler

- Python 3.8+
- Redis 5.0+ (otomatik kurulacak)
- Linux/macOS/Windows (WSL)

---

## ⚡ Hızlı Kurulum

### 1. Redis'i Kur ve Başlat (30 saniye)

```bash
# Otomatik kurulum ve başlatma
./setup_redis.sh
```

**Beklenen Çıktı:**
```
✅ Redis zaten kurulu
🚀 Redis başlatılıyor...
✅ Redis çalışıyor ve erişilebilir!
🎉 Kurulum başarıyla tamamlandı!
```

---

### 2. Bağlantıyı Test Et (10 saniye)

```bash
# Redis bağlantısını test et
python3 test_redis_connection.py
```

**Beklenen Çıktı:**
```
🔴 REDIS BAĞLANTI VE FONKSİYON TESTİ
======================================================================
1️⃣ Redis Sağlık Kontrolü
----------------------------------------------------------------------
✅ Redis SAĞLIKLI
   📊 Bağlı Client Sayısı: 1
   💾 Kullanılan Bellek: 1.2M
   ⏱️  Uptime: 120 saniye

...

🎉 TÜM TESTLER TAMAMLANDI!
```

---

### 3. Backend'i Başlat (10 saniye)

```bash
# Backend'i başlat
uvicorn backend.main:app --reload
```

**Beklenen Çıktı:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     ✅ Redis bağlantısı başarılı
```

---

### 4. Health Check (5 saniye)

```bash
# Sistem durumunu kontrol et
curl http://localhost:8000/health | jq
```

**Beklenen Çıktı:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-30T12:00:00",
  "version": "2.2.1",
  "redis": {
    "status": "healthy",
    "connected_clients": 2,
    "used_memory_human": "1.2M",
    "uptime_in_seconds": 3600
  },
  "pending_registrations": {
    "total": 0,
    "redis_connected": true
  }
}
```

---

## 🎯 Kullanım Örnekleri

### Örnek 1: Kullanıcı Kaydı

```bash
# 1. Kayıt başlat
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "phone": "5551234567"
  }'

# Response: Email gönderildi, Redis'te saklandı
```

### Örnek 2: Pending Registrations Görüntüle

```bash
# Bekleyen kayıtları görüntüle
python3 test_new_registration_flow.py
```

**Çıktı:**
```
📋 BEKLEYEN KAYITLAR TEST
============================================================
📊 Toplam bekleyen kayıt: 1

📧 Bekleyen email adresleri:

  Email: test@example.com
  Ad Soyad: Test User
  Doğrulama Kodu: 123456
  Oluşturulma: 2025-01-30 12:00:00
  Son Geçerlilik: 2025-01-31 12:00:00
  Süresi Doldu mu: ✅ Hayır
```

### Örnek 3: Email Doğrulama

```bash
# 2. Email'i doğrula
curl -X POST http://localhost:8000/users/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456"
  }'

# Response: Kullanıcı veritabanına kaydedildi
```

---

## 🔧 Yapılandırma (Opsiyonel)

### Environment Variables

```bash
# .env dosyası oluştur
cat > .env << EOF
REDIS_URL=redis://localhost:6379/0
EOF
```

### Redis Password (Production)

```bash
# Redis'e password ekle
redis-cli CONFIG SET requirepass "your-strong-password"

# .env dosyasını güncelle
echo "REDIS_URL=redis://:your-strong-password@localhost:6379/0" > .env
```

---

## 🐳 Docker ile Kullanım (Alternatif)

```bash
# Redis'i Docker ile başlat
docker-compose up -d redis

# Durumu kontrol et
docker-compose ps

# Logları görüntüle
docker logs eticaret_redis

# Durdur
docker-compose down
```

---

## 🧪 Test Komutları

```bash
# Redis bağlantı testi
python3 test_redis_connection.py

# Pending registrations görüntüle
python3 test_new_registration_flow.py

# Health check
curl http://localhost:8000/health

# Redis CLI
redis-cli ping
redis-cli INFO
redis-cli KEYS "pending_registration:*"
```

---

## 🔍 Troubleshooting

### Redis Çalışmıyor

```bash
# Redis durumunu kontrol et
redis-cli ping

# Çalışmıyorsa başlat
# Linux
sudo systemctl start redis-server

# macOS
brew services start redis

# Docker
docker-compose up -d redis
```

### Backend Redis'e Bağlanamıyor

```bash
# Redis'in çalıştığından emin ol
redis-cli ping

# Port kontrolü
netstat -tulpn | grep 6379

# .env dosyasını kontrol et
cat .env | grep REDIS_URL
```

### Fallback Mode Aktif

```
⚠️ Redis başlatılamadı: Connection refused
⚠️ Fallback olarak in-memory manager kullanılacak
```

**Çözüm:** Redis'i başlatın ve backend'i yeniden başlatın.

---

## 📚 Daha Fazla Bilgi

- **Detaylı Rehber:** `REDIS_PRODUCTION_GUIDE.md`
- **Migration Özeti:** `REDIS_MIGRATION_SUMMARY.md`
- **Kayıt Sistemi:** `YENİ_KAYIT_SİSTEMİ.md`

---

## ✅ Checklist

- [ ] Redis kuruldu (`./setup_redis.sh`)
- [ ] Redis çalışıyor (`redis-cli ping`)
- [ ] Test başarılı (`python3 test_redis_connection.py`)
- [ ] Backend başlatıldı (`uvicorn backend.main:app --reload`)
- [ ] Health check OK (`curl http://localhost:8000/health`)

---

## 🎉 Tamamlandı!

Redis ile production-ready kayıt sisteminiz hazır!

**Sonraki Adımlar:**
1. Frontend'i başlatın: `python3 frontend/main.py`
2. Kayıt akışını test edin
3. Production deployment için `REDIS_PRODUCTION_GUIDE.md` okuyun

---

**Versiyon:** 2.2.1  
**Tarih:** 30 Ocak 2025  
**Süre:** ~5 dakika  
**Durum:** ✅ HAZIR