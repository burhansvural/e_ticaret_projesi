import flet as ft
import requests
from urllib.parse import parse_qs

API_URL = "http://127.0.0.1:8000"


class EmailVerificationView:
    def __init__(self, app):
        self.app = app
        self.email = None
        self.code_fields = []
        
    def build(self):
        """E-mail doğrulama sayfası - 6 haneli kod girişi"""
        # URL'den email parametresini al
        self.email = self.get_email_from_url()
        
        # 6 haneli kod giriş alanları
        self.code_fields = [
            ft.TextField(
                width=50,
                height=60,
                text_align=ft.TextAlign.CENTER,
                text_size=24,
                max_length=1,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=lambda e, idx=i: self.on_code_change(e, idx),
                border_color=ft.Colors.BLUE_200,
                focused_border_color=ft.Colors.BLUE,
            )
            for i in range(6)
        ]
        
        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.BLUE_50, ft.Colors.BLUE_100]
            ),
            content=ft.Column([
                ft.Container(height=50),
                
                # Logo ve başlık
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.MARK_EMAIL_READ, size=80, color=ft.Colors.BLUE),
                        ft.Text("E-mail Doğrulama", size=32, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            f"E-mail adresinize gönderilen 6 haneli kodu girin",
                            size=16,
                            color=ft.Colors.GREY_600,
                            text_align=ft.TextAlign.CENTER
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    alignment=ft.alignment.center
                ),
                
                ft.Container(height=30),
                
                # Doğrulama kartı
                ft.Container(
                    width=500,
                    padding=30,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 5)
                    ),
                    content=ft.Column([
                        # E-mail bilgisi
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.EMAIL, size=20, color=ft.Colors.BLUE),
                                ft.Text(
                                    self.email or "E-mail adresi bulunamadı",
                                    size=14,
                                    color=ft.Colors.GREY_700,
                                    weight=ft.FontWeight.BOLD
                                )
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                            padding=10,
                            bgcolor=ft.Colors.BLUE_50,
                            border_radius=10
                        ),
                        
                        ft.Container(height=20),
                        
                        # 6 haneli kod giriş alanları
                        ft.Row(
                            self.code_fields,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        ),
                        
                        ft.Container(height=20),
                        
                        # Doğrula butonu
                        ft.ElevatedButton(
                            "Doğrula",
                            icon=ft.Icons.CHECK_CIRCLE,
                            on_click=self.verify_code,
                            width=200,
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE,
                                padding=ft.padding.symmetric(horizontal=30, vertical=15)
                            )
                        ),
                        
                        ft.Container(height=10),
                        
                        # Yeniden gönder butonu
                        ft.TextButton(
                            "Kodu almadınız mı? Yeniden gönder",
                            icon=ft.Icons.REFRESH,
                            on_click=self.resend_verification_code,
                            style=ft.ButtonStyle(
                                color=ft.Colors.ORANGE
                            )
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                    alignment=ft.alignment.center
                ),
                
                ft.Container(height=30),
                
                # Geri dön butonu
                ft.Row([
                    ft.ElevatedButton(
                        "Giriş Sayfasına Dön",
                        icon=ft.Icons.LOGIN,
                        on_click=lambda e: self.app.page.go("/auth"),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREY_400,
                            color=ft.Colors.WHITE,
                            padding=ft.padding.symmetric(horizontal=30, vertical=15)
                        )
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def get_email_from_url(self):
        """URL'den email parametresini çıkar"""
        try:
            route = self.app.page.route
            if "?email=" in route:
                email = route.split("?email=")[1].split("&")[0]
                # URL encoding'i çöz
                from urllib.parse import unquote
                return unquote(email)
            return None
        except:
            return None
    
    def on_code_change(self, e, index):
        """Kod değiştiğinde otomatik olarak bir sonraki alana geç"""
        if e.control.value and len(e.control.value) == 1:
            # Bir sonraki alana odaklan
            if index < 5:
                self.code_fields[index + 1].focus()
        self.app.page.update()
    
    def verify_code(self, e):
        """Doğrulama kodunu kontrol et"""
        # 6 haneli kodu birleştir
        code = "".join([field.value or "" for field in self.code_fields])
        
        if len(code) != 6:
            self.show_error("Lütfen 6 haneli kodu tam olarak girin")
            return
        
        if not self.email:
            self.show_error("E-mail adresi bulunamadı. Lütfen kayıt işlemini tekrar yapın.")
            return
        
        try:
            response = requests.post(
                f"{API_URL}/users/verify-email",
                json={
                    "email": self.email,
                    "code": code
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.show_success("✅ E-mail adresiniz başarıyla doğrulandı! Giriş sayfasına yönlendiriliyorsunuz...")
                # 2 saniye sonra giriş sayfasına yönlendir
                import time
                time.sleep(2)
                self.app.page.go("/auth")
            else:
                error_data = response.json()
                self.show_error(error_data.get("detail", "Doğrulama başarısız. Lütfen kodu kontrol edin."))
                # Kod alanlarını temizle
                for field in self.code_fields:
                    field.value = ""
                self.code_fields[0].focus()
                self.app.page.update()
                
        except requests.exceptions.RequestException as ex:
            self.show_error(f"Sunucuya bağlanılamıyor: {str(ex)}")
    
    def resend_verification_code(self, e):
        """Doğrulama kodunu yeniden gönder"""
        if not self.email:
            self.show_error("E-mail adresi bulunamadı")
            return
        
        try:
            response = requests.post(
                f"{API_URL}/resend-verification",
                params={"email": self.email},
                timeout=10
            )
            
            if response.status_code == 200:
                self.show_success("✅ Yeni doğrulama kodu e-mail adresinize gönderildi!")
                # Kod alanlarını temizle
                for field in self.code_fields:
                    field.value = ""
                self.code_fields[0].focus()
                self.app.page.update()
            else:
                error_data = response.json()
                self.show_error(error_data.get("detail", "Kod gönderilemedi"))
                
        except requests.exceptions.RequestException as ex:
            self.show_error(f"Sunucuya bağlanılamıyor: {str(ex)}")
    
    def show_success(self, message):
        """Başarı mesajı göster"""
        page = self.app.page
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()
    
    def show_error(self, message):
        """Hata mesajı göster"""
        page = self.app.page
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()