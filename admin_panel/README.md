# E-Ticaret Admin Panel

Profesyonel modüler yapıda geliştirilmiş admin panel uygulaması.

## 📁 Proje Yapısı

```
admin_panel/
├── main.py                 # Ana giriş noktası
├── config.py              # Merkezi konfigürasyon
│
├── core/                  # Ana uygulama mantığı
│   ├── __init__.py
│   └── app.py            # AdminPanel ana sınıfı
│
├── services/             # İş mantığı katmanı
│   ├── __init__.py
│   ├── api_service.py   # API iletişim servisi
│   └── auth_service.py  # Kimlik doğrulama servisi
│
├── views/               # UI sunum katmanı
│   ├── __init__.py
│   ├── auth_view.py    # Giriş/Kayıt/Doğrulama ekranları
│   ├── dashboard_view.py    # Dashboard görünümü
│   ├── products_view.py     # Ürün yönetimi
│   ├── orders_view.py       # Sipariş yönetimi
│   ├── customers_view.py    # Müşteri listesi
│   └── categories_view.py   # Kategori yönetimi
│
├── components/          # Yeniden kullanılabilir UI bileşenleri
│   ├── __init__.py
│   ├── sidebar.py      # Navigasyon sidebar
│   ├── modals.py       # Modal dialog yöneticisi
│   └── notifications.py # Bildirim sistemi
│
└── utils/              # Yardımcı fonksiyonlar
    ├── __init__.py
    └── helpers.py      # Genel yardımcı fonksiyonlar
```

## 🚀 Çalıştırma

```bash
cd /home/burhan/Genel/Ogrenci_Python/e_ticaret_projesi/admin_panel
python3 main.py
```

## 🏗️ Mimari Prensipler

### 1. **Separation of Concerns (Endişelerin Ayrılması)**
- Her modül tek bir sorumluluğa sahip
- UI, iş mantığı ve veri katmanları ayrı

### 2. **Service Layer Pattern**
- API iletişimi `APIService` üzerinden
- Kimlik doğrulama `AuthService` üzerinden
- Test edilebilir ve bakımı kolay

### 3. **Component-Based UI**
- Sidebar, Modal, Notification gibi bileşenler yeniden kullanılabilir
- Her view bağımsız olarak geliştirilebilir

### 4. **Dependency Injection**
- View'lar servisleri constructor'dan alır
- Loose coupling (gevşek bağlılık)
- Test edilebilirlik artar

### 5. **Configuration Management**
- Tüm sabitler `config.py`'de merkezi
- Kolay değiştirilebilir
- Environment-specific ayarlar

## 📦 Modüller

### Core (`core/`)
Ana uygulama sınıfı ve orchestration mantığı.

**app.py**: 
- Tüm view'ları ve servisleri yönetir
- Navigasyon kontrolü
- Kimlik doğrulama akışı

### Services (`services/`)
Backend ile iletişim ve iş mantığı.

**api_service.py**:
- HTTP istekleri
- Token yönetimi
- Error handling
- Ürün, sipariş, müşteri, kategori CRUD işlemleri

**auth_service.py**:
- Kayıt (register)
- Giriş (login)
- E-posta doğrulama
- Admin parametresi yönetimi

### Views (`views/`)
Kullanıcı arayüzü ekranları.

**auth_view.py**: Login, Register, Email Verification
**dashboard_view.py**: İstatistikler ve genel bakış
**products_view.py**: Ürün listesi ve CRUD
**orders_view.py**: Sipariş listesi ve durum yönetimi
**customers_view.py**: Müşteri listesi
**categories_view.py**: Kategori yönetimi

### Components (`components/`)
Yeniden kullanılabilir UI bileşenleri.

**sidebar.py**: Navigasyon menüsü
**modals.py**: Dialog ve onay pencereleri
**notifications.py**: Başarı/hata/bilgi mesajları

### Utils (`utils/`)
Yardımcı fonksiyonlar.

**helpers.py**:
- `format_currency()`: Para formatı
- `format_date()`: Tarih formatı
- `validate_email()`: E-posta validasyonu
- `validate_phone()`: Telefon validasyonu
- `get_status_color()`: Durum renkleri
- `get_status_text()`: Durum metinleri

## 🔧 Konfigürasyon

`config.py` dosyasında tüm ayarlar:

```python
API_BASE_URL = "http://127.0.0.1:8000"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
ITEMS_PER_PAGE = 10
```

## 🔐 Kimlik Doğrulama

Admin panel, backend'e `is_admin=True` parametresi ile istek gönderir:
- Kayıt: `/users/register` (is_admin=True)
- Giriş: `/users/login` (is_admin=True)
- Doğrulama: `/users/verify-email` (is_admin=True)

## 📝 Geliştirme Notları

### Yeni View Ekleme

1. `views/` altında yeni view dosyası oluştur
2. `BaseView` pattern'ini takip et
3. `views/__init__.py`'ye ekle
4. `core/app.py`'de initialize et
5. `navigate_to()` metoduna ekle

### Yeni API Endpoint Ekleme

1. `services/api_service.py`'ye yeni metod ekle
2. Error handling ekle
3. View'dan çağır

### Yeni Component Ekleme

1. `components/` altında yeni dosya oluştur
2. `build()` metodu ile UI döndür
3. `components/__init__.py`'ye ekle

## 🐛 Hata Ayıklama

Tüm hata mesajları `NotificationManager` üzerinden gösterilir:
- `show_success()`: Başarılı işlemler
- `show_error()`: Hatalar
- `show_info()`: Bilgilendirme
- `show_warning()`: Uyarılar

## 📚 Eski Dosyalar

- `main_old_backup.py`: Orijinal monolitik dosya (yedek)
- `main_old.py`: Önceki yedek
- `main2.py`: Test dosyası

Bu dosyalar silinebilir veya referans için saklanabilir.

## ✅ Avantajlar

1. **Bakım Kolaylığı**: Her modül bağımsız
2. **Test Edilebilirlik**: Servisler ve view'lar ayrı test edilebilir
3. **Ölçeklenebilirlik**: Yeni özellikler kolayca eklenebilir
4. **Okunabilirlik**: Kod organizasyonu net
5. **Yeniden Kullanılabilirlik**: Componentler başka projelerde kullanılabilir
6. **Takım Çalışması**: Farklı geliştiriciler farklı modüllerde çalışabilir

## 🔄 Gelecek Geliştirmeler

- [ ] Unit testler ekle
- [ ] Logging sistemi
- [ ] Cache mekanizması
- [ ] Offline mode desteği
- [ ] Export/Import özellikleri
- [ ] Gelişmiş filtreleme
- [ ] Bulk operations
- [ ] Activity log