# Stok Yönetimi Sistemi - Dokümantasyon

## 📋 Genel Bakış

E-ticaret admin paneline tam kapsamlı bir stok yönetimi sistemi eklenmiştir. Bu sistem şunları içerir:

- **Stok Hareketleri Takibi** (Giriş/Çıkış)
- **Düşük Stok Uyarıları**
- **Manuel Stok Girişi/Çıkışı**
- **Tedarikçi Yönetimi**
- **Alış Fatura/İrsaliye İşlemleri**

## 🗂️ Dosya Yapısı

### Yeni Eklenen Dosyalar

```
admin_panel/
├── views/
│   ├── stock_views.py          # Stok yönetimi view'ları
│   └── supplier_views.py       # Tedarikçi ve fatura yönetimi view'ları
└── services/
    └── api_service.py          # Güncellenmiş API metodları
```

### Güncellenen Dosyalar

```
admin_panel/
├── views/
│   └── __init__.py             # Yeni view'lar export edildi
├── components/
│   └── sidebar.py              # Yeni menü öğeleri eklendi
└── core/
    └── app.py                  # Yeni view'lar import ve initialize edildi
```

## 🎯 Özellikler

### 1. Stok Hareketleri (StockMovementsView)

**Menü:** Stok Yönetimi → Stok Hareketleri

**Özellikler:**
- Tüm stok giriş/çıkış hareketlerini listeler
- Ürüne göre filtreleme
- Hareket tipine göre filtreleme (Giriş/Çıkış)
- Tarih bazlı filtreleme
- İstatistikler (Toplam Giriş, Toplam Çıkış, Net Değişim)

**API Endpoint:** `GET /stock/movements/`

### 2. Düşük Stok Uyarıları (LowStockAlertsView)

**Menü:** Stok Yönetimi → Düşük Stok Uyarıları

**Özellikler:**
- Belirlenen eşiğin altındaki ürünleri listeler
- Minimum stok seviyesi ayarlanabilir
- Hızlı stok ekleme butonu
- Renk kodlu durum göstergeleri (Tükendi/Düşük)

**API Endpoint:** `GET /stock/low-stock/?threshold={threshold}`

### 3. Manuel Stok Girişi (ManualStockEntryView)

**Menü:** Stok Yönetimi → Stok Girişi

**Özellikler:**
- Ürün seçimi (dropdown)
- Miktar girişi
- Açıklama alanı
- Referans no (Fatura/İrsaliye no)
- Form validasyonu
- Otomatik stok güncelleme

**API Endpoint:** `POST /stock/movements/`

**Veri Formatı:**
```json
{
  "product_id": 1,
  "movement_type": "entry",
  "quantity": 100,
  "description": "Manuel stok girişi",
  "reference": "FT-2024-001"
}
```

### 4. Manuel Stok Çıkışı (ManualStockExitView)

**Menü:** Stok Yönetimi → Stok Çıkışı

**Özellikler:**
- Ürün seçimi (mevcut stok bilgisi ile)
- Miktar girişi
- Zorunlu açıklama (fire, bozulma, vb.)
- Referans no
- Yetersiz stok kontrolü
- Uyarı mesajları

**API Endpoint:** `POST /stock/movements/`

**Veri Formatı:**
```json
{
  "product_id": 1,
  "movement_type": "exit",
  "quantity": 10,
  "description": "Fire nedeniyle stok çıkışı",
  "reference": null
}
```

### 5. Tedarikçi Listesi (SuppliersListView)

**Menü:** Tedarikçi Yönetimi → Tedarikçiler

**Özellikler:**
- Tüm tedarikçileri listeler
- Arama özelliği
- Durum göstergesi (Aktif/Pasif)
- Düzenleme ve silme işlemleri
- Yeni tedarikçi ekleme butonu

**API Endpoints:**
- `GET /suppliers/` - Liste
- `DELETE /suppliers/{id}` - Silme

### 6. Yeni Tedarikçi Ekle (AddSupplierView)

**Menü:** Tedarikçi Yönetimi → Yeni Tedarikçi

**Form Alanları:**

**Temel Bilgiler:**
- Firma Adı * (zorunlu)
- İletişim Kişisi
- Telefon * (zorunlu)
- E-posta

**Adres ve Vergi Bilgileri:**
- Adres
- Vergi Dairesi
- Vergi Numarası

**Ek Bilgiler:**
- Notlar
- Aktif/Pasif durumu

**API Endpoint:** `POST /suppliers/`

**Veri Formatı:**
```json
{
  "company_name": "ABC Tedarik A.Ş.",
  "contact_person": "Ahmet Yılmaz",
  "phone": "+90 555 123 4567",
  "email": "info@abctedarik.com",
  "address": "İstanbul, Türkiye",
  "tax_office": "Kadıköy",
  "tax_number": "1234567890",
  "notes": "Güvenilir tedarikçi",
  "is_active": true
}
```

### 7. Alış Faturaları (PurchaseInvoicesView)

**Menü:** Tedarikçi Yönetimi → Alış Faturaları

**Özellikler:**
- Tüm alış faturalarını/irsaliyelerini listeler
- Ödeme durumuna göre filtreleme
- Fatura detaylarını görüntüleme
- Silme işlemi
- Yeni fatura ekleme butonu

**API Endpoints:**
- `GET /purchases/` - Liste
- `GET /purchases/{id}` - Detay
- `DELETE /purchases/{id}` - Silme

### 8. Yeni Fatura/İrsaliye (AddPurchaseInvoiceView)

**Menü:** Tedarikçi Yönetimi → Yeni Fatura/İrsaliye

**Form Bölümleri:**

**Fatura Bilgileri:**
- Tedarikçi * (dropdown)
- Fatura/İrsaliye No *
- Tarih *
- Belge Tipi * (Fatura/İrsaliye)
- Ödeme Durumu * (Beklemede/Ödendi/Kısmi)
- Notlar
- Belge Yükleme (PDF/Resim)

**Ürün Ekleme:**
- Ürün seçimi
- Miktar
- Birim Fiyat
- KDV Oranı (0%, 1%, 8%, 18%, 20%)
- Dinamik toplam hesaplama

**Eklenen Ürünler:**
- Liste görünümü
- Ürün silme
- Ara toplam, KDV ve genel toplam gösterimi

**Özellikler:**
- Otomatik stok güncelleme
- KDV hesaplama
- Belge yükleme
- Çoklu ürün ekleme
- Form validasyonu

**API Endpoints:**
- `POST /purchases/` - Fatura oluşturma
- `POST /purchases/upload-document/` - Belge yükleme

**Veri Formatı:**
```json
{
  "supplier_id": 1,
  "invoice_number": "FT-2024-001",
  "invoice_date": "2024-01-15",
  "document_type": "invoice",
  "payment_status": "pending",
  "subtotal": 1000.00,
  "tax_total": 180.00,
  "total_amount": 1180.00,
  "notes": "İlk alım",
  "document_url": "https://example.com/invoice.pdf",
  "items": [
    {
      "product_id": 1,
      "quantity": 100,
      "unit_price": 10.00,
      "tax_rate": 18
    }
  ]
}
```

## 🔌 API Servisi Metodları

### Stok Yönetimi

```python
# Stok hareketlerini getir
api_service.get_stock_movements(product_id=None)

# Stok hareketi oluştur
api_service.create_stock_movement(movement_data)

# Düşük stoklu ürünleri getir
api_service.get_low_stock_products(threshold=10)

# Stok özeti
api_service.get_stock_summary()
```

### Tedarikçi Yönetimi

```python
# Tedarikçileri getir
api_service.get_suppliers()

# Tek tedarikçi getir
api_service.get_supplier(supplier_id)

# Tedarikçi oluştur
api_service.create_supplier(supplier_data)

# Tedarikçi güncelle
api_service.update_supplier(supplier_id, supplier_data)

# Tedarikçi sil
api_service.delete_supplier(supplier_id)
```

### Alış Faturaları

```python
# Faturaları getir
api_service.get_purchase_invoices()

# Tek fatura getir
api_service.get_purchase_invoice(invoice_id)

# Fatura oluştur
api_service.create_purchase_invoice(invoice_data)

# Fatura güncelle
api_service.update_purchase_invoice(invoice_id, invoice_data)

# Fatura sil
api_service.delete_purchase_invoice(invoice_id)

# Belge yükle
api_service.upload_purchase_document(file_data)
```

## 🎨 UI/UX Özellikleri

### Renk Kodlaması

- **Mavi (Blue):** Genel bilgiler, başlıklar
- **Yeşil (Green):** Stok girişi, başarılı işlemler
- **Kırmızı (Red):** Stok çıkışı, uyarılar, silme işlemleri
- **Turuncu (Orange):** Düşük stok, ek bilgiler
- **Gri (Grey):** Pasif durumlar

### Form Validasyonu

- Zorunlu alanlar (*) işaretli
- Sayısal alanlar için keyboard type kontrolü
- Negatif değer kontrolü
- Yetersiz stok kontrolü
- E-posta format kontrolü
- Telefon format kontrolü

### Kullanıcı Geri Bildirimi

- Başarılı işlemler için yeşil bildirim
- Hata durumları için kırmızı bildirim
- Bilgilendirme için mavi bildirim
- Form hatalarında ilgili alana focus
- Yükleme durumu göstergeleri

## 🔄 Stok Akışı

### Otomatik Stok Çıkışı
Sipariş onaylandığında otomatik olarak stok düşer (backend tarafında).

### Manuel Stok Girişi
1. Stok Yönetimi → Stok Girişi
2. Ürün seç
3. Miktar gir
4. Açıklama ekle (opsiyonel)
5. Referans no ekle (opsiyonel)
6. Kaydet

### Fatura ile Stok Girişi
1. Tedarikçi Yönetimi → Yeni Fatura/İrsaliye
2. Tedarikçi seç
3. Fatura bilgilerini gir
4. Ürünleri ekle (miktar, fiyat, KDV)
5. Belge yükle (opsiyonel)
6. Kaydet → Otomatik stok güncellenir

### Manuel Stok Çıkışı
1. Stok Yönetimi → Stok Çıkışı
2. Ürün seç
3. Miktar gir
4. Açıklama gir (zorunlu - fire, bozulma, vb.)
5. Kaydet

## 📊 Raporlama

### Stok Hareketleri Raporu
- Tarih aralığına göre filtreleme
- Ürüne göre filtreleme
- Hareket tipine göre filtreleme
- Excel/PDF export (gelecek özellik)

### Düşük Stok Raporu
- Eşik değeri ayarlanabilir
- Kritik stok uyarıları
- Hızlı aksiyon butonları

## 🔐 Güvenlik

- Tüm API istekleri JWT token ile korunur
- Kullanıcı yetkilendirmesi (gelecek özellik)
- Veri validasyonu hem frontend hem backend'de
- SQL injection koruması
- XSS koruması

## 🚀 Kullanım

### Başlangıç

1. Admin panele giriş yapın
2. Sol menüden "Stok Yönetimi" veya "Tedarikçi Yönetimi" seçin
3. İlgili alt menüye tıklayın

### İlk Kurulum Adımları

1. **Tedarikçi Ekle:**
   - Tedarikçi Yönetimi → Yeni Tedarikçi
   - Tedarikçi bilgilerini girin

2. **Fatura Oluştur:**
   - Tedarikçi Yönetimi → Yeni Fatura/İrsaliye
   - Tedarikçi seçin ve ürünleri ekleyin
   - Stok otomatik güncellenecek

3. **Stok Takibi:**
   - Stok Yönetimi → Stok Hareketleri
   - Tüm hareketleri görüntüleyin

4. **Düşük Stok Kontrolü:**
   - Stok Yönetimi → Düşük Stok Uyarıları
   - Kritik stokları kontrol edin

## 🐛 Bilinen Sorunlar

- Backend API endpoint'leri henüz implement edilmemiş olabilir
- Bazı view'larda modal dialog'lar placeholder olarak bırakılmış
- Excel/PDF export özellikleri henüz eklenmemiş
- Kullanıcı yetkilendirmesi henüz aktif değil

## 📝 Gelecek Geliştirmeler

- [ ] Stok transfer işlemleri (depolar arası)
- [ ] Barkod okuyucu entegrasyonu
- [ ] Otomatik sipariş oluşturma (minimum stok altında)
- [ ] Tedarikçi performans analizi
- [ ] Fatura onay süreci
- [ ] Çoklu depo yönetimi
- [ ] Seri/Lot numarası takibi
- [ ] Son kullanma tarihi takibi
- [ ] Stok sayım modülü
- [ ] Excel/PDF export
- [ ] Gelişmiş raporlama ve grafikler

## 🤝 Katkıda Bulunma

Bu sistem modüler yapıda tasarlanmıştır. Yeni özellikler eklemek için:

1. İlgili view dosyasını düzenleyin
2. API servisine yeni metodlar ekleyin
3. Sidebar'a menü öğesi ekleyin
4. `app.py` dosyasında view'ı initialize edin

## 📞 Destek

Sorularınız için proje dokümantasyonuna bakın veya geliştirici ile iletişime geçin.

---

**Son Güncelleme:** 2024
**Versiyon:** 1.0.0
**Geliştirici:** E-Ticaret Admin Panel Ekibi