"""
Reports and Analytics Views
"""

import flet as ft
from admin_panel.services import APIService
from datetime import datetime, timedelta


class SalesReportsView:
    """Sales reports view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build sales reports UI"""
        # Date range selector
        date_range = ft.Row([
            ft.TextField(
                label="Başlangıç Tarihi",
                value=datetime.now().strftime("%Y-%m-%d"),
                width=200
            ),
            ft.TextField(
                label="Bitiş Tarihi",
                value=datetime.now().strftime("%Y-%m-%d"),
                width=200
            ),
            ft.ElevatedButton("Rapor Oluştur", icon=ft.Icons.ANALYTICS),
        ], spacing=10)
        
        # Summary cards
        summary_cards = ft.Row([
            self._create_summary_card("Toplam Satış", "₺0", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN),
            self._create_summary_card("Sipariş Sayısı", "0", ft.Icons.SHOPPING_CART, ft.Colors.BLUE),
            self._create_summary_card("Ortalama Sepet", "₺0", ft.Icons.SHOPPING_BAG, ft.Colors.ORANGE),
            self._create_summary_card("İptal Oranı", "%0", ft.Icons.CANCEL, ft.Colors.RED),
        ], spacing=20, wrap=True)
        
        # Chart placeholder
        chart_container = ft.Container(
            content=ft.Column([
                ft.Text("Satış Grafiği", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Container(
                    content=ft.Text("Grafik burada görüntülenecek", color=ft.Colors.GREY_600),
                    height=300,
                    alignment=ft.alignment.center
                )
            ]),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            expand=True
        )
        
        return ft.Column([
            ft.Text("Satış Raporları", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            date_range,
            ft.Container(height=20),
            summary_cards,
            ft.Container(height=20),
            chart_container,
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_summary_card(self, title: str, value: str, icon, color) -> ft.Container:
        """Create summary card"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=40, color=color),
                    ft.Column([
                        ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(title, size=14, color=ft.Colors.GREY_600)
                    ], spacing=0)
                ], spacing=15)
            ]),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            width=250,
        )
    
    def load_data(self):
        """Load sales data"""
        try:
            # Load sales data from API
            pass
        except Exception as e:
            self.notification_manager.show_error(f"Veri yükleme hatası: {e}")


class ProductPerformanceView:
    """Product performance view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build product performance UI"""
        # Top products table
        top_products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ürün", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Satış Adedi", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Gelir", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Görüntülenme", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Dönüşüm Oranı", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
        
        return ft.Column([
            ft.Text("Ürün Performansı", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([
                    ft.Text("En Çok Satan Ürünler", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    top_products_table
                ]),
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load product performance data"""
        pass


class CustomerAnalyticsView:
    """Customer analytics view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build customer analytics UI"""
        # Customer metrics
        metrics = ft.Row([
            self._create_metric_card("Toplam Müşteri", "0", ft.Icons.PEOPLE),
            self._create_metric_card("Aktif Müşteri", "0", ft.Icons.PERSON),
            self._create_metric_card("Yeni Müşteri (Bu Ay)", "0", ft.Icons.PERSON_ADD),
            self._create_metric_card("Müşteri Elde Tutma", "%0", ft.Icons.TRENDING_UP),
        ], spacing=20, wrap=True)
        
        return ft.Column([
            ft.Text("Müşteri Analizi", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            metrics,
            ft.Container(height=20),
            ft.Container(
                content=ft.Text("Müşteri segmentasyonu ve davranış analizi burada görüntülenecek"),
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_metric_card(self, title: str, value: str, icon) -> ft.Container:
        """Create metric card"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=40, color=ft.Colors.BLUE),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=14, color=ft.Colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            width=200,
        )
    
    def load_data(self):
        """Load customer analytics data"""
        pass