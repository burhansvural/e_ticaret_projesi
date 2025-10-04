import flet as ft
import requests
import base64
from datetime import datetime

API_URL = "http://127.0.0.1:8000"
UPLOAD_URL = f"{API_URL}/upload-image/"


class AdminPanel:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "E-Ticaret Admin Paneli"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.padding = 0
        
        # Durum yönetimi
        self.current_view = "dashboard"
        self.editing_product_id = None
        self.access_token = None  # Authentication token
        self.current_user = None  # Giriş yapan kullanıcı bilgisi
        self.show_register_form = False  # Kayıt formu gösterim durumu
        
        # Login kontrolü
        if not self.access_token:
            self.show_login()
        else:
            self.show_main_panel()
    
    def show_main_panel(self):
        """Ana panel görünümünü göster"""
        # Ana konteynerler
        self.sidebar = self.create_sidebar()
        self.content_area = ft.Container(
            expand=True,
            padding=20,
            content=ft.Column([])
        )
        
        # Ana layout
        self.main_layout = ft.Row([
            self.sidebar,
            ft.VerticalDivider(width=1),
            self.content_area
        ], expand=True, spacing=0)
        
        self.page.controls.clear()
        self.page.add(self.main_layout)
        self.show_dashboard()
    
    def show_login(self):
        """Login ekranını göster"""
        if self.show_register_form:
            self.show_register()
            return
            
        self.email_field = ft.TextField(
            label="E-posta",
            width=300,
            prefix_icon=ft.Icons.EMAIL,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Şifre",
            width=300,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            on_submit=lambda e: self.do_login(e)
        )
        
        login_button = ft.ElevatedButton(
            "Giriş Yap",
            width=300,
            height=50,
            on_click=self.do_login,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
        
        register_button = ft.TextButton(
            "Hesabınız yok mu? Kayıt Olun",
            on_click=lambda e: self.toggle_register_form(),
            style=ft.ButtonStyle(color=ft.Colors.BLUE)
        )
        
        login_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=80, color=ft.Colors.BLUE),
                ft.Text("Admin Panel", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("E-Ticaret Yönetim Sistemi", size=16, color=ft.Colors.GREY_600),
                ft.Container(height=30),
                self.email_field,
                self.password_field,
                ft.Container(height=10),
                login_button,
                register_button,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=50,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0),
            )
        )
        
        self.page.controls.clear()
        self.page.add(
            ft.Container(
                content=login_container,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.BLUE_GREY_50
            )
        )
        self.page.update()
    
    def toggle_register_form(self):
        """Kayıt formu ile login formu arasında geçiş yap"""
        self.show_register_form = not self.show_register_form
        self.show_login()
    
    def show_register(self):
        """Kayıt ekranını göster"""
        self.reg_first_name = ft.TextField(
            label="Ad",
            width=300,
            prefix_icon=ft.Icons.PERSON,
            autofocus=True
        )
        
        self.reg_last_name = ft.TextField(
            label="Soyad",
            width=300,
            prefix_icon=ft.Icons.PERSON_OUTLINE
        )
        
        self.reg_email = ft.TextField(
            label="E-posta",
            width=300,
            prefix_icon=ft.Icons.EMAIL
        )
        
        self.reg_phone = ft.TextField(
            label="Telefon (Opsiyonel)",
            width=300,
            prefix_icon=ft.Icons.PHONE
        )
        
        self.reg_password = ft.TextField(
            label="Şifre",
            width=300,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True
        )
        
        self.reg_password_confirm = ft.TextField(
            label="Şifre Tekrar",
            width=300,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            on_submit=lambda e: self.do_register(e)
        )
        
        self.reg_is_admin = ft.Checkbox(
            label="Admin Yetkisi",
            value=True
        )
        
        register_button = ft.ElevatedButton(
            "Kayıt Ol",
            width=300,
            height=50,
            on_click=self.do_register,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE
        )
        
        back_button = ft.TextButton(
            "Zaten hesabınız var mı? Giriş Yapın",
            on_click=lambda e: self.toggle_register_form(),
            style=ft.ButtonStyle(color=ft.Colors.BLUE)
        )
        
        register_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PERSON_ADD, size=80, color=ft.Colors.GREEN),
                ft.Text("Yeni Admin Kaydı", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Admin hesabı oluşturun", size=16, color=ft.Colors.GREY_600),
                ft.Container(height=20),
                self.reg_first_name,
                self.reg_last_name,
                self.reg_email,
                self.reg_phone,
                self.reg_password,
                self.reg_password_confirm,
                ft.Container(
                    content=self.reg_is_admin,
                    padding=ft.padding.only(left=50)
                ),
                ft.Container(height=10),
                register_button,
                back_button,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=50,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0),
            )
        )
        
        self.page.controls.clear()
        self.page.add(
            ft.Container(
                content=register_container,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.BLUE_GREY_50
            )
        )
        self.page.update()
    
    def do_register(self, e):
        """Kayıt işlemini gerçekleştir"""
        first_name = self.reg_first_name.value
        last_name = self.reg_last_name.value
        email = self.reg_email.value
        phone = self.reg_phone.value
        password = self.reg_password.value
        password_confirm = self.reg_password_confirm.value
        is_admin = self.reg_is_admin.value
        
        # Validasyon
        if not all([first_name, last_name, email, password, password_confirm]):
            self.show_error("Lütfen tüm zorunlu alanları doldurun!")
            return
        
        if password != password_confirm:
            self.show_error("Şifreler eşleşmiyor!")
            return
        
        if len(password) < 8:
            self.show_error("Şifre en az 8 karakter olmalıdır!")
            return
        
        try:
            # Kayıt API'sine istek gönder
            response = requests.post(
                f"{API_URL}/users/register",
                json={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone if phone else None,
                    "password": password,
                    "is_admin": is_admin
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.show_success("Kayıt başarılı! E-posta doğrulama kodu gönderildi. Lütfen e-postanızı kontrol edin.")
                
                # Doğrulama ekranına geç
                self.show_verification_screen(email)
            else:
                error_detail = response.json().get("detail", "Kayıt başarısız!")
                self.show_error(error_detail)
                
        except requests.exceptions.ConnectionError:
            self.show_error("Backend sunucusuna bağlanılamıyor! Lütfen backend'in çalıştığından emin olun.")
        except Exception as e:
            self.show_error(f"Kayıt hatası: {e}")
    
    def show_verification_screen(self, email):
        """E-posta doğrulama ekranını göster"""
        self.verify_email = email
        
        self.verify_code = ft.TextField(
            label="Doğrulama Kodu",
            width=300,
            prefix_icon=ft.Icons.VERIFIED_USER,
            autofocus=True,
            on_submit=lambda e: self.do_verify(e)
        )
        
        verify_button = ft.ElevatedButton(
            "Doğrula",
            width=300,
            height=50,
            on_click=self.do_verify,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
        
        back_button = ft.TextButton(
            "Giriş ekranına dön",
            on_click=lambda e: self.back_to_login(),
            style=ft.ButtonStyle(color=ft.Colors.BLUE)
        )
        
        verify_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.EMAIL, size=80, color=ft.Colors.BLUE),
                ft.Text("E-posta Doğrulama", size=32, weight=ft.FontWeight.BOLD),
                ft.Text(f"{email} adresine gönderilen kodu girin", size=14, color=ft.Colors.GREY_600),
                ft.Container(height=30),
                self.verify_code,
                ft.Container(height=10),
                verify_button,
                back_button,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=50,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0),
            )
        )
        
        self.page.controls.clear()
        self.page.add(
            ft.Container(
                content=verify_container,
                alignment=ft.alignment.center,
                expand=True,
                bgcolor=ft.Colors.BLUE_GREY_50
            )
        )
        self.page.update()
    
    def do_verify(self, e):
        """E-posta doğrulama işlemini gerçekleştir"""
        code = self.verify_code.value
        
        if not code:
            self.show_error("Lütfen doğrulama kodunu girin!")
            return
        
        try:
            # Doğrulama API'sine istek gönder (admin olarak)
            response = requests.post(
                f"{API_URL}/users/verify-email",
                json={
                    "email": self.verify_email,
                    "code": code,
                    "is_admin": True  # Admin kaydı doğrulaması
                },
                timeout=5
            )
            
            if response.status_code == 200:
                self.show_success("E-posta doğrulandı! Şimdi giriş yapabilirsiniz.")
                self.back_to_login()
            else:
                error_detail = response.json().get("detail", "Doğrulama başarısız!")
                self.show_error(error_detail)
                
        except requests.exceptions.ConnectionError:
            self.show_error("Backend sunucusuna bağlanılamıyor!")
        except Exception as e:
            self.show_error(f"Doğrulama hatası: {e}")
    
    def back_to_login(self):
        """Login ekranına geri dön"""
        self.show_register_form = False
        self.show_login()
    
    def do_login(self, e):
        """Login işlemini gerçekleştir"""
        email = self.email_field.value
        password = self.password_field.value
        
        if not email or not password:
            self.show_error("E-posta ve şifre gereklidir!")
            return
        
        try:
            # Login API'sine istek gönder (admin olarak)
            response = requests.post(
                f"{API_URL}/users/login",
                json={
                    "email": email,
                    "password": password,
                    "is_admin": True  # Admin paneli için admin girişi
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"DEBUG - Login response: {data}")
                
                # Backend'den gelen response formatı: {user: {...}, tokens: {access_token: ...}, message: ...}
                tokens = data.get("tokens", {})
                self.access_token = tokens.get("access_token")
                self.current_user = data.get("user")
                
                print(f"DEBUG - Access token: {self.access_token}")
                print(f"DEBUG - Current user: {self.current_user}")
                
                # Admin kontrolü
                if not self.current_user.get("is_admin"):
                    self.show_error("Bu panele sadece admin kullanıcılar erişebilir!")
                    self.access_token = None
                    self.current_user = None
                    return
                
                print("DEBUG - Calling show_main_panel()")
                # Ana paneli göster
                self.show_main_panel()
                print("DEBUG - show_main_panel() completed")
            else:
                error_detail = response.json().get("detail", "Giriş başarısız!")
                self.show_error(error_detail)
                
        except requests.exceptions.ConnectionError:
            self.show_error("Backend sunucusuna bağlanılamıyor! Lütfen backend'in çalıştığından emin olun.")
        except Exception as e:
            self.show_error(f"Giriş hatası: {e}")
    
    def logout(self):
        """Çıkış yap"""
        self.access_token = None
        self.current_user = None
        self.show_login()
    
    def get_headers(self):
        """API istekleri için Authorization header'ı döndür"""
        if self.access_token:
            return {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        return {"Content-Type": "application/json"}
    
    def create_sidebar(self):
        """Sol menü oluştur"""
        # Kullanıcı bilgisi
        user_info = ft.Container(
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=30, color=ft.Colors.WHITE),
                    ft.Column([
                        ft.Text(
                            self.current_user.get("email", "Admin") if self.current_user else "Admin",
                            size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text("Admin", size=10, color=ft.Colors.BLUE_GREY_300)
                    ], spacing=0)
                ], spacing=10),
                ft.Container(height=5),
                ft.ElevatedButton(
                    "Çıkış Yap",
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda e: self.logout(),
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    width=250
                )
            ], spacing=5),
            bgcolor=ft.Colors.BLUE_GREY_800,
            border_radius=8,
            margin=ft.margin.all(10)
        )
        
        return ft.Container(
            width=280,
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=ft.padding.all(0),
            content=ft.Column([
                # Header
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=40, color=ft.Colors.WHITE),
                        ft.Text("Admin Panel", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("E-Ticaret Yönetimi", size=12, color=ft.Colors.BLUE_GREY_300)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
                ),
                ft.Divider(color=ft.Colors.BLUE_GREY_700, height=1),
                
                # Kullanıcı bilgisi
                user_info,
                
                # Menü öğeleri
                ft.Container(
                    expand=True,
                    padding=ft.padding.symmetric(vertical=10),
                    content=ft.ListView([
                        self.create_menu_item("Dashboard", ft.Icons.DASHBOARD, "dashboard"),
                        
                        # Ürün Yönetimi
                        self.create_menu_section("Ürün Yönetimi", ft.Icons.INVENTORY),
                        self.create_submenu_item("Ürün Listesi", ft.Icons.LIST, "products_list"),
                        self.create_submenu_item("Ürün Ekle", ft.Icons.ADD_BOX, "add_product"),
                        self.create_submenu_item("Kategoriler", ft.Icons.CATEGORY, "categories"),
                        self.create_submenu_item("Stok Yönetimi", ft.Icons.WAREHOUSE, "inventory"),
                        
                        # Sipariş Yönetimi
                        self.create_menu_section("Sipariş Yönetimi", ft.Icons.SHOPPING_CART),
                        self.create_submenu_item("Tüm Siparişler", ft.Icons.RECEIPT_LONG, "orders_list"),
                        self.create_submenu_item("Bekleyen Siparişler", ft.Icons.PENDING, "pending_orders"),
                        self.create_submenu_item("Tamamlanan Siparişler", ft.Icons.CHECK_CIRCLE, "completed_orders"),
                        self.create_submenu_item("İptal Edilen Siparişler", ft.Icons.CANCEL, "cancelled_orders"),
                        
                        # Müşteri Yönetimi
                        self.create_menu_section("Müşteri Yönetimi", ft.Icons.PEOPLE),
                        self.create_submenu_item("Müşteri Listesi", ft.Icons.PERSON, "customers_list"),
                        self.create_submenu_item("Müşteri Grupları", ft.Icons.GROUP, "customer_groups"),
                        self.create_submenu_item("Müşteri Yorumları", ft.Icons.RATE_REVIEW, "reviews"),
                        
                        # Raporlar
                        self.create_menu_section("Raporlar", ft.Icons.ANALYTICS),
                        self.create_submenu_item("Satış Raporları", ft.Icons.TRENDING_UP, "sales_reports"),
                        self.create_submenu_item("Ürün Raporları", ft.Icons.BAR_CHART, "product_reports"),
                        self.create_submenu_item("Müşteri Raporları", ft.Icons.PIE_CHART, "customer_reports"),
                        
                        # Pazarlama
                        self.create_menu_section("Pazarlama", ft.Icons.CAMPAIGN),
                        self.create_submenu_item("Kampanyalar", ft.Icons.LOCAL_OFFER, "campaigns"),
                        self.create_submenu_item("Kuponlar", ft.Icons.CARD_GIFTCARD, "coupons"),
                        self.create_submenu_item("E-posta Pazarlama", ft.Icons.EMAIL, "email_marketing"),
                        
                        # Ayarlar
                        self.create_menu_section("Sistem", ft.Icons.SETTINGS),
                        self.create_submenu_item("Genel Ayarlar", ft.Icons.TUNE, "settings"),
                        self.create_submenu_item("Ödeme Ayarları", ft.Icons.PAYMENT, "payment_settings"),
                        self.create_submenu_item("Kargo Ayarları", ft.Icons.LOCAL_SHIPPING, "shipping_settings"),
                        self.create_submenu_item("Kullanıcı Yönetimi", ft.Icons.ADMIN_PANEL_SETTINGS, "user_management"),
                    ], spacing=2)
                )
            ], spacing=0)
        )
    
    def create_menu_item(self, title, icon, view_name):
        """Ana menü öğesi oluştur"""
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icon, color=ft.Colors.WHITE),
                title=ft.Text(title, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                on_click=lambda e: self.navigate_to(view_name)
            ),
            bgcolor=ft.Colors.BLUE_600 if self.current_view == view_name else None,
            border_radius=ft.border_radius.all(8),
            margin=ft.margin.symmetric(horizontal=10, vertical=2)
        )
    
    def create_menu_section(self, title, icon):
        """Menü bölümü başlığı oluştur"""
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            content=ft.Row([
                ft.Icon(icon, size=18, color=ft.Colors.BLUE_GREY_400),
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_400)
            ], spacing=10)
        )
    
    def create_submenu_item(self, title, icon, view_name):
        """Alt menü öğesi oluştur"""
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Container(width=20),  # Girinti için boşluk
                title=ft.Row([
                    ft.Icon(icon, size=16, color=ft.Colors.BLUE_GREY_300),
                    ft.Text(title, color=ft.Colors.BLUE_GREY_100, size=13)
                ], spacing=10),
                on_click=lambda e: self.navigate_to(view_name)
            ),
            bgcolor=ft.Colors.BLUE_700 if self.current_view == view_name else None,
            border_radius=ft.border_radius.all(6),
            margin=ft.margin.symmetric(horizontal=15, vertical=1)
        )
    
    def navigate_to(self, view_name):
        """Sayfa navigasyonu"""
        self.current_view = view_name
        self.update_sidebar_selection()
        
        # İçerik alanını güncelle
        if view_name == "dashboard":
            self.show_dashboard()
        elif view_name == "products_list":
            self.show_products_list()
        elif view_name == "add_product":
            self.show_add_product()
        elif view_name == "orders_list":
            self.show_orders_list()
        elif view_name == "pending_orders":
            self.show_pending_orders()
        elif view_name == "customers_list":
            self.show_customers_list()
        elif view_name == "categories":
            self.show_categories()
        elif view_name == "inventory":
            self.show_inventory()
        elif view_name == "sales_reports":
            self.show_sales_reports()
        else:
            self.show_coming_soon(view_name)
    
    def update_sidebar_selection(self):
        """Sidebar seçimini güncelle"""
        self.sidebar = self.create_sidebar()
        self.main_layout.controls[0] = self.sidebar
        self.page.update()
    
    def show_dashboard(self):
        """Dashboard görünümü"""
        self.content_area.content = ft.Column([
            ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # İstatistik kartları
            ft.Row([
                self.create_stat_card("Toplam Ürün", "156", ft.Icons.INVENTORY, ft.Colors.BLUE),
                self.create_stat_card("Toplam Sipariş", "89", ft.Icons.SHOPPING_CART, ft.Colors.GREEN),
                self.create_stat_card("Toplam Müşteri", "234", ft.Icons.PEOPLE, ft.Colors.ORANGE),
                self.create_stat_card("Toplam Gelir", "₺45,678", ft.Icons.ATTACH_MONEY, ft.Colors.PURPLE),
            ], spacing=20),
            
            ft.Container(height=20),
            
            # Son aktiviteler
            ft.Text("Son Aktiviteler", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=20,
                content=ft.Column([
                    self.create_activity_item("Yeni sipariş alındı", "#12345", "2 dakika önce"),
                    self.create_activity_item("Ürün stokta tükendi", "iPhone 15", "15 dakika önce"),
                    self.create_activity_item("Yeni müşteri kaydı", "ahmet@email.com", "1 saat önce"),
                    self.create_activity_item("Sipariş tamamlandı", "#12340", "2 saat önce"),
                ], spacing=10)
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.page.update()
    
    def create_stat_card(self, title, value, icon, color):
        """İstatistik kartı oluştur"""
        return ft.Container(
            width=250,
            height=120,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=20,
            content=ft.Row([
                ft.Column([
                    ft.Text(title, size=14, color=ft.Colors.GREY_600),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color),
                ], spacing=5),
                ft.Icon(icon, size=40, color=color)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
    
    def create_activity_item(self, title, subtitle, time):
        """Aktivite öğesi oluştur"""
        return ft.Row([
            ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.BLUE),
            ft.Column([
                ft.Text(title, weight=ft.FontWeight.W_500),
                ft.Text(subtitle, size=12, color=ft.Colors.GREY_600)
            ], spacing=2),
            ft.Text(time, size=12, color=ft.Colors.GREY_500)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def show_products_list(self):
        """Ürün listesi görünümü"""
        self.content_area.content = ft.Column([
            ft.Row([
                ft.Text("Ürün Yönetimi", size=28, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    "Yeni Ürün Ekle",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.navigate_to("add_product")
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            
            # Arama ve filtreler
            ft.Row([
                ft.TextField(
                    label="Ürün ara...",
                    prefix_icon=ft.Icons.SEARCH,
                    width=300
                ),
                ft.Dropdown(
                    label="Kategori",
                    width=150,
                    options=[
                        ft.dropdown.Option("Tümü"),
                        ft.dropdown.Option("Elektronik"),
                        ft.dropdown.Option("Giyim"),
                        ft.dropdown.Option("Ev & Yaşam"),
                    ]
                ),
                ft.ElevatedButton("Filtrele", icon=ft.Icons.FILTER_LIST)
            ], spacing=10),
            
            ft.Container(height=10),
            
            # Ürün tablosu
            self.create_products_table()
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.load_products_data()
    
    def create_products_table(self):
        """Ürün tablosu oluştur"""
        self.products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Resim")),
                ft.DataColumn(ft.Text("Ürün Adı")),
                ft.DataColumn(ft.Text("Kategori")),
                ft.DataColumn(ft.Text("Fiyat")),
                ft.DataColumn(ft.Text("Stok")),
                ft.DataColumn(ft.Text("Birim")),
                ft.DataColumn(ft.Text("Durum")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=[]
        )
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=20,
            content=self.products_table
        )
    
    def load_products_data(self):
        """Ürün verilerini yükle"""
        try:
            response = requests.get(f"{API_URL}/products/", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            products_data = response.json()
            
            self.products_table.rows.clear()
            for product in products_data:
                self.products_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(product['id']))),
                        ft.DataCell(
                            ft.Image(
                                src=product.get('image_url', ''),
                                width=40,
                                height=40,
                                fit=ft.ImageFit.COVER,
                                border_radius=5,
                                error_content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED)
                            )
                        ),
                        ft.DataCell(ft.Text(product['name'])),
                        ft.DataCell(ft.Text("Genel")),  # Kategori bilgisi backend'de yok
                        ft.DataCell(ft.Text(f"₺{product['price']:.2f}")),
                        ft.DataCell(ft.Text(str(product.get('stock_quantity', 0)))),
                        ft.DataCell(ft.Text(product.get('unit', 'adet'))),
                        ft.DataCell(ft.Container(
                            bgcolor=ft.Colors.GREEN_100,
                            border_radius=15,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            content=ft.Text("Aktif", color=ft.Colors.GREEN_800, size=12)
                        )),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                tooltip="Düzenle",
                                on_click=lambda e, p=product: self.edit_product(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Sil",
                                on_click=lambda e, p=product: self.delete_product(p['id'])
                            )
                        ], spacing=0))
                    ])
                )
            self.page.update()
        except Exception as e:
            self.show_error(f"Ürünler yüklenirken hata: {e}")
    
    def show_add_product(self):
        """Ürün ekleme formu"""
        # Form kontrolleri
        self.product_name_input = ft.TextField(label="Ürün Adı", width=400)
        self.product_desc_input = ft.TextField(
            label="Açıklama", 
            width=400, 
            multiline=True, 
            min_lines=3,
            max_lines=5
        )
        self.product_price_input = ft.TextField(label="Fiyat", width=200, prefix_text="₺")
        
        # Kategorileri API'den yükle
        self.product_category_input = ft.Dropdown(
            label="Kategori",
            width=200,
            options=[]
        )
        self.load_categories_for_dropdown()
        
        self.product_stock_input = ft.TextField(label="Stok Miktarı", width=200)
        
        # Birim seçimi
        self.product_unit_input = ft.Dropdown(
            label="Birim",
            width=200,
            options=[
                ft.dropdown.Option("adet"),
                ft.dropdown.Option("kg"),
                ft.dropdown.Option("gram"),
                ft.dropdown.Option("litre"),
                ft.dropdown.Option("ml"),
                ft.dropdown.Option("metre"),
                ft.dropdown.Option("cm"),
                ft.dropdown.Option("paket"),
                ft.dropdown.Option("kutu"),
            ],
            value="adet"
        )
        
        # Resim yükleme
        self.uploaded_image_url = ft.TextField(visible=False)
        self.image_container = ft.Container(
            width=200,
            height=200,
            border=ft.border.all(2, ft.Colors.GREY_400),
            border_radius=10,
            content=ft.Column([
                ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=40, color=ft.Colors.GREY_500),
                ft.Text("Resim Seç", color=ft.Colors.GREY_500)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center
        )
        
        # Dosya seçici
        self.file_picker = ft.FilePicker(on_result=self.on_file_picker_result)
        self.page.overlay.append(self.file_picker)
        
        # Başlık düzenleme moduna göre değişir
        title = "Ürün Düzenle" if hasattr(self, 'editing_product_id') and self.editing_product_id else "Yeni Ürün Ekle"
        
        self.content_area.content = ft.Column([
            ft.Text(title, size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=30,
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            self.product_name_input,
                            self.product_desc_input,
                            ft.Row([
                                self.product_price_input,
                                self.product_stock_input,
                                self.product_unit_input
                            ], spacing=20),
                            self.product_category_input,
                        ], spacing=20),
                        
                        ft.Container(width=50),  # Boşluk
                        
                        ft.Column([
                            ft.Text("Ürün Resmi", weight=ft.FontWeight.BOLD),
                            self.image_container,
                            ft.ElevatedButton(
                                "Resim Seç",
                                icon=ft.Icons.UPLOAD_FILE,
                                on_click=lambda _: self.file_picker.pick_files(
                                    allow_multiple=False,
                                    allowed_extensions=["png", "jpeg", "jpg"]
                                )
                            )
                        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ], alignment=ft.MainAxisAlignment.START),
                    
                    ft.Container(height=30),
                    
                    ft.Row([
                        ft.ElevatedButton(
                            "İptal",
                            on_click=self.cancel_product_edit
                        ),
                        ft.ElevatedButton(
                            "Ürünü Kaydet",
                            icon=ft.Icons.SAVE,
                            on_click=self.save_product
                        )
                    ], alignment=ft.MainAxisAlignment.END, spacing=10)
                ], spacing=20)
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.page.update()
        
        # Düzenleme modundaysa form alanlarını doldur
        self.fill_product_form()
    
    def load_categories_for_dropdown(self):
        """Kategorileri API'den yükleyip dropdown'a ekle"""
        try:
            response = requests.get(f"{API_URL}/categories/", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            categories = response.json()
            
            # Dropdown seçeneklerini temizle ve yenilerini ekle
            self.product_category_input.options.clear()
            for category in categories:
                self.product_category_input.options.append(
                    ft.dropdown.Option(category['name'])
                )
            
        except Exception as ex:
            print(f"Kategori yükleme hatası: {ex}")
            # Hata durumunda varsayılan kategoriler
            self.product_category_input.options = [
                ft.dropdown.Option("Elektronik"),
                ft.dropdown.Option("Giyim"),
                ft.dropdown.Option("Ev & Yaşam"),
                ft.dropdown.Option("Spor"),
                ft.dropdown.Option("Kitap"),
            ]
    
    def cancel_product_edit(self, e):
        """Ürün düzenlemeyi iptal et"""
        # Düzenleme modunu temizle
        if hasattr(self, 'editing_product_id'):
            self.editing_product_id = None
        if hasattr(self, 'editing_product_data'):
            self.editing_product_data = None
        self.navigate_to("products_list")
    
    def on_file_picker_result(self, e: ft.FilePickerResultEvent):
        """Dosya seçimi sonucu"""
        if not e.files:
            return
        
        selected_file = e.files[0]
        try:
            with open(selected_file.path, "rb") as f:
                file_content_binary = f.read()
            
            # Önizleme göster
            preview_image = ft.Image(
                src_base64=base64.b64encode(file_content_binary).decode('utf-8'),
                width=200,
                height=200,
                fit=ft.ImageFit.CONTAIN,
                border_radius=10
            )
            self.image_container.content = preview_image
            self.page.update()
            
            # Resmi sunucuya yükle
            files = {"file": (selected_file.name, file_content_binary, "image/jpeg")}
            response = requests.post(UPLOAD_URL, files=files, headers=self.get_headers())
            response.raise_for_status()
            
            url = response.json().get("url")
            self.uploaded_image_url.value = url
            preview_image.src = url
            preview_image.src_base64 = None
            
        except Exception as ex:
            self.show_error(f"Resim yüklenemedi: {ex}")
        
        self.page.update()
    
    def save_product(self, e):
        """Ürünü kaydet"""
        try:
            price = float(self.product_price_input.value or 0)
        except ValueError:
            self.show_error("Geçerli bir fiyat girin.")
            return
        
        try:
            stock_quantity = int(self.product_stock_input.value or 0)
        except ValueError:
            self.show_error("Geçerli bir stok miktarı girin.")
            return
        
        if not self.product_name_input.value:
            self.show_error("Ürün adı zorunludur.")
            return
        
        product_data = {
            "name": self.product_name_input.value,
            "description": self.product_desc_input.value or "",
            "price": price,
            "stock_quantity": stock_quantity,
            "unit": self.product_unit_input.value or "adet",
            "image_url": self.uploaded_image_url.value or ""
        }
        
        # Kategori seçimi varsa ekle
        if self.product_category_input.value:
            # Kategori adından ID'yi bul
            try:
                response = requests.get(f"{API_URL}/categories/", headers=self.get_headers())
                if response.status_code == 200:
                    categories = response.json()
                    for cat in categories:
                        if cat['name'] == self.product_category_input.value:
                            product_data['category_id'] = cat['id']
                            break
            except:
                pass
        
        try:
            # Düzenleme modunda mı yoksa yeni ekleme mi?
            if hasattr(self, 'editing_product_id') and self.editing_product_id:
                # Ürün güncelleme (PUT)
                response = requests.put(
                    f"{API_URL}/products/{self.editing_product_id}", 
                    json=product_data,
                    headers=self.get_headers()
                )
                response.raise_for_status()
                self.show_success("Ürün başarıyla güncellendi!")
                # Düzenleme modunu temizle
                self.editing_product_id = None
                if hasattr(self, 'editing_product_data'):
                    self.editing_product_data = None
            else:
                # Yeni ürün ekleme (POST)
                response = requests.post(
                    f"{API_URL}/products/", 
                    json=product_data,
                    headers=self.get_headers()
                )
                response.raise_for_status()
                self.show_success("Ürün başarıyla eklendi!")
            
            self.navigate_to("products_list")
            
        except requests.exceptions.RequestException as ex:
            self.show_error(f"API hatası: {ex}")
    
    def show_orders_list(self):
        """Sipariş listesi görünümü"""
        # Sipariş tablosunu oluştur
        self.orders_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sipariş No")),
                ft.DataColumn(ft.Text("Müşteri ID")),
                ft.DataColumn(ft.Text("Tarih")),
                ft.DataColumn(ft.Text("Tutar")),
                ft.DataColumn(ft.Text("Ürün Sayısı")),
                ft.DataColumn(ft.Text("Durum")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=[]
        )
        
        self.content_area.content = ft.Column([
            ft.Text("Sipariş Yönetimi", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Yenile butonu
            ft.Row([
                ft.ElevatedButton(
                    "Siparişleri Yenile",
                    icon=ft.Icons.REFRESH,
                    on_click=lambda e: self.page.run_thread(self.load_orders_data)
                )
            ]),
            
            ft.Container(height=10),
            
            # Sipariş tablosu
            ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=20,
                content=self.orders_table
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.page.run_thread(self.load_orders_data)
    
    def load_orders_data(self):
        """Sipariş verilerini yükle"""
        try:
            print("Siparişler yükleniyor...")  # Debug
            response = requests.get(f"{API_URL}/orders/", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            orders_data = response.json()
            print(f"Toplam {len(orders_data)} sipariş bulundu")  # Debug
            
            self.orders_table.rows.clear()
            for order in orders_data:
                print(f"Sipariş işleniyor: {order['id']}")  # Debug
                # Sipariş durumu rengi
                status_color = self.get_status_color(order.get('status', 'pending'))
                
                # Ürün sayısını hesapla
                item_count = len(order.get('items', []))
                
                # Tarih formatla
                created_date = order.get('created_date', '')
                if created_date:
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%d.%m.%Y %H:%M')
                    except:
                        formatted_date = created_date[:16]
                else:
                    formatted_date = 'N/A'
                
                self.orders_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"#{order['id']}")),
                        ft.DataCell(ft.Text(str(order.get('owner_id', 'N/A')))),
                        ft.DataCell(ft.Text(formatted_date)),
                        ft.DataCell(ft.Text(f"{order.get('total_price', 0):.2f} TL")),
                        ft.DataCell(ft.Text(str(item_count))),
                        ft.DataCell(ft.Container(
                            content=ft.Text(
                                self.get_status_text(order.get('status', 'pending')),
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            border_radius=15
                        )),
                        ft.DataCell(
                            content=ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                tooltip="Detayları Görüntüle",
                                on_click=lambda e, oid=order['id']: self.page.run_thread(lambda: self.show_order_details(oid))
                            ),
                            ft.IconButton(
                                icon=ft.Icons.RESTAURANT_MENU,
                                tooltip="Hazırlama Yönet",
                                on_click=lambda e, oid=order['id']: self.page.run_thread(lambda: self.show_preparation_manager(oid)),
                                bgcolor=ft.Colors.BLUE_100 if order.get('status') in ['pending', 'preparing'] else ft.Colors.GREY_200
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Durumu Güncelle",
                                on_click=lambda e, oid=order['id']: self.page.run_thread(lambda: self.show_order_status_dialog(oid))
                            )
                        ], spacing=5))
                    ]),
                )
                print(f"Handler'lar oluşturuldu: {order['id']}")  # Debug
        except Exception as e:
            self.show_error(f"Siparişler yüklenirken hata: {e}")
        self.page.update()
    
    def get_status_color(self, status):
        """Sipariş durumuna göre renk döndür"""
        status_colors = {
            'pending': ft.Colors.ORANGE_600,
            'preparing': ft.Colors.BLUE_600,
            'ready': ft.Colors.GREEN_600,
            'shipped': ft.Colors.PURPLE_600,
            'delivered': ft.Colors.GREEN_800,
            'cancelled': ft.Colors.RED_600
        }
        return status_colors.get(status, ft.Colors.GREY_600)
    
    def get_status_text(self, status):
        """Sipariş durumunu Türkçe'ye çevir"""
        status_texts = {
            'pending': 'Bekliyor',
            'preparing': 'Hazırlanıyor',
            'ready': 'Hazır',
            'shipped': 'Kargoda',
            'delivered': 'Teslim Edildi',
            'cancelled': 'İptal Edildi'
        }
        return status_texts.get(status, status)
    
    def show_order_details(self, order_id):
        """Sipariş detaylarını göster"""
        try:
            print(f"Sipariş detayları açılıyor: {order_id}")  # Debug
            response = requests.get(f"{API_URL}/orders/{order_id}", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            order = response.json()
            print(f"Sipariş verisi alındı: {order}")  # Debug
            
            # Müşteri bilgilerini al
            customer_response = requests.get(f"{API_URL}/users/", timeout=5, headers=self.get_headers())
            customers = customer_response.json() if customer_response.status_code == 200 else []
            customer = next((c for c in customers if c['id'] == order.get('owner_id')), None)
            
            # Ürün detaylarını oluştur
            items_content = []
            for item in order.get('items', []):
                # Ürün bilgilerini al
                try:
                    product_response = requests.get(f"{API_URL}/products/{item['product_id']}", timeout=5, headers=self.get_headers())
                    product = product_response.json() if product_response.status_code == 200 else None
                    product_name = product['name'] if product else f"Ürün #{item['product_id']}"
                except:
                    product_name = f"Ürün #{item['product_id']}"
                
                items_content.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(product_name, expand=True),
                            ft.Text(f"{item['quantity']} kg"),
                            ft.Text(f"{item['price_per_item']:.2f} TL"),
                            ft.Text(f"{item['quantity'] * item['price_per_item']:.2f} TL", weight=ft.FontWeight.BOLD)
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.GREY_50,
                        border_radius=5,
                        margin=ft.margin.only(bottom=5)
                    )
                )
            
            # Tarih formatla
            created_date = order.get('created_date', '')
            if created_date:
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%d.%m.%Y %H:%M')
                except:
                    formatted_date = created_date[:16]
            else:
                formatted_date = 'N/A'
            
            def close_dialog(e):
                print("Modal kapatılıyor")  # Debug
                self.close_modal()
            
            def open_status_dialog(e):
                print("Durum güncelleme dialogu açılıyor")  # Debug
                self.close_modal()  # Önce modalı kapat
                self.page.run_thread(lambda: self.show_order_status_dialog(order_id))
            
            # DÜZELTİLDİ: Artık ft.AlertDialog yerine sade bir Container kullanıyoruz
            modal_content = ft.Container(
                content=ft.Column([
                    ft.Text(f"Sipariş Detayları - #{order['id']}", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # İçerik Column'u
                    ft.Container(
                        content=ft.Column([
                            # Müşteri bilgileri
                            ft.Text("Müşteri Bilgileri", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Ad Soyad: {customer['first_name']} {customer['last_name']}" if customer else "Müşteri bulunamadı"),
                                    ft.Text(f"E-posta: {customer['email']}" if customer else ""),
                                    ft.Text(f"Telefon: {customer.get('phone', 'Belirtilmemiş')}" if customer else ""),
                                    ft.Text(f"Adres: {customer.get('address', 'Belirtilmemiş')}" if customer else ""),
                                ]),
                                padding=10,
                                bgcolor=ft.Colors.BLUE_50,
                                border_radius=5
                            ),
                            
                            ft.Divider(),
                            
                            # Sipariş bilgileri
                            ft.Text("Sipariş Bilgileri", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Sipariş Tarihi: {formatted_date}"),
                                    ft.Text(f"Durum: {self.get_status_text(order.get('status', 'pending'))}"),
                                    ft.Text(f"Toplam Tutar: {order.get('total_price', 0):.2f} TL"),
                                    ft.Text(f"Notlar: {order.get('notes', 'Yok')}")
                                ]),
                                padding=10,
                                bgcolor=ft.Colors.GREEN_50,
                                border_radius=5
                            ),
                            
                            ft.Divider(),
                            
                            # Ürün listesi
                            ft.Text("Sipariş Edilen Ürünler", size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text("Ürün", expand=True, weight=ft.FontWeight.BOLD),
                                        ft.Text("Miktar", weight=ft.FontWeight.BOLD),
                                        ft.Text("Birim Fiyat", weight=ft.FontWeight.BOLD),
                                        ft.Text("Toplam", weight=ft.FontWeight.BOLD)
                                    ]),
                                    ft.Divider(),
                                    *items_content
                                ]),
                                padding=10,
                                bgcolor=ft.Colors.ORANGE_50,
                                border_radius=5
                            )
                        ], spacing=10, scroll=ft.ScrollMode.AUTO),
                        width=600,
                        height=400
                    ),
                ], spacing=15, scroll=ft.ScrollMode.AUTO),
                
                # Dialog'un görünümünü taklit eden Container stili:
                width=650,
                height=650,
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
            )
            
            # Eylemleri ayrı bir Container'a al
            actions_row = ft.Container(
                content=ft.Row([
                    ft.TextButton("Kapat", on_click=close_dialog),
                    ft.ElevatedButton(
                        "Durumu Güncelle",
                        icon=ft.Icons.EDIT,
                        on_click=open_status_dialog
                    )
                ], alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.only(top=15)
            )
            
            # Tüm içeriği tek bir Column'da topla
            full_modal = ft.Column([modal_content, actions_row], tight=True)
            
            print("Modal açılıyor (Custom Modal)")  # Debug
            
            # Modal'ı açma işlemini UI thread'e zorlamak için run_thread kullanmak hala en güvenilir yoldur.
            self.page.run_thread(lambda: self._show_overlay_modal(full_modal))
            
            print("Modal başarıyla açıldı.")
            
        except Exception as e:
            print(f"Hata oluştu: {e}")  # Debug
            self.show_error(f"Sipariş detayları yüklenirken hata: {e}")
    
    def show_order_status_dialog(self, order_id):
        """Sipariş durumu güncelleme dialogu"""
        print(f"Durum güncelleme dialogu açılıyor: {order_id}")  # Debug
        
        # Mevcut sipariş bilgilerini al
        try:
            response = requests.get(f"{API_URL}/orders/{order_id}", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            order = response.json()
            current_status = order.get('status', 'pending')
            current_notes = order.get('notes', '')
            print(f"Mevcut durum: {current_status}, notlar: {current_notes}")  # Debug
        except Exception as e:
            print(f"Sipariş bilgileri alınırken hata: {e}")  # Debug
            current_status = 'pending'
            current_notes = ''
        
        # Form alanları
        status_dropdown = ft.Dropdown(
            label="Sipariş Durumu",
            value=current_status,
            options=[
                ft.dropdown.Option("pending", "Bekliyor"),
                ft.dropdown.Option("preparing", "Hazırlanıyor"),
                ft.dropdown.Option("ready", "Hazır"),
                ft.dropdown.Option("shipped", "Kargoda"),
                ft.dropdown.Option("delivered", "Teslim Edildi"),
                ft.dropdown.Option("cancelled", "İptal Edildi"),
            ],
            width=300
        )
        
        notes_field = ft.TextField(
            label="Admin Notları",
            value=current_notes,
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=300
        )
        
        def update_status(e):
            try:
                print(f"Durum güncelleniyor: {status_dropdown.value}, notlar: {notes_field.value}")  # Debug
                update_data = {
                    "status": status_dropdown.value,
                    "notes": notes_field.value
                }
                
                response = requests.put(
                    f"{API_URL}/orders/{order_id}",
                    json=update_data,
                    timeout=5,
                    headers=self.get_headers()
                )
                response.raise_for_status()
                print("Durum başarıyla güncellendi")  # Debug
                
                self.close_modal()
                self.show_success("Sipariş durumu başarıyla güncellendi!")
                self.page.run_thread(self.load_orders_data)  # Tabloyu yenile
                
            except Exception as ex:
                print(f"Güncelleme hatası: {ex}")  # Debug
                self.show_error(f"Sipariş güncellenirken hata: {ex}")
        
        def cancel_update(e):
            print("Güncelleme iptal edildi")  # Debug
            self.close_modal()
        
        # Custom Modal İçeriği
        modal_content = ft.Container(
            content=ft.Column([
                ft.Text(f"Sipariş Durumu Güncelle - #{order_id}", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                ft.Container(
                    content=ft.Column([
                        status_dropdown,
                        notes_field,
                        ft.Container(
                            content=ft.Text(
                                "Not: Durum değişikliği müşteriye bildirilecektir.",
                                size=12,
                                color=ft.Colors.GREY_600
                            ),
                            margin=ft.margin.only(top=10)
                        )
                    ], spacing=15),
                    width=350
                ),
            ], spacing=15),
            
            # Modal stili
            width=400,
            height=350,
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
        )
        
        # Eylemler
        actions_row = ft.Container(
            content=ft.Row([
                ft.TextButton("İptal", on_click=cancel_update),
                ft.ElevatedButton("Güncelle", on_click=update_status),
            ], alignment=ft.MainAxisAlignment.END),
            padding=ft.padding.only(top=15)
        )
        
        # Tüm içeriği birleştir
        full_modal = ft.Column([modal_content, actions_row], tight=True)
        
        print("Durum güncelleme modalı açılıyor (Custom Modal)")  # Debug
        
        # Modal'ı açma işlemini UI thread'e zorla
        self.page.run_thread(lambda: self._show_overlay_modal(full_modal))
        
        print("Durum güncelleme modalı başarıyla açıldı.")
    
    def show_customers_list(self):
        """Müşteri listesi görünümü"""
        self.content_area.content = ft.Column([
            ft.Text("Müşteri Yönetimi", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Arama ve filtreler
            ft.Row([
                ft.TextField(
                    label="Müşteri ara...",
                    prefix_icon=ft.Icons.SEARCH,
                    width=300
                ),
                ft.Dropdown(
                    label="Durum",
                    width=150,
                    options=[
                        ft.dropdown.Option("Tümü"),
                        ft.dropdown.Option("Aktif"),
                        ft.dropdown.Option("Pasif"),
                    ]
                ),
                ft.ElevatedButton("Filtrele", icon=ft.Icons.FILTER_LIST)
            ], spacing=10),
            
            ft.Container(height=10),
            
            # Müşteri tablosu
            self.create_customers_table()
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.load_customers_data()
    
    def show_categories(self):
        """Kategori yönetimi"""
        self.load_categories_data()
    
    def load_categories_data(self):
        """Kategorileri API'den yükle"""
        try:
            response = requests.get(f"{API_URL}/categories/", headers=self.get_headers())
            response.raise_for_status()
            categories = response.json()
            
            # Kategori ekleme formu
            self.category_name_field = ft.TextField(
                label="Kategori Adı",
                width=300,
                hint_text="Kategori adını girin"
            )
            
            self.category_description_field = ft.TextField(
                label="Açıklama",
                width=300,
                hint_text="Kategori açıklaması (opsiyonel)",
                multiline=True,
                max_lines=3
            )
            
            add_category_button = ft.ElevatedButton(
                "Kategori Ekle",
                on_click=self.add_category,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE
            )
            
            # Kategoriler tablosu
            categories_table = self.create_categories_table(categories)
            
            self.content_area.content = ft.Column([
                ft.Text("Kategori Yönetimi", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Kategori ekleme formu
                ft.Container(
                    content=ft.Column([
                        ft.Text("Yeni Kategori Ekle", size=20, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            self.category_name_field,
                            self.category_description_field,
                            add_category_button
                        ], alignment=ft.MainAxisAlignment.START),
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Kategoriler listesi
                ft.Text("Mevcut Kategoriler", size=20, weight=ft.FontWeight.BOLD),
                categories_table
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            
        except Exception as e:
            self.content_area.content = ft.Column([
                ft.Text("Kategori Yönetimi", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED),
                        ft.Text(f"Kategoriler yüklenirken hata: {e}", color=ft.Colors.RED)
                    ]),
                    padding=20
                )
            ])
        
        self.page.update()
    
    def create_categories_table(self, categories):
        """Kategoriler tablosu oluştur"""
        if not categories:
            return ft.Container(
                content=ft.Text("Henüz kategori bulunmuyor.", size=16, color=ft.Colors.GREY_600),
                padding=20
            )
        
        table_rows = []
        
        # Başlık satırı
        table_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text("Kategori Adı", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text("Açıklama", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
                ]
            )
        )
        
        # Kategori satırları
        for category in categories:
            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(category['id']))),
                        ft.DataCell(ft.Text(category['name'])),
                        ft.DataCell(ft.Text(category.get('description', '') or '-')),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    tooltip="Düzenle",
                                    on_click=lambda e, cat_id=category['id']: self.edit_category(cat_id)
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    tooltip="Sil",
                                    icon_color=ft.Colors.RED,
                                    on_click=lambda e, cat_id=category['id']: self.delete_category(cat_id)
                                ),
                            ])
                        ),
                    ]
                )
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Kategori Adı")),
                ft.DataColumn(ft.Text("Açıklama")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=table_rows[1:],  # Başlık satırını hariç tut
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
        )
    
    def add_category(self, e):
        """Yeni kategori ekle"""
        if not self.category_name_field.value or not self.category_name_field.value.strip():
            self.show_error("Kategori adı boş olamaz!")
            return
        
        try:
            category_data = {
                "name": self.category_name_field.value.strip(),
                "description": self.category_description_field.value.strip() if self.category_description_field.value else None
            }
            
            response = requests.post(
                f"{API_URL}/categories/", 
                json=category_data,
                headers=self.get_headers()
            )
            response.raise_for_status()
            
            self.show_success("Kategori başarıyla eklendi!")
            
            # Formu temizle
            self.category_name_field.value = ""
            self.category_description_field.value = ""
            
            # Kategorileri yeniden yükle
            self.load_categories_data()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                self.show_error("Bu isimde bir kategori zaten mevcut!")
            elif e.response.status_code == 401:
                self.show_error("Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.")
                self.logout()
            else:
                self.show_error(f"Kategori eklenirken hata: {e}")
        except Exception as e:
            self.show_error(f"Kategori eklenirken hata: {e}")
    
    def edit_category(self, category_id):
        """Kategori düzenle"""
        try:
            # Kategori bilgilerini al
            response = requests.get(f"{API_URL}/categories/{category_id}", headers=self.get_headers())
            response.raise_for_status()
            category = response.json()
            
            # Düzenleme dialog'u
            name_field = ft.TextField(
                label="Kategori Adı",
                value=category['name'],
                width=300
            )
            
            description_field = ft.TextField(
                label="Açıklama",
                value=category.get('description', '') or '',
                width=300,
                multiline=True,
                max_lines=3
            )
            
            def save_changes(e):
                if not name_field.value or not name_field.value.strip():
                    self.show_error("Kategori adı boş olamaz!")
                    return
                
                try:
                    update_data = {
                        "name": name_field.value.strip(),
                        "description": description_field.value.strip() if description_field.value else None
                    }
                    
                    response = requests.put(
                        f"{API_URL}/categories/{category_id}", 
                        json=update_data,
                        headers=self.get_headers()
                    )
                    response.raise_for_status()
                    
                    self.show_success("Kategori başarıyla güncellendi!")
                    self.close_modal()
                    self.load_categories_data()
                    
                except requests.exceptions.HTTPError as ex:
                    if ex.response.status_code == 400:
                        self.show_error("Bu isimde bir kategori zaten mevcut!")
                    else:
                        self.show_error(f"Güncelleme hatası: {ex}")
                except Exception as ex:
                    self.show_error(f"Güncelleme hatası: {ex}")
            
            def cancel_edit(e):
                self.close_modal()
            
            # Custom Modal İçeriği
            modal_content = ft.Container(
                content=ft.Column([
                    ft.Text("Kategori Düzenle", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    ft.Container(
                        content=ft.Column([
                            name_field,
                            description_field
                        ], spacing=15),
                        width=350
                    ),
                ], spacing=15),
                
                # Modal stili
                width=400,
                height=300,
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
            )
            
            # Eylemler
            actions_row = ft.Container(
                content=ft.Row([
                    ft.TextButton("İptal", on_click=cancel_edit),
                    ft.TextButton("Kaydet", on_click=save_changes),
                ], alignment=ft.MainAxisAlignment.END),
                padding=ft.padding.only(top=15)
            )
            
            # Tüm içeriği birleştir
            full_modal = ft.Column([modal_content, actions_row], tight=True)
            
            # Modal'ı aç
            self.page.run_thread(lambda: self._show_overlay_modal(full_modal))
            
        except Exception as e:
            self.show_error(f"Kategori bilgileri alınırken hata: {e}")
    
    def delete_category(self, category_id):
        """Kategori sil"""
        def confirm_delete(e):
            try:
                response = requests.delete(
                    f"{API_URL}/categories/{category_id}",
                    headers=self.get_headers()
                )
                response.raise_for_status()
                self.show_success("Kategori başarıyla silindi!")
                self.close_modal()
                self.load_categories_data()
            except requests.exceptions.HTTPError as ex:
                if ex.response.status_code == 400:
                    error_detail = ex.response.json().get('detail', 'Kategori silinemedi')
                    self.show_error(error_detail)
                else:
                    self.show_error(f"Silme hatası: {ex}")
            except Exception as ex:
                self.show_error(f"Silme hatası: {ex}")
        
        def cancel_delete(e):
            self.close_modal()
        
        # Custom Modal İçeriği
        modal_content = ft.Container(
            content=ft.Column([
                ft.Text("Kategoriyi Sil", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                ft.Container(
                    content=ft.Text(
                        f"ID: {category_id} olan kategoriyi silmek istediğinizden emin misiniz?\n\nNot: Bu kategoriye ait ürünler varsa kategori silinemez.",
                        text_align=ft.TextAlign.CENTER
                    ),
                    width=400,
                    padding=20
                ),
            ], spacing=15),
            
            # Modal stili
            width=450,
            height=250,
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
        )
        
        # Eylemler
        actions_row = ft.Container(
            content=ft.Row([
                ft.TextButton("İptal", on_click=cancel_delete),
                ft.TextButton("Sil", on_click=confirm_delete),
            ], alignment=ft.MainAxisAlignment.END),
            padding=ft.padding.only(top=15)
        )
        
        # Tüm içeriği birleştir
        full_modal = ft.Column([modal_content, actions_row], tight=True)
        
        # Modal'ı aç
        self.page.run_thread(lambda: self._show_overlay_modal(full_modal))
    
    def show_inventory(self):
        """Stok yönetimi"""
        self.content_area.content = ft.Column([
            ft.Text("Stok Yönetimi", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Stok yönetimi burada olacak...", size=16)
        ], spacing=10)
        self.page.update()
    
    def show_sales_reports(self):
        """Satış raporları"""
        self.content_area.content = ft.Column([
            ft.Text("Satış Raporları", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Satış raporları burada görüntülenecek...", size=16)
        ], spacing=10)
        self.page.update()
    
    def show_pending_orders(self):
        """Bekleyen siparişler yönetimi"""
        self.load_pending_orders_data()
    
    def load_pending_orders_data(self):
        """Bekleyen siparişleri API'den yükle"""
        try:
            response = requests.get(f"{API_URL}/orders/", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            orders_data = response.json()
            
            # Sadece bekleyen siparişleri filtrele (status = "pending" olanlar)
            pending_orders = [order for order in orders_data if order.get('status', 'pending') == 'pending']
            
            # Yenile butonu
            refresh_button = ft.ElevatedButton(
                "Yenile",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: self.load_pending_orders_data(),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
            
            # Bekleyen siparişler tablosu
            pending_orders_table = self.create_pending_orders_table(pending_orders)
            
            self.content_area.content = ft.Column([
                ft.Text("Bekleyen Siparişler", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Üst bilgi ve yenile butonu
                ft.Row([
                    ft.Text(f"Toplam {len(pending_orders)} bekleyen sipariş", size=16, color=ft.Colors.GREY_700),
                    refresh_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # Siparişler tablosu
                pending_orders_table
            ], spacing=10, scroll=ft.ScrollMode.AUTO)
            
        except Exception as e:
            self.content_area.content = ft.Column([
                ft.Text("Bekleyen Siparişler", size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED),
                        ft.Text(f"Siparişler yüklenirken hata: {e}", color=ft.Colors.RED)
                    ]),
                    padding=20
                )
            ])
        
        self.page.update()
    
    def create_pending_orders_table(self, orders):
        """Bekleyen siparişler tablosu oluştur"""
        if not orders:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=64, color=ft.Colors.GREY_400),
                    ft.Text("Bekleyen sipariş bulunmuyor.", size=16, color=ft.Colors.GREY_600),
                    ft.Text("Yeni siparişler geldiğinde burada görünecek.", size=14, color=ft.Colors.GREY_500)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                alignment=ft.alignment.center
            )
        
        table_rows = []
        
        # Sipariş satırları
        for order in orders:
            # Sipariş tarihini formatla
            order_date = order.get('created_at', '2024-01-15')
            if 'T' in order_date:
                order_date = order_date.split('T')[0]
            
            # Sipariş öğelerini say
            items_count = len(order.get('items', []))
            
            # Toplam tutarı hesapla
            total_price = order.get('total_price', 0.0)
            
            # Durum rengi
            status_color = ft.Colors.ORANGE
            status_text = "Bekliyor"
            
            table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(order['id']))),
                        ft.DataCell(ft.Text(str(order.get('customer_id', 'Bilinmiyor')))),
                        ft.DataCell(ft.Text(order_date)),
                        ft.DataCell(ft.Text(f"{total_price:.2f} TL")),
                        ft.DataCell(ft.Text(f"{items_count} ürün")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(status_text, color=ft.Colors.WHITE, size=12),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.ElevatedButton(
                                    "Onayla",
                                    icon=ft.Icons.CHECK,
                                    bgcolor=ft.Colors.GREEN,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda e, oid=order['id']: self.approve_order(oid)
                                ),
                                ft.ElevatedButton(
                                    "Reddet",
                                    icon=ft.Icons.CLOSE,
                                    bgcolor=ft.Colors.RED,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda e, oid=order['id']: self.reject_order(oid)
                                ),
                                ft.IconButton(
                                    ft.Icons.VISIBILITY,
                                    tooltip="Detayları Görüntüle",
                                    on_click=lambda e, oid=order['id']: self.view_order_details(oid)
                                ),
                            ], spacing=5)
                        ),
                    ]
                )
            )
        
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sipariş ID")),
                ft.DataColumn(ft.Text("Müşteri ID")),
                ft.DataColumn(ft.Text("Tarih")),
                ft.DataColumn(ft.Text("Toplam")),
                ft.DataColumn(ft.Text("Ürün Sayısı")),
                ft.DataColumn(ft.Text("Durum")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=table_rows,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
        )
    
    def approve_order(self, order_id):
        """Siparişi onayla"""
        def confirm_approve(e):
            try:
                # Sipariş durumunu "approved" olarak güncelle
                update_data = {"status": "approved"}
                response = requests.put(
                    f"{API_URL}/orders/{order_id}", 
                    json=update_data,
                    headers=self.get_headers()
                )
                response.raise_for_status()
                
                self.show_success(f"Sipariş #{order_id} başarıyla onaylandı!")
                self.load_pending_orders_data()  # Listeyi yenile
            except Exception as ex:
                self.show_error(f"Sipariş onaylanırken hata: {ex}")
            self.close_modal()
        
        def cancel_approve(e):
            self.close_modal()
        
        # Custom modal content
        modal_content = ft.Container(
            content=ft.Column([
                ft.Text("Siparişi Onayla", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(
                    f"Sipariş #{order_id}'yi onaylamak istediğinizden emin misiniz?\n\nOnaylanan sipariş hazırlanmaya başlanacak.",
                    size=14
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("İptal", on_click=cancel_approve),
                    ft.ElevatedButton("Onayla", on_click=confirm_approve),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=10),
            width=400,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )
        
        self._show_overlay_modal(modal_content)
    
    def reject_order(self, order_id):
        """Siparişi reddet"""
        def confirm_reject(e):
            try:
                # Sipariş durumunu "cancelled" olarak güncelle
                update_data = {"status": "cancelled"}
                response = requests.put(
                    f"{API_URL}/orders/{order_id}", 
                    json=update_data,
                    headers=self.get_headers()
                )
                response.raise_for_status()
                
                self.show_success(f"Sipariş #{order_id} reddedildi!")
                self.load_pending_orders_data()  # Listeyi yenile
            except Exception as ex:
                self.show_error(f"Sipariş reddedilirken hata: {ex}")
            self.close_modal()
        
        def cancel_reject(e):
            self.close_modal()
        
        # Custom modal content
        modal_content = ft.Container(
            content=ft.Column([
                ft.Text("Siparişi Reddet", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(
                    f"Sipariş #{order_id}'yi reddetmek istediğinizden emin misiniz?\n\nReddedilen sipariş iptal edilecek.",
                    size=14
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("İptal", on_click=cancel_reject),
                    ft.ElevatedButton("Reddet", on_click=confirm_reject, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=10),
            width=400,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )
        
        self._show_overlay_modal(modal_content)
    
    def view_order_details(self, order_id):
        """Sipariş detaylarını görüntüle"""
        try:
            # Sipariş detaylarını al
            response = requests.get(f"{API_URL}/orders/{order_id}", headers=self.get_headers())
            response.raise_for_status()
            order = response.json()
            
            # Sipariş tarihini formatla
            order_date = order.get('created_at', '2024-01-15')
            if 'T' in order_date:
                order_date = order_date.split('T')[0]
            
            def close_details(e):
                self.close_modal()
            
            # Sipariş öğelerini ayrıntılı ListView olarak oluştur
            items_list = []
            total_items = 0
            
            for item in order.get('items', []):
                product_id = item.get('product_id', 'Bilinmiyor')
                quantity = item.get('quantity', 0)
                price = item.get('price', 0.0)
                total_price = quantity * price
                total_items += quantity
                
                # Her ürün için ayrıntılı bir kart oluştur
                item_card = ft.Container(
                    content=ft.Row([
                        # Ürün bilgileri
                        ft.Column([
                            ft.Text(f"Ürün ID: {product_id}", size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Birim Fiyat: {price:.2f} TL", size=12, color=ft.Colors.GREY_700),
                            ft.Text(f"Adet: {quantity}", size=12, color=ft.Colors.GREY_700),
                        ], spacing=2, expand=True),
                        # Toplam fiyat
                        ft.Column([
                            ft.Text("Toplam", size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"{total_price:.2f} TL", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                        ], spacing=2, horizontal_alignment=ft.CrossAxisAlignment.END),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15,
                    margin=ft.margin.only(bottom=8),
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                )
                items_list.append(item_card)
            
            # Eğer ürün yoksa boş mesajı göster
            if not items_list:
                items_list.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, size=48, color=ft.Colors.GREY_400),
                            ft.Text("Bu siparişte ürün bulunmuyor", size=14, color=ft.Colors.GREY_600),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                        alignment=ft.alignment.center
                    )
                )
            
            # Scroll edilebilir ürün listesi
            products_listview = ft.Container(
                content=ft.ListView(
                    controls=items_list,
                    spacing=0,
                    padding=ft.padding.all(10),
                ),
                height=250,
                bgcolor=ft.Colors.GREY_50,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREY_300)
            )
            
            # Custom modal content
            modal_content = ft.Container(
                content=ft.Column([
                    # Başlık
                    ft.Text(f"Sipariş #{order_id} Detayları", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # Sipariş bilgileri
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Müşteri ID:", size=14, weight=ft.FontWeight.W_500),
                                ft.Text(f"{order.get('customer_id', 'Bilinmiyor')}", size=14),
                            ]),
                            ft.Row([
                                ft.Text("Tarih:", size=14, weight=ft.FontWeight.W_500),
                                ft.Text(f"{order_date}", size=14),
                            ]),
                            ft.Row([
                                ft.Text("Durum:", size=14, weight=ft.FontWeight.W_500),
                                ft.Container(
                                    content=ft.Text(
                                        f"{order.get('status', 'pending').title()}", 
                                        size=12, 
                                        color=ft.Colors.WHITE
                                    ),
                                    bgcolor=ft.Colors.ORANGE if order.get('status') == 'pending' else ft.Colors.GREEN,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12
                                ),
                            ]),
                            ft.Row([
                                ft.Text("Toplam Ürün:", size=14, weight=ft.FontWeight.W_500),
                                ft.Text(f"{total_items} adet", size=14),
                            ]),
                            ft.Row([
                                ft.Text("Toplam Tutar:", size=14, weight=ft.FontWeight.W_500),
                                ft.Text(f"{order.get('total_price', 0.0):.2f} TL", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                            ]),
                        ], spacing=8),
                        padding=15,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=8,
                    ),
                    
                    ft.Container(height=10),
                    
                    # Ürün listesi başlığı
                    ft.Text("Sipariş İçeriği:", size=16, weight=ft.FontWeight.BOLD),
                    
                    # Scroll edilebilir ürün listesi
                    products_listview,
                    
                    ft.Container(height=15),
                    
                    # Kapatma butonu
                    ft.Row([
                        ft.TextButton("Kapat", on_click=close_details),
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=10),
                width=650,
                height=600,
                padding=25,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            )
            
            print("Modal açılıyor")  # Debug
            self._show_overlay_modal(modal_content)
            print("Modal başarıyla açıldı.")
            
        except Exception as e:
            self.show_error(f"Sipariş detayları alınırken hata: {e}")
    
    def show_coming_soon(self, view_name):
        """Yakında gelecek sayfalar için placeholder"""
        view_titles = {
            "pending_orders": "Bekleyen Siparişler",
            "completed_orders": "Tamamlanan Siparişler",
            "cancelled_orders": "İptal Edilen Siparişler",
            "customer_groups": "Müşteri Grupları",
            "reviews": "Müşteri Yorumları",
            "product_reports": "Ürün Raporları",
            "customer_reports": "Müşteri Raporları",
            "campaigns": "Kampanyalar",
            "coupons": "Kuponlar",
            "email_marketing": "E-posta Pazarlama",
            "settings": "Genel Ayarlar",
            "payment_settings": "Ödeme Ayarları",
            "shipping_settings": "Kargo Ayarları",
            "user_management": "Kullanıcı Yönetimi"
        }
        
        title = view_titles.get(view_name, view_name.replace("_", " ").title())
        
        self.content_area.content = ft.Column([
            ft.Text(title, size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Container(
                height=300,
                content=ft.Column([
                    ft.Icon(ft.Icons.CONSTRUCTION, size=80, color=ft.Colors.GREY_400),
                    ft.Text("Bu özellik yakında gelecek!", size=20, color=ft.Colors.GREY_600),
                    ft.Text(f"{title} sayfası geliştirme aşamasında.", size=14, color=ft.Colors.GREY_500)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center
            )
        ], spacing=10)
        self.page.update()
    
    def edit_product(self, product):
        """Ürün düzenleme"""
        self.editing_product_id = product['id']
        self.editing_product_data = product  # Ürün verilerini sakla
        self.navigate_to("add_product")
        
        # Form alanları oluşturulduktan sonra doldur
        self.fill_product_form()
    
    def fill_product_form(self):
        """Düzenleme modunda form alanlarını doldur"""
        if not hasattr(self, 'editing_product_data') or not self.editing_product_data:
            return
        
        product = self.editing_product_data
        
        # Form alanları oluşturulmuş mu kontrol et
        if hasattr(self, 'product_name_input') and self.product_name_input:
            self.product_name_input.value = product.get('name', '')
            self.product_desc_input.value = product.get('description', '')
            self.product_price_input.value = str(product.get('price', ''))
            self.product_stock_input.value = str(product.get('stock_quantity', ''))
            self.product_unit_input.value = product.get('unit', 'adet')
            
            # Kategori seçimi (eğer kategori bilgisi varsa)
            if product.get('category_id'):
                # Kategori ID'sinden kategori adını bul
                try:
                    response = requests.get(
                        f"{API_URL}/categories/{product['category_id']}",
                        headers=self.get_headers()
                    )
                    if response.status_code == 200:
                        category = response.json()
                        self.product_category_input.value = category.get('name', '')
                except:
                    pass
            
            # Resim varsa göster
            if product.get('image_url'):
                self.uploaded_image_url.value = product['image_url']
                try:
                    preview_image = ft.Image(
                        src=product['image_url'],
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=10
                    )
                    self.image_container.content = preview_image
                except:
                    pass
            
            self.page.update()
    
    def delete_product(self, product_id):
        """Ürün silme"""
        def confirm_delete(e):
            try:
                response = requests.delete(
                    f"{API_URL}/products/{product_id}",
                    headers=self.get_headers()
                )
                response.raise_for_status()
                self.show_success("Ürün başarıyla silindi!")
                self.load_products_data()
            except Exception as ex:
                self.show_error(f"Silme hatası: {ex}")
            self.close_modal()
        
        def cancel_delete(e):
            self.close_modal()
        
        # Custom modal content
        modal_content = ft.Container(
            content=ft.Column([
                ft.Text("Ürünü Sil", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(
                    f"ID: {product_id} olan ürünü silmek istediğinizden emin misiniz?",
                    size=14
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.TextButton("İptal", on_click=cancel_delete),
                    ft.ElevatedButton("Sil", on_click=confirm_delete, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=10),
            width=400,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
        )
        
        self._show_overlay_modal(modal_content)
    
    def create_customers_table(self):
        """Müşteri tablosu oluştur"""
        self.customers_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Ad Soyad")),
                ft.DataColumn(ft.Text("E-posta")),
                ft.DataColumn(ft.Text("Telefon")),
                ft.DataColumn(ft.Text("Kayıt Tarihi")),
                ft.DataColumn(ft.Text("Durum")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=[]
        )
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=20,
            content=self.customers_table
        )
    
    def load_customers_data(self):
        """Müşteri verilerini yükle"""
        try:
            # Gerçek API'den müşteri verilerini çek
            response = requests.get(f"{API_URL}/users/", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            customers_data = response.json()
            
            self.customers_table.rows.clear()
            for customer in customers_data:
                # API'den gelen veri yapısına göre düzenle
                status_color = ft.Colors.GREEN if customer.get('is_active', True) else ft.Colors.RED
                status_text = "Aktif" if customer.get('is_active', True) else "Pasif"
                
                # Ad soyad birleştir
                full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                if not full_name:
                    full_name = customer.get('email', 'Bilinmiyor')
                
                # Kayıt tarihini formatla
                created_at = customer.get('created_at', '2024-01-15')
                if 'T' in created_at:
                    created_at = created_at.split('T')[0]
                
                self.customers_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(customer['id']))),
                        ft.DataCell(ft.Text(full_name)),
                        ft.DataCell(ft.Text(customer['email'])),
                        ft.DataCell(ft.Text(customer.get('phone', '-'))),
                        ft.DataCell(ft.Text(created_at)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(status_text, color=ft.Colors.WHITE, size=12),
                                bgcolor=status_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.VISIBILITY,
                                    tooltip="Detayları Görüntüle",
                                    on_click=lambda e, cid=customer['id']: self.view_customer_details(cid)
                                ),
                                ft.IconButton(
                                    ft.Icons.EDIT,
                                    tooltip="Düzenle",
                                    on_click=lambda e, cid=customer['id']: self.edit_customer(cid)
                                ),
                                ft.IconButton(
                                    ft.Icons.BLOCK if customer.get('is_active', True) else ft.Icons.CHECK_CIRCLE,
                                    tooltip="Durumu Değiştir",
                                    on_click=lambda e, cid=customer['id']: self.toggle_customer_status(cid)
                                )
                            ], spacing=5)
                        )
                    ])
                )
            
        except Exception as e:
            self.show_error(f"Müşteriler yüklenirken hata: {e}")
        self.page.update()
    
    def view_customer_details(self, customer_id):
        """Müşteri detaylarını görüntüle"""
        self.show_info(f"Müşteri {customer_id} detayları görüntülenecek")
    
    def edit_customer(self, customer_id):
        """Müşteri düzenle"""
        self.show_info(f"Müşteri {customer_id} düzenleme sayfası açılacak")
    
    def toggle_customer_status(self, customer_id):
        """Müşteri durumunu değiştir"""
        self.show_info(f"Müşteri {customer_id} durumu değiştirilecek")
    
    def show_info(self, message):
        """Bilgi mesajı göster"""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.Colors.BLUE,
            open=True
        )
        self.page.update()
    
    def show_error(self, message):
        """Hata mesajı göster"""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.Colors.RED,
            open=True
        )
        self.page.update()
    
    def show_success(self, message):
        """Başarı mesajı göster"""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=ft.Colors.GREEN,
            open=True
        )
        self.page.update()
    
    def _update_ui_sync(self):
        """
        UI güncellemelerini ana thread'e zorlar. 
        Bu metot, işçi thread'den çağrılabilir.
        """
        # self.page.update() çağrısını doğrudan UI thread'e yönlendirmeliyiz.
        # Flet 0.28.3'te bu genellikle page.update() ile çalışır, 
        # ancak başarısız olduğu durumda run_thread ile sarmalamak gerekir.
        try:
             # Eğer burası thread'de ise, update'in kendisi bazen kaybolabilir.
             self.page.update()
        except:
             # Eğer update çağrısı thread'de başarısız oluyorsa, 
             # run_thread kullanarak UI thread'e geri atarız.
             self.page.run_thread(self.page.update)
    
    def _open_dialog_on_ui(self, dialog_control):
        """
        Dialog açma işlemini UI thread'e zorlar ve günceller.
        """
        # Bu fonksiyon, page.run_thread içinde çağrılacaktır.
        self.page.dialog = dialog_control
        dialog_control.open = True
        self._update_ui_sync() # UI güncellemeyi çağır
    
    def _show_overlay_modal(self, modal_content):
        """Custom Modal'ı gösterir (Dialog'a alternatif)"""
        
        # 1. Modal Katmanını Oluştur
        # Bu Container, tüm ekranı kaplar ve arka planı flu yapar
        self.modal_overlay = ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=modal_content,
                        width=700,
                        # Modal içeriği ortalanır
                        alignment=ft.alignment.center
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER # Yatayda ortala
            ),
            # Arka planı koyu ve hafif şeffaf yap
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK),
            expand=True,
            # Modal'ı kapatmak için dışarı tıklama olayını ekleyebiliriz (opsiyonel)
            on_click=lambda e: self.close_modal() 
        )
        # 2. Modal'ı sayfanın overlay'ine ekle
        self.page.overlay.append(self.modal_overlay)
        self.page.update()
    
    def close_modal(self, e=None):
        """Custom Modal'ı kapat"""
        if hasattr(self, 'modal_overlay') and self.modal_overlay in self.page.overlay:
            self.page.overlay.remove(self.modal_overlay)
            self.page.update()
    
    def load_completed_orders_data(self):
        """Tamamlanan sipariş verilerini yükle"""
        try:
            response = requests.get(f"{API_URL}/orders/", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            orders_data = response.json()
            
            self.orders_table.rows.clear()
            for order in orders_data:
                # Tarih formatını düzenle
                created_date = order.get('created_date', '')
                if created_date:
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%d.%m.%Y %H:%M')
                    except:
                        formatted_date = created_date[:10]  # Sadece tarih kısmı
                else:
                    formatted_date = "Bilinmiyor"
                
                # Ürün sayısını hesapla
                item_count = len(order.get('items', []))
                
                self.orders_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"#{order['id']}")),
                        ft.DataCell(ft.Text(str(order.get('owner_id', 'N/A')))),
                        ft.DataCell(ft.Text(formatted_date)),
                        ft.DataCell(ft.Text(f"₺{order.get('total_price', 0):.2f}")),
                        ft.DataCell(ft.Text(str(item_count))),
                        ft.DataCell(ft.Container(
                            bgcolor=ft.Colors.GREEN_100,
                            border_radius=15,
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            content=ft.Text("Tamamlandı", color=ft.Colors.GREEN_800, size=12)
                        )),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY, 
                                icon_color=ft.Colors.BLUE,
                                tooltip="Detayları Görüntüle",
                                on_click=lambda e, order_id=order['id']: self.page.run_thread(lambda: self.view_order_details(order_id))
                            ),
                        ], spacing=0))
                    ])
                )
            
            self.page.update()
            self.show_success(f"{len(orders_data)} sipariş yüklendi")
            
        except requests.exceptions.RequestException as ex:
            self.show_error(f"API'ye ulaşılamıyor: {ex}")
        except Exception as ex:
            self.show_error(f"Sipariş yükleme hatası: {ex}")
    
    def view_order_details(self, order_id):
        """Sipariş detaylarını görüntüle"""
        self.show_info(f"Sipariş #{order_id} detayları görüntülenecek")
    
    def show_pending_orders(self):
        """Bekleyen siparişler görünümü"""
        # Bekleyen sipariş tablosunu oluştur
        self.pending_orders_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sipariş No")),
                ft.DataColumn(ft.Text("Müşteri ID")),
                ft.DataColumn(ft.Text("Tarih")),
                ft.DataColumn(ft.Text("Tutar")),
                ft.DataColumn(ft.Text("Ürün Sayısı")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=[]
        )
        
        self.content_area.content = ft.Column([
            ft.Text("Bekleyen Siparişler", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            
            # Bilgi mesajı
            ft.Container(
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10,
                padding=20,
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE),
                    ft.Text(
                        "Bu demo uygulamada tüm siparişler otomatik olarak 'Tamamlandı' durumunda görünür. "
                        "Gerçek bir uygulamada burada bekleyen siparişler listelenecektir.",
                        size=14,
                        color=ft.Colors.BLUE_800
                    )
                ], spacing=10)
            ),
            
            # Yenile butonu
            ft.Row([
                ft.ElevatedButton(
                    "Siparişleri Yenile",
                    icon=ft.Icons.REFRESH,
                    on_click=lambda e: self.load_pending_orders_data()
                )
            ]),
            
            ft.Container(height=10),
            
            # Bekleyen sipariş tablosu
            ft.Container(
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=20,
                content=self.pending_orders_table
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
        self.load_pending_orders_data()
    
    def load_pending_orders_data(self):
        """Bekleyen sipariş verilerini yükle"""
        try:
            response = requests.get(f"{API_URL}/orders/", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            orders_data = response.json()
            
            self.pending_orders_table.rows.clear()
            
            # Demo için: Son 5 siparişi "bekleyen" olarak göster
            recent_orders = orders_data[-5:] if len(orders_data) >= 5 else orders_data
            
            for order in recent_orders:
                # Tarih formatını düzenle
                created_date = order.get('created_date', '')
                if created_date:
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%d.%m.%Y %H:%M')
                    except:
                        formatted_date = created_date[:10]
                else:
                    formatted_date = "Bilinmiyor"
                
                # Ürün sayısını hesapla
                item_count = len(order.get('items', []))
                
                self.pending_orders_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"#{order['id']}")),
                        ft.DataCell(ft.Text(str(order.get('owner_id', 'N/A')))),
                        ft.DataCell(ft.Text(formatted_date)),
                        ft.DataCell(ft.Text(f"₺{order.get('total_price', 0):.2f}")),
                        ft.DataCell(ft.Text(str(item_count))),
                        ft.DataCell(ft.Row([
                            ft.ElevatedButton(
                                "Onayla",
                                icon=ft.Icons.CHECK,
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.GREEN,
                                on_click=lambda e, order_id=order['id']: self.approve_order_simple(order_id)
                            ),
                            ft.ElevatedButton(
                                "Reddet",
                                icon=ft.Icons.CLOSE,
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.RED,
                                on_click=lambda e, order_id=order['id']: self.reject_order_simple(order_id)
                            ),
                        ], spacing=5))
                    ])
                )
            
            self.page.update()
            self.show_success(f"{len(recent_orders)} bekleyen sipariş yüklendi")
            
        except requests.exceptions.RequestException as ex:
            self.show_error(f"API'ye ulaşılamıyor: {ex}")
        except Exception as ex:
            self.show_error(f"Bekleyen sipariş yükleme hatası: {ex}")
    
    def approve_order_simple(self, order_id):
        """Siparişi onayla (basit versiyon)"""
        self.show_success(f"Sipariş #{order_id} onaylandı!")
        # Gerçek uygulamada burada sipariş durumu güncellenecek
        
    def reject_order_simple(self, order_id):
        """Siparişi reddet (basit versiyon)"""
        self.show_error(f"Sipariş #{order_id} reddedildi!")
        # Gerçek uygulamada burada sipariş durumu güncellenecek
    
    def show_preparation_manager(self, order_id):
        """Sipariş hazırlama yöneticisini göster"""
        try:
            print(f"Hazırlama yöneticisi açılıyor: {order_id}")
            
            # Sipariş detaylarını al
            response = requests.get(f"{API_URL}/orders/{order_id}", timeout=5, headers=self.get_headers())
            response.raise_for_status()
            order = response.json()
            
            # Sipariş durumu kontrolü
            if order.get('status') not in ['pending', 'preparing']:
                self.show_error("Bu sipariş artık hazırlama aşamasında değil!")
                return
            
            # Ürün listesi oluştur
            items_list = []
            print(f"Sipariş ürünleri: {order.get('items', [])}")  # Debug
            
            for item in order.get('items', []):
                try:
                    print(f"İşlenen ürün: {item}")  # Debug
                    
                    # Ürün bilgilerini al
                    product_response = requests.get(
                        f"{API_URL}/products/{item['product_id']}", 
                        timeout=5,
                        headers=self.get_headers()
                    )
                    if product_response.status_code == 200:
                        product = product_response.json()
                        product_name = product.get('name', f"Ürün #{item['product_id']}")
                        product_description = product.get('description', 'Açıklama yok')
                        product_unit = product.get('unit', 'adet')
                        print(f"Ürün bilgisi alındı: {product_name}")  # Debug
                    else:
                        product_name = f"Ürün #{item['product_id']}"
                        product_description = "Ürün bilgisi bulunamadı"
                        product_unit = "adet"
                        print(f"Ürün bilgisi alınamadı: {product_response.status_code}")  # Debug
                    
                    # Ürün hazırlık durumu ve notları
                    is_ready = item.get('preparation_status', False)
                    preparation_note = item.get('preparation_note', '')
                    cannot_prepare = item.get('cannot_prepare', False)
                    cannot_prepare_reason = item.get('cannot_prepare_reason', '')
                    
                    # Durum belirleme
                    if cannot_prepare:
                        status_text = "HAZIRLANAMAZ"
                        status_color = ft.Colors.RED
                    elif is_ready:
                        status_text = "HAZIR"
                        status_color = ft.Colors.GREEN
                    else:
                        status_text = "BEKLİYOR"
                        status_color = ft.Colors.ORANGE
                    
                    # Tüm durumlar için aynı buton
                    button_text = "İşlem Yap"
                    button_icon = ft.Icons.SETTINGS
                    button_color = ft.Colors.BLUE
                    
                    # Ürün kartı oluştur
                    item_card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                # Ürün bilgileri
                                ft.Column([
                                    ft.Text(product_name, weight=ft.FontWeight.BOLD, size=16),
                                    ft.Text(f"Miktar: {item['quantity']} {product_unit}", size=14, color=ft.Colors.GREY_600),
                                    ft.Text(f"Birim Fiyat: {item['price_per_item']:.2f} TL", size=12, color=ft.Colors.GREY_500),
                                    ft.Text(f"Toplam: {item['quantity'] * item['price_per_item']:.2f} TL", 
                                           size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600)
                                ], spacing=2, expand=True),
                                
                                # Hazırlık durumu ve butonlar
                                ft.Column([
                                    ft.Container(
                                        content=ft.Text(
                                            status_text,
                                            color=ft.Colors.WHITE,
                                            weight=ft.FontWeight.BOLD,
                                            size=12
                                        ),
                                        bgcolor=status_color,
                                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                        border_radius=15
                                    ),
                                    ft.ElevatedButton(
                                        button_text,
                                        icon=button_icon,
                                        bgcolor=button_color,
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, item_data=item: self.show_item_preparation_dialog(order_id, item_data)
                                    )
                                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            
                            # Notlar ve açıklamalar
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Açıklama: {product_description}", 
                                           size=12, color=ft.Colors.GREY_600, italic=True),
                                    ft.Text(f"Hazırlama Notu: {preparation_note}" if preparation_note else "", 
                                           size=12, color=ft.Colors.BLUE_600) if preparation_note else ft.Container(),
                                    ft.Text(f"Hazırlanamama Nedeni: {cannot_prepare_reason}", 
                                           size=12, color=ft.Colors.RED_600) if cannot_prepare_reason else ft.Container()
                                ], spacing=2),
                                padding=ft.padding.only(top=10),
                                visible=bool(product_description != 'Açıklama yok' or preparation_note or cannot_prepare_reason)
                            )
                        ], spacing=5),
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10,
                        padding=15,
                        margin=ft.margin.only(bottom=10)
                    )
                    items_list.append(item_card)
                    
                except Exception as e:
                    print(f"Ürün bilgisi alınamadı: {e}")
                    # Hata durumunda basit kart oluştur
                    error_card = ft.Container(
                        content=ft.Text(f"Ürün #{item.get('product_id', 'N/A')} - Bilgi alınamadı: {str(e)}", 
                                      color=ft.Colors.RED),
                        bgcolor=ft.Colors.RED_50,
                        border=ft.border.all(1, ft.Colors.RED_300),
                        border_radius=10,
                        padding=15,
                        margin=ft.margin.only(bottom=10)
                    )
                    items_list.append(error_card)
                    continue
            
            # Genel sipariş durumu
            ready_count = sum(1 for item in order.get('items', []) if item.get('preparation_status', False))
            total_count = len(order.get('items', []))
            
            # Modal içeriği
            modal_content = ft.Container(
                width=700,
                height=600,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=20,
                content=ft.Column([
                    # Başlık
                    ft.Row([
                        ft.Text(f"Sipariş #{order_id} - Hazırlama Yönetimi", 
                               size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            on_click=lambda e: self.close_modal()
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(),
                    
                    # Genel durum bilgisi
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Hazırlık Durumu: {ready_count}/{total_count} ürün hazır", 
                                   size=16, weight=ft.FontWeight.BOLD),
                            ft.ProgressBar(
                                value=ready_count / total_count if total_count > 0 else 0,
                                bgcolor=ft.Colors.GREY_300,
                                color=ft.Colors.GREEN
                            )
                        ], spacing=5),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=15,
                        border_radius=10,
                        margin=ft.margin.only(bottom=15)
                    ),
                    
                    # Ürün listesi
                    ft.Text("Ürünler:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.ListView(
                            controls=items_list,
                            spacing=0,
                            padding=ft.padding.all(10)
                        ),
                        height=350,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=10
                    ),
                    
                    # Alt butonlar
                    ft.Row([
                        ft.ElevatedButton(
                            "Tümünü Hazır İşaretle",
                            icon=ft.Icons.DONE_ALL,
                            bgcolor=ft.Colors.GREEN,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: self.mark_all_items_ready(order_id)
                        ),
                        ft.ElevatedButton(
                            "Siparişi Hazır Olarak İşaretle",
                            icon=ft.Icons.RESTAURANT,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: self.mark_order_ready(order_id),
                            disabled=ready_count < total_count
                        ),
                        ft.ElevatedButton(
                            "Kapat",
                            on_click=lambda e: self.close_modal()
                        )
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10, scroll=ft.ScrollMode.AUTO)
            )
            
            self._show_overlay_modal(modal_content)
            
        except Exception as e:
            self.show_error(f"Hazırlama yöneticisi açılırken hata: {e}")
    
    def show_item_preparation_dialog(self, order_id, item_data):
        """Ürün hazırlama durumu dialog'unu göster"""
        try:
            # Ürün bilgilerini al
            product_response = requests.get(
                f"{API_URL}/products/{item_data['product_id']}", 
                timeout=5,
                headers=self.get_headers()
            )
            if product_response.status_code == 200:
                product = product_response.json()
                product_name = product.get('name', f"Ürün #{item_data['product_id']}")
                product_unit = product.get('unit', 'adet')
            else:
                product_name = f"Ürün #{item_data['product_id']}"
                product_unit = "adet"
            
            # Mevcut durumlar
            is_ready = item_data.get('preparation_status', False)
            cannot_prepare = item_data.get('cannot_prepare', False)
            preparation_note = item_data.get('preparation_note', '')
            cannot_prepare_reason = item_data.get('cannot_prepare_reason', '')
            
            # Form alanları
            self.prep_note_field = ft.TextField(
                label="Hazırlama Notu",
                value=preparation_note,
                multiline=True,
                max_lines=3,
                hint_text="Özel talimatlar, notlar..."
            )
            
            self.cannot_prep_reason_field = ft.TextField(
                label="Hazırlanamama Nedeni",
                value=cannot_prepare_reason,
                multiline=True,
                max_lines=3,
                hint_text="Stok yok, malzeme eksik, vb..."
            )
            
            # Durum seçimi
            self.prep_status_radio = ft.RadioGroup(
                content=ft.Column([
                    ft.Radio(value="ready", label="Hazır"),
                    ft.Radio(value="waiting", label="Bekliyor"),
                    ft.Radio(value="cannot", label="Hazırlanamaz")
                ]),
                value="ready" if is_ready else ("cannot" if cannot_prepare else "waiting")
            )
            
            # Modal içeriği
            modal_content = ft.Container(
                width=500,
                bgcolor=ft.Colors.WHITE,
                border_radius=15,
                padding=20,
                content=ft.Column([
                    # Başlık
                    ft.Row([
                        ft.Text(f"Ürün Hazırlama: {product_name}", 
                               size=18, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            on_click=lambda e: self.close_modal()
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(),
                    
                    # Ürün bilgileri
                    ft.Container(
                        content=ft.Column([
                            ft.Text(f"Miktar: {item_data['quantity']} {product_unit}", size=14),
                            ft.Text(f"Birim Fiyat: {item_data['price_per_item']:.2f} TL", size=14),
                            ft.Text(f"Toplam: {item_data['quantity'] * item_data['price_per_item']:.2f} TL", 
                                   size=14, weight=ft.FontWeight.BOLD)
                        ], spacing=5),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=15,
                        border_radius=10,
                        margin=ft.margin.only(bottom=15)
                    ),
                    
                    # Durum seçimi
                    ft.Text("Hazırlama Durumu:", size=16, weight=ft.FontWeight.BOLD),
                    self.prep_status_radio,
                    
                    ft.Container(height=10),
                    
                    # Notlar
                    ft.Text("Hazırlama Notu:", size=14, weight=ft.FontWeight.BOLD),
                    self.prep_note_field,
                    
                    ft.Container(height=10),
                    
                    ft.Text("Hazırlanamama Nedeni:", size=14, weight=ft.FontWeight.BOLD),
                    self.cannot_prep_reason_field,
                    
                    ft.Container(height=20),
                    
                    # Butonlar
                    ft.Row([
                        ft.ElevatedButton(
                            "Kaydet",
                            icon=ft.Icons.SAVE,
                            bgcolor=ft.Colors.GREEN,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: self.save_item_preparation(order_id, item_data)
                        ),
                        ft.ElevatedButton(
                            "İptal",
                            on_click=lambda e: self.close_modal()
                        )
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10, scroll=ft.ScrollMode.AUTO)
            )
            
            self._show_overlay_modal(modal_content)
            
        except Exception as e:
            self.show_error(f"Ürün hazırlama dialog'u açılırken hata: {e}")
    
    def save_item_preparation(self, order_id, item_data):
        """Ürün hazırlama durumunu kaydet"""
        try:
            status = self.prep_status_radio.value
            note = self.prep_note_field.value.strip()
            cannot_reason = self.cannot_prep_reason_field.value.strip()
            
            # Durum kontrolü
            if status == "cannot" and not cannot_reason:
                self.show_error("Hazırlanamama nedeni belirtmelisiniz!")
                return
            
            # API'ye gönderilecek veri
            update_data = {
                "product_id": item_data['product_id'],
                "preparation_status": status == "ready",
                "cannot_prepare": status == "cannot",
                "preparation_note": note,
                "cannot_prepare_reason": cannot_reason if status == "cannot" else ""
            }
            
            # API'ye istek gönder
            try:
                response = requests.put(
                    f"{API_URL}/orders/{order_id}/items/{item_data['product_id']}/preparation", 
                    json=update_data, 
                    timeout=5,
                    headers=self.get_headers()
                )
                response.raise_for_status()
                
                self.show_success(f"Ürün hazırlık durumu güncellendi!")
                self.close_modal()
                
                # Sipariş detaylarını yenile
                if hasattr(self, 'order_items_table'):
                    self.page.run_thread(lambda: self.load_order_details(order_id))
                    
            except Exception as e:
                self.show_error(f"Hazırlık durumu güncellenirken hata: {e}")
                
        except Exception as e:
            self.show_error(f"Hata: {e}")
    
    def mark_order_ready(self, order_id):
        """Siparişi hazır olarak işaretle"""
        try:
            # Sipariş durumunu "ready" yap
            update_data = {
                "status": "ready"
            }
            
            response = requests.put(f"{API_URL}/orders/{order_id}", json=update_data, timeout=5, headers=self.get_headers())
            response.raise_for_status()
            
            self.show_success(f"Sipariş #{order_id} hazır olarak işaretlendi!")
            self.close_modal()
            
            # Sipariş listesini yenile
            if hasattr(self, 'orders_table'):
                self.page.run_thread(self.load_orders_data)
                
        except Exception as e:
            self.show_error(f"Sipariş durumu güncellenirken hata: {e}")


def main(page: ft.Page):
    AdminPanel(page)


if __name__ == "__main__":
    ft.app(target=main)
