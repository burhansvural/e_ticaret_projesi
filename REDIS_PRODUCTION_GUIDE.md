# 🔴 Redis ile Production-Ready Kayıt Sistemi

## 📋 İçindekiler
1. [Genel Bakış](#genel-bakış)
2. [Neden Redis?](#neden-redis)
3. [Kurulum](#kurulum)
4. [Yapılandırma](#yapılandırma)
5. [Kullanım](#kullanım)
6. [Test](#test)
7. [Production Deployment](#production-deployment)
8. [Monitoring ve Troubleshooting](#monitoring-ve-troubleshooting)
9. [Güvenlik](#güvenlik)
10. [Performans Optimizasyonu](#performans-optimizasyonu)

---

## 🎯 Genel Bakış

Bu sistem, kullanıcı kayıtlarını **doğrulama kodu girilene kadar** Redis'te geçici olarak saklar. Veritabanına kayıt **sadece** email doğrulaması tamamlandıktan sonra yapılır.

### Önceki Sistem (In-Memory)
```
❌ Sunucu yeniden başlatılınca pending registrations kaybolur
❌ Multi-instance deployment'ta çalışmaz
❌ Cluster ortamında senkronizasyon sorunu
```

### Yeni Sistem (Redis)
```
✅ Sunucu yeniden başlatılsa bile pending registrations korunur
✅ Multi-instance deployment'ta sorunsuz çalışır
✅ Cluster ortamında merkezi veri deposu
✅ Otomatik TTL (Time To Live) ile expired kayıtlar temizlenir
✅ Production-ready ve scalable
```

---

## 🤔 Neden Redis?

### 1. **Persistence (Kalıcılık)**
- Sunucu yeniden başlatılsa bile veriler kaybolmaz
- AOF (Append Only File) ile veri güvenliği

### 2. **Performance (Performans)**
- In-memory veri deposu (çok hızlı)
- O(1) kompleksitede okuma/yazma

### 3. **TTL (Time To Live)**
- Otomatik süre dolumu
- Manuel cleanup'a gerek yok

### 4. **Scalability (Ölçeklenebilirlik)**
- Horizontal scaling desteği
- Redis Cluster ile dağıtık mimari

### 5. **High Availability**
- Redis Sentinel ile otomatik failover
- Master-Slave replication

---

## 🔧 Kurulum

### Otomatik Kurulum (Önerilen)

```bash
# Redis'i otomatik kur ve başlat
./setup_redis.sh
```

### Manuel Kurulum

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Linux (CentOS/RHEL)
```bash
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Docker (Production)
```bash
docker-compose up -d redis
```

### Kurulum Doğrulama
```bash
redis-cli ping
# Beklenen çıktı: PONG
```

---

## ⚙️ Yapılandırma

### 1. Environment Variables

`.env` dosyası oluşturun:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Redis with Password (Production)
# REDIS_URL=redis://:your-password@localhost:6379/0

# Redis Cluster (Production)
# REDIS_URL=redis://redis-cluster:6379/0
```

### 2. Redis Yapılandırması

#### Development (Varsayılan)
```bash
# /etc/redis/redis.conf
bind 127.0.0.1
port 6379
daemonize yes
```

#### Production (Önerilen)
```bash
# /etc/redis/redis.conf

# Güvenlik
bind 0.0.0.0
requirepass your-strong-password-here
protected-mode yes

# Persistence
appendonly yes
appendfsync everysec

# Memory
maxmemory 256mb
maxmemory-policy allkeys-lru

# Performance
tcp-backlog 511
timeout 300
```

### 3. Uygulama Yapılandırması

`backend/pending_registrations_redis.py` otomatik olarak şu sırayla yapılandırılır:

1. `.env` dosyasından `REDIS_URL` okur
2. Bulamazsa `redis://localhost:6379/0` kullanır
3. Redis'e bağlanamazsa **fallback** olarak in-memory manager kullanır

---

## 🚀 Kullanım

### Backend'i Başlatma

```bash
# Redis'in çalıştığından emin olun
redis-cli ping

# Backend'i başlatın
uvicorn backend.main:app --reload
```

### API Endpoints

#### 1. Kayıt Başlatma
```bash
POST /users/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "5551234567"
}

# Response: 6 haneli kod email'e gönderilir
# Kullanıcı Redis'te saklanır (veritabanında DEĞİL)
```

#### 2. Email Doğrulama
```bash
POST /users/verify-email
{
  "email": "user@example.com",
  "code": "123456"
}

# Response: Kod doğrulanır
# Kullanıcı Redis'ten silinir
# Kullanıcı VERİTABANINA kaydedilir
```

#### 3. Kod Yeniden Gönderme
```bash
POST /resend-verification?email=user@example.com

# Response: Yeni kod oluşturulur ve email'e gönderilir
# Redis'te TTL sıfırlanır (24 saat daha)
```

#### 4. Health Check
```bash
GET /health

# Response:
{
  "status": "healthy",
  "version": "2.2.0",
  "redis": {
    "status": "healthy",
    "connected_clients": 2,
    "used_memory_human": "1.2M",
    "uptime_in_seconds": 3600
  },
  "pending_registrations": {
    "total": 5,
    "redis_connected": true
  }
}
```

---

## 🧪 Test

### 1. Redis Bağlantı Testi

```bash
python3 test_redis_connection.py
```

**Test Edilen Özellikler:**
- ✅ Redis sağlık kontrolü
- ✅ Pending registrations istatistikleri
- ✅ Kayıt oluşturma
- ✅ Kayıt okuma
- ✅ Kod güncelleme
- ✅ Kod doğrulama ve silme
- ✅ Expired kayıtları temizleme

### 2. Pending Registrations Görüntüleme

```bash
python3 test_new_registration_flow.py
```

### 3. Manuel Redis Testi

```bash
# Redis CLI'ye bağlan
redis-cli

# Tüm pending registration key'lerini listele
127.0.0.1:6379> KEYS pending_registration:*

# Belirli bir kaydı görüntüle
127.0.0.1:6379> GET pending_registration:user@example.com

# TTL kontrolü (saniye cinsinden kalan süre)
127.0.0.1:6379> TTL pending_registration:user@example.com

# Tüm pending registrations'ı sil (DİKKAT!)
127.0.0.1:6379> FLUSHDB
```

---

## 🌐 Production Deployment

### 1. Docker ile Deployment

```bash
# Redis'i başlat
docker-compose up -d redis

# Redis durumunu kontrol et
docker-compose ps
docker logs eticaret_redis

# Backend'i başlat (opsiyonel)
docker-compose up -d backend
```

### 2. Systemd Service (Linux)

`/etc/systemd/system/eticaret-backend.service`:

```ini
[Unit]
Description=E-Ticaret Backend API
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/eticaret
Environment="REDIS_URL=redis://localhost:6379/0"
ExecStart=/usr/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable eticaret-backend
sudo systemctl start eticaret-backend
```

### 3. Nginx Reverse Proxy

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4. Environment Variables (Production)

```bash
# .env (Production)
REDIS_URL=redis://:strong-password@redis-server:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5
REDIS_SOCKET_CONNECT_TIMEOUT=5
```

---

## 📊 Monitoring ve Troubleshooting

### 1. Redis Monitoring

```bash
# Redis bilgilerini görüntüle
redis-cli INFO

# Gerçek zamanlı monitoring
redis-cli --stat

# Slow query log
redis-cli SLOWLOG GET 10

# Memory kullanımı
redis-cli INFO memory
```

### 2. Application Monitoring

```bash
# Health check
curl http://localhost:8000/health

# Pending registrations sayısı
curl http://localhost:8000/health | jq '.pending_registrations.total'

# Redis durumu
curl http://localhost:8000/health | jq '.redis.status'
```

### 3. Logging

Backend logları:

```python
# backend/main.py
logger.info("✅ Pending registration eklendi: user@example.com")
logger.warning("⚠️ Geçersiz doğrulama kodu: user@example.com")
logger.error("❌ Redis bağlantı hatası: Connection refused")
```

### 4. Common Issues

#### Redis'e Bağlanılamıyor

```bash
# Redis çalışıyor mu?
redis-cli ping

# Port dinleniyor mu?
netstat -tulpn | grep 6379

# Firewall kontrolü
sudo ufw status
sudo ufw allow 6379/tcp
```

#### Fallback Mode Aktif

```
⚠️ Redis başlatılamadı: Connection refused
⚠️ Fallback olarak in-memory manager kullanılacak
```

**Çözüm:**
```bash
# Redis'i başlat
sudo systemctl start redis-server

# Backend'i yeniden başlat
sudo systemctl restart eticaret-backend
```

#### Memory Doldu

```bash
# Memory kullanımını kontrol et
redis-cli INFO memory

# Expired key'leri temizle
redis-cli --scan --pattern "pending_registration:*" | xargs redis-cli DEL

# Maxmemory ayarla
redis-cli CONFIG SET maxmemory 512mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## 🔒 Güvenlik

### 1. Redis Güvenliği

```bash
# /etc/redis/redis.conf

# Şifre koru
requirepass your-very-strong-password-here

# Sadece localhost'tan bağlantı (development)
bind 127.0.0.1

# Tüm IP'lerden bağlantı (production - dikkatli kullanın)
bind 0.0.0.0
protected-mode yes

# Tehlikeli komutları devre dışı bırak
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

### 2. Network Güvenliği

```bash
# Firewall kuralları
sudo ufw allow from 10.0.0.0/8 to any port 6379
sudo ufw deny 6379/tcp
```

### 3. SSL/TLS (Production)

```bash
# Redis 6+ ile SSL
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

```python
# Python client
REDIS_URL = "rediss://:password@redis-server:6380/0"  # rediss:// (SSL)
```

---

## ⚡ Performans Optimizasyonu

### 1. Connection Pooling

```python
# backend/pending_registrations_redis.py
redis_client = redis.from_url(
    redis_url,
    max_connections=50,  # Connection pool size
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)
```

### 2. Redis Yapılandırması

```bash
# /etc/redis/redis.conf

# TCP backlog
tcp-backlog 511

# Timeout
timeout 300

# TCP keepalive
tcp-keepalive 300

# Max clients
maxclients 10000
```

### 3. Monitoring Metrikleri

```bash
# Throughput
redis-cli INFO stats | grep instantaneous_ops_per_sec

# Latency
redis-cli --latency

# Memory fragmentation
redis-cli INFO memory | grep mem_fragmentation_ratio
```

---

## 📈 Scalability

### 1. Redis Cluster

```bash
# 3 master, 3 slave cluster
redis-cli --cluster create \
  192.168.1.1:6379 192.168.1.2:6379 192.168.1.3:6379 \
  192.168.1.4:6379 192.168.1.5:6379 192.168.1.6:6379 \
  --cluster-replicas 1
```

### 2. Redis Sentinel (High Availability)

```bash
# sentinel.conf
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 10000
```

### 3. Load Balancing

```nginx
upstream redis_backend {
    server redis1:6379 max_fails=3 fail_timeout=30s;
    server redis2:6379 max_fails=3 fail_timeout=30s;
    server redis3:6379 max_fails=3 fail_timeout=30s;
}
```

---

## 📚 Kaynaklar

- [Redis Documentation](https://redis.io/documentation)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Redis Best Practices](https://redis.io/topics/best-practices)
- [Redis Security](https://redis.io/topics/security)

---

## 🎉 Özet

✅ **Redis kuruldu ve yapılandırıldı**  
✅ **Production-ready pending registration sistemi**  
✅ **Otomatik TTL ve cleanup**  
✅ **Health check ve monitoring**  
✅ **Fallback mekanizması**  
✅ **Docker desteği**  
✅ **Güvenlik ve performans optimizasyonları**

**Versiyon:** 2.2.0  
**Tarih:** 30 Ocak 2025  
**Durum:** ✅ PRODUCTION READY