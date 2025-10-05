"""
Dashboard View
"""

import flet as ft

from admin_panel.services import APIService


class DashboardView:
    """Dashboard view with statistics and overview"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.stats_row = None
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.stats = {
            "total_products": 0,
            "pending_orders": 0,
            "total_customers": 0,
            "today_sales": 0
        }
    
    def build(self) -> ft.Control:
        """Build dashboard UI"""
        # Statistics cards
        self.stats_row = ft.Row([
            self._create_stat_card("Toplam Ürün", str(self.stats["total_products"]), ft.Icons.INVENTORY, ft.Colors.BLUE),
            self._create_stat_card("Bekleyen Sipariş", str(self.stats["pending_orders"]), ft.Icons.PENDING, ft.Colors.ORANGE),
            self._create_stat_card("Toplam Müşteri", str(self.stats["total_customers"]), ft.Icons.PEOPLE, ft.Colors.GREEN),
            self._create_stat_card("Bugünkü Satış", f"₺{self.stats['today_sales']}", ft.Icons.ATTACH_MONEY, ft.Colors.PURPLE),
        ], spacing=20, wrap=True)
        
        # Recent orders section
        recent_orders = ft.Container(
            content=ft.Column([
                ft.Text("Son Siparişler", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Henüz sipariş yok", color=ft.Colors.GREY_600)
            ], spacing=10),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.GREY_300
            )
        )
        
        # Low stock products
        low_stock = ft.Container(
            content=ft.Column([
                ft.Text("Düşük Stok Uyarısı", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Tüm ürünler yeterli stokta", color=ft.Colors.GREY_600)
            ], spacing=10),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.GREY_300
            )
        )
        
        return ft.Column([
            ft.Text("Dashboard", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            self.stats_row,
            ft.Container(height=20),
            ft.Row([
                ft.Container(content=recent_orders, expand=True),
                ft.Container(width=20),
                ft.Container(content=low_stock, expand=True),
            ], expand=True)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def _create_stat_card(self, title: str, value: str, icon, color) -> ft.Container:
        """Create statistics card"""
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
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.Colors.GREY_300
            )
        )
    
    def load_data(self):
        """Load dashboard data"""
        try:
            # Load statistics from API
            products = self.api_service.get_products()
            orders = self.api_service.get_orders()
            customers = self.api_service.get_customers()
            
            # Update stats
            self.stats["total_products"] = len(products) if isinstance(products, list) else 0
            self.stats["total_customers"] = len(customers) if isinstance(customers, list) else 0
            
            # Count pending orders
            if isinstance(orders, list):
                self.stats["pending_orders"] = sum(1 for order in orders if order.get("status") == "pending")
                
                # Calculate today's sales (simplified - you may want to filter by date)
                self.stats["today_sales"] = sum(order.get("total", 0) for order in orders)
            
            # Update UI
            self._update_stats_display()
            
        except Exception as e:
            self.notification_manager.show_error(f"Veri yükleme hatası: {e}")
    
    def _update_stats_display(self):
        """Update statistics display"""
        if hasattr(self, 'stats_row'):
            self.stats_row.controls.clear()
            self.stats_row.controls.extend([
                self._create_stat_card("Toplam Ürün", str(self.stats["total_products"]), ft.Icons.INVENTORY, ft.Colors.BLUE),
                self._create_stat_card("Bekleyen Sipariş", str(self.stats["pending_orders"]), ft.Icons.PENDING, ft.Colors.ORANGE),
                self._create_stat_card("Toplam Müşteri", str(self.stats["total_customers"]), ft.Icons.PEOPLE, ft.Colors.GREEN),
                self._create_stat_card("Bugünkü Satış", f"₺{self.stats['today_sales']}", ft.Icons.ATTACH_MONEY, ft.Colors.PURPLE),
            ])
            self.page.update()