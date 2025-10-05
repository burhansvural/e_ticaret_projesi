"""
Marketing Views
"""

import flet as ft
from admin_panel.services import APIService


class CampaignsView:
    """Campaigns management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
        self.campaigns = []
    
    def build(self) -> ft.Control:
        """Build campaigns UI"""
        # Campaigns list
        campaigns_list = ft.ListView(
            spacing=10,
            padding=20,
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Kampanyalar", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Kampanya",
                    icon=ft.Icons.ADD,
                    on_click=self.create_campaign
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=campaigns_list,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load campaigns data"""
        self.notification_manager.show_info("Kampanyalar yükleniyor...")
    
    def create_campaign(self, e):
        """Create new campaign"""
        self.notification_manager.show_info("Yeni kampanya oluşturma özelliği yakında eklenecek")


class CouponsView:
    """Coupons management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build coupons UI"""
        # Coupons table
        coupons_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Kupon Kodu", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İndirim", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Geçerlilik", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Kullanım", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("İndirim Kuponları", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Kupon",
                    icon=ft.Icons.ADD,
                    on_click=self.create_coupon
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=coupons_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load coupons data"""
        pass
    
    def create_coupon(self, e):
        """Create new coupon"""
        self.notification_manager.show_info("Yeni kupon oluşturma özelliği yakında eklenecek")


class EmailMarketingView:
    """Email marketing view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build email marketing UI"""
        # Email campaigns list
        campaigns_list = ft.ListView(spacing=10)
        
        return ft.Column([
            ft.Row([
                ft.Text("E-posta Pazarlama", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Kampanya",
                    icon=ft.Icons.EMAIL,
                    on_click=self.create_email_campaign
                ),
            ]),
            ft.Container(height=20),
            ft.Row([
                self._create_stat_card("Gönderilen", "0", ft.Colors.BLUE),
                self._create_stat_card("Açılma Oranı", "%0", ft.Colors.GREEN),
                self._create_stat_card("Tıklama Oranı", "%0", ft.Colors.ORANGE),
            ], spacing=20),
            ft.Container(height=20),
            ft.Container(
                content=campaigns_list,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_stat_card(self, title: str, value: str, color) -> ft.Container:
        """Create stat card"""
        return ft.Container(
            content=ft.Column([
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(title, size=14, color=ft.Colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            width=200,
        )
    
    def load_data(self):
        """Load email marketing data"""
        pass
    
    def create_email_campaign(self, e):
        """Create new email campaign"""
        self.notification_manager.show_info("E-posta kampanyası oluşturma özelliği yakında eklenecek")