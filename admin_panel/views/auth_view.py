
"""
Authentication View - Login, Register, Email Verification
"""

import flet as ft
from typing import Callable

from admin_panel.services import AuthService


class AuthView:
    """Handles authentication UI (login, register, verification)"""
    
    def __init__(self, page: ft.Page, auth_service: AuthService, on_login_success: Callable = None, 
                 notification_manager=None, on_success: Callable = None):
        self.page = page
        self.auth_service = auth_service
        # Support both parameter names for backward compatibility
        self.on_success = on_login_success or on_success
        self.notification_manager = notification_manager
        self.show_register_form = False
        self.verify_email = None
    
    def show_login(self):
        """Show login screen"""
        if self.show_register_form:
            self.show_register()
            return
        
        email_field = ft.TextField(
            label="E-posta",
            width=300,
            prefix_icon=ft.Icons.EMAIL,
            autofocus=True
        )
        
        password_field = ft.TextField(
            label="Şifre",
            width=300,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True
        )
        
        def do_login(e):
            email = email_field.value
            password = password_field.value
            
            if not email or not password:
                self._show_error("E-posta ve şifre gereklidir!")
                return
            
            try:
                data = self.auth_service.login(email, password)
                self.on_success(data)
            except Exception as ex:
                self._show_error(f"Giriş hatası: {ex}")
        
        password_field.on_submit = do_login
        
        login_button = ft.ElevatedButton(
            "Giriş Yap",
            width=300,
            height=50,
            on_click=do_login,
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
                email_field,
                password_field,
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
        """Toggle between login and register forms"""
        self.show_register_form = not self.show_register_form
        self.show_login()
    
    def show_register(self):
        """Show registration screen"""
        first_name_field = ft.TextField(
            label="Ad",
            width=300,
            prefix_icon=ft.Icons.PERSON,
            autofocus=True
        )
        
        last_name_field = ft.TextField(
            label="Soyad",
            width=300,
            prefix_icon=ft.Icons.PERSON_OUTLINE
        )
        
        email_field = ft.TextField(
            label="E-posta",
            width=300,
            prefix_icon=ft.Icons.EMAIL
        )
        
        phone_field = ft.TextField(
            label="Telefon (Opsiyonel)",
            width=300,
            prefix_icon=ft.Icons.PHONE
        )
        
        password_field = ft.TextField(
            label="Şifre",
            width=300,
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True
        )
        
        password_confirm_field = ft.TextField(
            label="Şifre Tekrar",
            width=300,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True
        )
        
        is_admin_checkbox = ft.Checkbox(
            label="Admin Yetkisi",
            value=True
        )
        
        def do_register(e):
            first_name = first_name_field.value
            last_name = last_name_field.value
            email = email_field.value
            phone = phone_field.value
            password = password_field.value
            password_confirm = password_confirm_field.value
            is_admin = is_admin_checkbox.value
            
            # Validation
            if not all([first_name, last_name, email, password, password_confirm]):
                self._show_error("Lütfen tüm zorunlu alanları doldurun!")
                return
            
            if password != password_confirm:
                self._show_error("Şifreler eşleşmiyor!")
                return
            
            if len(password) < 8:
                self._show_error("Şifre en az 8 karakter olmalıdır!")
                return
            
            try:
                user_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone": phone if phone else None,
                    "password": password,
                    "is_admin": is_admin
                }
                self.auth_service.register(user_data)
                self._show_success("Kayıt başarılı! E-posta doğrulama kodu gönderildi.")
                self.show_verification_screen(email)
            except Exception as ex:
                self._show_error(f"Kayıt hatası: {ex}")
        
        password_confirm_field.on_submit = do_register
        
        register_button = ft.ElevatedButton(
            "Kayıt Ol",
            width=300,
            height=50,
            on_click=do_register,
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
                first_name_field,
                last_name_field,
                email_field,
                phone_field,
                password_field,
                password_confirm_field,
                ft.Container(
                    content=is_admin_checkbox,
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
    
    def show_verification_screen(self, email: str):
        """Show email verification screen"""
        self.verify_email = email
        
        code_field = ft.TextField(
            label="Doğrulama Kodu",
            width=300,
            prefix_icon=ft.Icons.VERIFIED_USER,
            autofocus=True
        )
        
        def do_verify(e):
            code = code_field.value
            
            if not code:
                self._show_error("Lütfen doğrulama kodunu girin!")
                return
            
            try:
                self.auth_service.verify_email(self.verify_email, code)
                self._show_success("E-posta doğrulandı! Şimdi giriş yapabilirsiniz.")
                self.back_to_login()
            except Exception as ex:
                self._show_error(f"Doğrulama hatası: {ex}")
        
        code_field.on_submit = do_verify
        
        verify_button = ft.ElevatedButton(
            "Doğrula",
            width=300,
            height=50,
            on_click=do_verify,
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
                code_field,
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
    
    def back_to_login(self):
        """Go back to login screen"""
        self.show_register_form = False
        self.show_login()
    
    def _show_success(self, message: str):
        """Show success notification"""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.GREEN
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()
    
    def _show_error(self, message: str):
        """Show error notification"""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.RED
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()