"""
Settings Views
"""

import flet as ft
from admin_panel.services import APIService


class GeneralSettingsView:
    """General settings view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build general settings UI"""
        # Store information
        store_info = ft.Container(
            content=ft.Column([
                ft.Text("Mağaza Bilgileri", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.TextField(label="Mağaza Adı", value="E-Ticaret Mağazası"),
                ft.TextField(label="E-posta", value="info@eticaret.com"),
                ft.TextField(label="Telefon", value="+90 555 123 4567"),
                ft.TextField(label="Adres", multiline=True, min_lines=3),
            ], spacing=10),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
        )
        
        # Business hours
        business_hours = ft.Container(
            content=ft.Column([
                ft.Text("Çalışma Saatleri", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.TextField(label="Hafta İçi", value="09:00 - 18:00"),
                ft.TextField(label="Hafta Sonu", value="10:00 - 16:00"),
            ], spacing=10),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
        )
        
        return ft.Column([
            ft.Text("Genel Ayarlar", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            store_info,
            ft.Container(height=20),
            business_hours,
            ft.Container(height=20),
            ft.ElevatedButton(
                "Kaydet",
                icon=ft.Icons.SAVE,
                on_click=self.save_settings
            ),
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load settings data"""
        pass
    
    def save_settings(self, e):
        """Save settings"""
        self.notification_manager.show_success("Ayarlar kaydedildi")


class UserManagementView:
    """User management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build user management UI"""
        # Users table
        users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Kullanıcı Adı", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("E-posta", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Rol", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Son Giriş", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Kullanıcı Yönetimi", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Kullanıcı",
                    icon=ft.Icons.PERSON_ADD,
                    on_click=self.add_user
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=users_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load users data"""
        pass
    
    def add_user(self, e):
        """Add new user"""
        self.notification_manager.show_info("Kullanıcı ekleme özelliği yakında eklenecek")


class NotificationsSettingsView:
    """Notifications settings view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build notifications settings UI"""
        # Email notifications
        email_settings = ft.Container(
            content=ft.Column([
                ft.Text("E-posta Bildirimleri", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Checkbox(label="Yeni sipariş bildirimi", value=True),
                ft.Checkbox(label="Düşük stok uyarısı", value=True),
                ft.Checkbox(label="Yeni müşteri kaydı", value=False),
                ft.Checkbox(label="Ürün yorumu", value=True),
            ], spacing=10),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
        )
        
        # SMS notifications
        sms_settings = ft.Container(
            content=ft.Column([
                ft.Text("SMS Bildirimleri", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Checkbox(label="Acil siparişler", value=True),
                ft.Checkbox(label="Sistem uyarıları", value=True),
            ], spacing=10),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
        )
        
        return ft.Column([
            ft.Text("Bildirim Ayarları", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            email_settings,
            ft.Container(height=20),
            sms_settings,
            ft.Container(height=20),
            ft.ElevatedButton(
                "Kaydet",
                icon=ft.Icons.SAVE,
                on_click=self.save_settings
            ),
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load notifications settings"""
        pass
    
    def save_settings(self, e):
        """Save settings"""
        self.notification_manager.show_success("Bildirim ayarları kaydedildi")


class SystemLogsView:
    """System logs view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build system logs UI"""
        # Logs table
        logs_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tarih/Saat", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Seviye", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Kullanıcı", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlem", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Detay", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        # Filters
        filters = ft.Row([
            ft.Dropdown(
                label="Seviye",
                width=150,
                options=[
                    ft.dropdown.Option("all", "Tümü"),
                    ft.dropdown.Option("info", "Bilgi"),
                    ft.dropdown.Option("warning", "Uyarı"),
                    ft.dropdown.Option("error", "Hata"),
                ],
                value="all"
            ),
            ft.TextField(label="Tarih", width=200),
            ft.ElevatedButton("Filtrele", icon=ft.Icons.FILTER_LIST),
            ft.Container(expand=True),
            ft.ElevatedButton("Dışa Aktar", icon=ft.Icons.DOWNLOAD),
        ], spacing=10)
        
        return ft.Column([
            ft.Text("Sistem Logları", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            filters,
            ft.Container(height=20),
            ft.Container(
                content=logs_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load system logs"""
        pass