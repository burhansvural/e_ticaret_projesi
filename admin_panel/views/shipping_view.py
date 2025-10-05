"""
Shipping and Logistics Views
"""

import flet as ft
from admin_panel.services import APIService


class ShippingCompaniesView:
    """Shipping companies management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build shipping companies UI"""
        # Companies table
        companies_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Kargo Firması", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İletişim", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Entegrasyon", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Kargo Firmaları", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Firma Ekle",
                    icon=ft.Icons.ADD,
                    on_click=self.add_company
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=companies_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load shipping companies data"""
        pass
    
    def add_company(self, e):
        """Add new shipping company"""
        self.notification_manager.show_info("Kargo firması ekleme özelliği yakında eklenecek")


class ShipmentTrackingView:
    """Shipment tracking view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build shipment tracking UI"""
        # Search field
        search_field = ft.TextField(
            label="Takip Numarası veya Sipariş No",
            prefix_icon=ft.Icons.SEARCH,
            width=400,
        )
        
        # Shipments table
        shipments_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sipariş No", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Takip No", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Kargo Firması", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tahmini Teslimat", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Text("Kargo Takip", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Row([
                search_field,
                ft.ElevatedButton("Ara", icon=ft.Icons.SEARCH),
            ], spacing=10),
            ft.Container(height=20),
            ft.Container(
                content=shipments_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load shipment tracking data"""
        pass


class DeliveryZonesView:
    """Delivery zones management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build delivery zones UI"""
        # Zones table
        zones_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Bölge Adı", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İller", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Teslimat Süresi", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Kargo Ücreti", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Teslimat Bölgeleri", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Bölge",
                    icon=ft.Icons.ADD,
                    on_click=self.add_zone
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=zones_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load delivery zones data"""
        pass
    
    def add_zone(self, e):
        """Add new delivery zone"""
        self.notification_manager.show_info("Teslimat bölgesi ekleme özelliği yakında eklenecek")