# frontend/src/views/auth_view.py
import flet as ft
import requests

API_URL = "http://127.0.0.1:8000"

class AuthView(ft.View):
    def __init__(self, app):
        super().__init__()
        self.error_dialog_ref = None
        self.home_button = None
        self.switch_mode_button = None
        self.main_button = None
        self.form_container = None
        self.subtitle_text = None
        self.title_text = None
        self.app = app
        self.route = "/auth"
        self.padding = 20
        self.bgcolor = ft.Colors.GREY_50
        
        # Form alanları
        self.email_field = ft.TextField(
            label="E-posta",
            prefix_icon=ft.Icons.EMAIL,
            width=350,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Şifre",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=350,
            on_change=self.on_password_change
        )
        
        self.confirm_password_field = ft.TextField(
            label="Şifre Tekrar",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            width=350,
            on_change=self.on_confirm_password_change
        )
        
        # Şifre güçlülük göstergesi
        self.password_strength_bar = ft.ProgressBar(
            width=350,
            height=4,
            value=0,
            color=ft.Colors.RED,
            visible=False
        )
        
        self.password_strength_text = ft.Text(
            "",
            size=12,
            color=ft.Colors.GREY_600,
            visible=False
        )
        
        self.first_name_field = ft.TextField(
            label="Ad",
            prefix_icon=ft.Icons.PERSON,
            width=350
        )
        
        self.last_name_field = ft.TextField(
            label="Soyad",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            width=350
        )
        
        self.phone_field = ft.TextField(
            label="Telefon (Opsiyonel)",
            prefix_icon=ft.Icons.PHONE,
            width=350
        )
        
        self.address_field = ft.TextField(
            label="Adres (Opsiyonel)",
            prefix_icon=ft.Icons.HOME,
            width=350,
            multiline=True,
            min_lines=2,
            max_lines=3
        )
        
        # Durum yönetimi
        self.is_login_mode = True
        self.loading = False
        
        # UI bileşenleri
        self.create_ui()

    
    def create_ui(self):
        """UI bileşenlerini oluştur"""
        # Başlık
        self.title_text = ft.Text(
            "Giriş Yap",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_900
        )
        
        # Alt başlık
        self.subtitle_text = ft.Text(
            "Hesabınıza giriş yapın",
            size=16,
            color=ft.Colors.GREY_600
        )
        
        # Form konteyner
        self.form_container = ft.Container(
            content=ft.Column([
                self.email_field,
                self.password_field,
            ], spacing=15),
            padding=30,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 5)
            )
        )
        
        # Ana buton
        self.main_button = ft.ElevatedButton(
            "Giriş Yap",
            icon=ft.Icons.LOGIN,
            width=350,
            height=50,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD)
            ),
            on_click=self.handle_auth
        )
        
        # Mod değiştirme butonu
        self.switch_mode_button = ft.TextButton(
            "Hesabınız yok mu? Kayıt olun",
            on_click=self.switch_mode
        )
        
        # Ana sayfa butonu
        self.home_button = ft.TextButton(
            "← Ana Sayfaya Dön",
            on_click=lambda e: self.app.page.go("/")
        )
        
        # Ana layout
        self.controls = [
            ft.Container(
                content=ft.Column([
                    # Header
                    ft.Container(
                        content=ft.Row([
                            self.home_button,
                        ], alignment=ft.MainAxisAlignment.START),
                        margin=ft.margin.only(bottom=20)
                    ),
                    
                    # Ana içerik
                    ft.Container(
                        content=ft.Column([
                            # Logo ve başlık
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(
                                        ft.Icons.SHOPPING_BAG,
                                        size=60,
                                        color=ft.Colors.BLUE_600
                                    ),
                                    self.title_text,
                                    self.subtitle_text,
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                                margin=ft.margin.only(bottom=30)
                            ),
                            
                            # Form
                            self.form_container,
                            
                            # Butonlar
                            ft.Container(
                                content=ft.Column([
                                    self.main_button,
                                    self.switch_mode_button,
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                                margin=ft.margin.only(top=20)
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=True
                    )
                ], spacing=0),
                expand=True,
                alignment=ft.alignment.center
            )
        ]
    
    def switch_mode(self, e):
        """Giriş/Kayıt modları arasında geçiş yap"""
        self.is_login_mode = not self.is_login_mode
        
        if self.is_login_mode:
            # Giriş moduna geç
            self.title_text.value = "Giriş Yap"
            self.subtitle_text.value = "Hesabınıza giriş yapın"
            self.main_button.text = "Giriş Yap"
            self.main_button.icon = ft.Icons.LOGIN
            self.switch_mode_button.text = "Hesabınız yok mu? Kayıt olun"
            
            # Kayıt alanlarını gizle
            self.form_container.content.controls = [
                self.email_field,
                self.password_field,
            ]
            
            # Şifre güçlülük göstergelerini gizle
            self.password_strength_bar.visible = False
            self.password_strength_text.visible = False
        else:
            # Kayıt moduna geç
            self.title_text.value = "Kayıt Ol"
            self.subtitle_text.value = "Yeni hesap oluşturun"
            self.main_button.text = "Kayıt Ol"
            self.main_button.icon = ft.Icons.PERSON_ADD
            self.switch_mode_button.text = "Zaten hesabınız var mı? Giriş yapın"
            
            # Kayıt alanlarını göster
            self.form_container.content.controls = [
                self.first_name_field,
                self.last_name_field,
                self.email_field,
                self.password_field,
                self.password_strength_bar,
                self.password_strength_text,
                self.confirm_password_field,
                self.phone_field,
                self.address_field,
            ]
            
            # Şifre güçlülük göstergelerini göster
            self.password_strength_bar.visible = True
            self.password_strength_text.visible = True
        
        # Alanları temizle
        self.clear_fields()
        self.app.page.update()
    
    def clear_fields(self):
        """Form alanlarını temizle"""
        self.email_field.value = ""
        self.password_field.value = ""
        self.confirm_password_field.value = ""
        self.first_name_field.value = ""
        self.last_name_field.value = ""
        self.phone_field.value = ""
        self.address_field.value = ""
        self.email_field.error_text = None
        self.password_field.error_text = None
        self.confirm_password_field.error_text = None
        self.first_name_field.error_text = None
        self.last_name_field.error_text = None
        
        # Şifre güçlülük göstergesini sıfırla
        self.password_strength_bar.value = 0
        self.password_strength_bar.color = ft.Colors.RED
        self.password_strength_text.value = ""
    
    def validate_fields(self):
        """Form alanlarını doğrula"""
        is_valid = True
        
        # E-posta kontrolü
        if not self.email_field.value or "@" not in self.email_field.value:
            self.email_field.error_text = "Geçerli bir e-posta adresi girin"
            is_valid = False
        else:
            self.email_field.error_text = None
        
        # Şifre kontrolü
        if not self.password_field.value:
            self.password_field.error_text = "Şifre gerekli"
            is_valid = False
        elif len(self.password_field.value) < 8:
            self.password_field.error_text = "Şifre en az 8 karakter olmalı"
            is_valid = False
        elif not self.is_login_mode and not self.validate_password_strength(self.password_field.value):
            self.password_field.error_text = "Şifre en az 1 büyük harf, 1 küçük harf ve 1 rakam içermeli"
            is_valid = False
        else:
            self.password_field.error_text = None
        
        # Kayıt modunda ad soyad ve şifre doğrulama kontrolü
        if not self.is_login_mode:
            if not self.first_name_field.value or len(self.first_name_field.value.strip()) < 2:
                self.first_name_field.error_text = "Ad en az 2 karakter olmalı"
                is_valid = False
            else:
                self.first_name_field.error_text = None
                
            if not self.last_name_field.value or len(self.last_name_field.value.strip()) < 2:
                self.last_name_field.error_text = "Soyad en az 2 karakter olmalı"
                is_valid = False
            else:
                self.last_name_field.error_text = None
            
            # Şifre doğrulama kontrolü
            if not self.confirm_password_field.value:
                self.confirm_password_field.error_text = "Şifre tekrarını girin"
                is_valid = False
            elif self.password_field.value != self.confirm_password_field.value:
                self.confirm_password_field.error_text = "Şifreler eşleşmiyor"
                is_valid = False
            else:
                self.confirm_password_field.error_text = None
        
        return is_valid
    
    def validate_password_strength(self, password):
        """Şifre güçlülüğünü kontrol et"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit
    
    def calculate_password_strength(self, password):
        """Şifre güçlülüğünü hesapla (0-1 arası)"""
        if not password:
            return 0, "Şifre girin", ft.Colors.RED
        
        score = 0
        feedback = []
        
        # Uzunluk kontrolü
        if len(password) >= 8:
            score += 0.25
        else:
            feedback.append("en az 8 karakter")
        
        # Büyük harf kontrolü
        if any(c.isupper() for c in password):
            score += 0.25
        else:
            feedback.append("büyük harf")
        
        # Küçük harf kontrolü
        if any(c.islower() for c in password):
            score += 0.25
        else:
            feedback.append("küçük harf")
        
        # Rakam kontrolü
        if any(c.isdigit() for c in password):
            score += 0.25
        else:
            feedback.append("rakam")
        
        # Özel karakter bonusu
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score = min(1.0, score + 0.1)
        
        # Mesaj ve renk belirleme
        if score < 0.3:
            message = "Zayıf şifre"
            color = ft.Colors.RED
        elif score < 0.6:
            message = "Orta güçlülük"
            color = ft.Colors.ORANGE
        elif score < 0.8:
            message = "İyi şifre"
            color = ft.Colors.YELLOW
        else:
            message = "Güçlü şifre"
            color = ft.Colors.GREEN
        
        if feedback:
            message += f" (Eksik: {', '.join(feedback)})"
        
        return score, message, color
    
    def on_password_change(self, e):
        """Şifre değiştiğinde gerçek zamanlı doğrulama"""
        if not self.is_login_mode:
            # Şifre güçlülük göstergesini güncelle
            score, message, color = self.calculate_password_strength(self.password_field.value)
            self.password_strength_bar.value = score
            self.password_strength_bar.color = color
            self.password_strength_text.value = message
            self.password_strength_text.color = color
            
            # Hata mesajını güncelle
            if self.password_field.value:
                if len(self.password_field.value) < 8:
                    self.password_field.error_text = "Şifre en az 8 karakter olmalı"
                elif not self.validate_password_strength(self.password_field.value):
                    self.password_field.error_text = "Şifre en az 1 büyük harf, 1 küçük harf ve 1 rakam içermeli"
                else:
                    self.password_field.error_text = None
            else:
                self.password_field.error_text = None
            
            # Şifre tekrar alanını da kontrol et
            if self.confirm_password_field.value:
                self.on_confirm_password_change(None)
            
            self.app.page.update()
    
    def on_confirm_password_change(self, e):
        """Şifre tekrar değiştiğinde gerçek zamanlı doğrulama"""
        if not self.is_login_mode and self.confirm_password_field.value:
            if self.password_field.value != self.confirm_password_field.value:
                self.confirm_password_field.error_text = "Şifreler eşleşmiyor"
            else:
                self.confirm_password_field.error_text = None
            
            self.app.page.update()

    def show_error(self, message):
        """Hata mesajı göster"""

        # Hata mesajını password field'ın altında göster
        self.password_field.error_text = message
        self.password_field.update()


    def handle_auth(self, e):
        """Giriş/Kayıt işlemini gerçekleştir"""
        if self.loading:
            return
        
        if not self.validate_fields():
            self.app.page.update()
            return
        
        self.loading = True
        self.main_button.disabled = True
        self.main_button.text = "İşleniyor..."
        self.app.page.update()
        
        try:
            if self.is_login_mode:
                self.handle_login()
            else:
                self.handle_register()
        except Exception as ex:
            self.show_error(f"Beklenmeyen hata: {str(ex)}")
        finally:
            self.loading = False
            self.main_button.disabled = False
            self.main_button.text = "Giriş Yap" if self.is_login_mode else "Kayıt Ol"
            self.app.page.update()
    
    def handle_login(self):
        """Giriş işlemi"""
        try:
            print(f"DEBUG: Login isteği gönderiliyor - email: {self.email_field.value}")
            response = requests.post(
                f"{API_URL}/users/login",
                json={
                    "email": self.email_field.value,
                    "password": self.password_field.value
                },
                timeout=10
            )
            
            print(f"DEBUG: Response status code: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                user = data["user"]
                
                # Ad soyad birleştir
                full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                if not full_name:
                    full_name = user.get('email', 'Kullanıcı')
                
                # Kullanıcı bilgilerini sakla (full_name alanı ile birlikte)
                user['full_name'] = full_name
                self.app.current_user = user
                
                self.show_success(f"Hoş geldiniz, {full_name}!")
                
                # Ana sayfaya yönlendir ve sayfayı yenile
                self.app.page.go("/")
                # Ana sayfayı yeniden yükle
                self.app.route_change("/")
            else:
                error_data = response.json()
                error_message = error_data.get("detail", "Giriş başarısız")
                print(f"DEBUG: Hata mesajı: {error_message}")
                # Şifreyi temizle ama email'i bırak
                self.password_field.value = ""
                self.show_error(error_message)
                
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Request exception: {e}")
            self.show_error("Sunucuya bağlanılamıyor. Lütfen daha sonra tekrar deneyin.")
    
    def handle_register(self):
        """Kayıt işlemi"""
        try:
            response = requests.post(
                f"{API_URL}/users/register",
                json={
                    "email": self.email_field.value,
                    "password": self.password_field.value,
                    "first_name": self.first_name_field.value,
                    "last_name": self.last_name_field.value,
                    "phone": self.phone_field.value or None,
                    "address": self.address_field.value or None
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Kullanıcıyı email doğrulama sayfasına yönlendir
                user_email = self.email_field.value
                self.app.page.go(f"/verify-email?email={user_email}")
                
                # Kayıt formunu temizle
                self.clear_register_form()
            else:
                error_data = response.json()
                self.show_error(error_data.get("detail", "Kayıt başarısız"))
                
        except requests.exceptions.RequestException:
            self.show_error("Sunucuya bağlanılamıyor. Lütfen daha sonra tekrar deneyin.")
    
    def clear_register_form(self):
        """Kayıt formunu temizle"""
        self.email_field.value = ""
        self.password_field.value = ""
        self.confirm_password_field.value = ""
        self.first_name_field.value = ""
        self.last_name_field.value = ""
        self.phone_field.value = ""
        self.address_field.value = ""
        self.app.page.update()
    
    def show_success(self, message):
        """Başarı mesajı göster (DÜZELTİLDİ)"""
        page = self.app.page

        # Sadece içeriği ve durumu değiştir
        page.snack_bar.content = ft.Text(message, color=ft.Colors.WHITE)
        page.snack_bar.bgcolor = ft.Colors.GREEN
        page.snack_bar.open = True
        page.snack_bar.duration = 5000

        self.app.page.update()
    
