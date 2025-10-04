"""
Orders View - Order list and management
"""

import flet as ft

from admin_panel.services import APIService


class OrdersView:
    """Orders management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
        self.orders = []
    
    def build(self) -> ft.Control:
        """Build orders list UI"""
        header = ft.Text("Sipariş Listesi", size=32, weight=ft.FontWeight.BOLD)
        
        # Orders table
        self.orders_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sipariş No")),
                ft.DataColumn(ft.Text("Müşteri")),
                ft.DataColumn(ft.Text("Tarih")),
                ft.DataColumn(ft.Text("Tutar")),
                ft.DataColumn(ft.Text("Durum")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=[]
        )
        
        table_container = ft.Container(
            content=ft.Column([self.orders_table], scroll=ft.ScrollMode.AUTO),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True
        )
        
        return ft.Column([
            header,
            ft.Container(height=20),
            table_container
        ], spacing=10, expand=True)
    
    def load_orders(self):
        """Load orders from API"""
        try:
            self.orders = self.api_service.get_orders()
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Siparişler yüklenemedi: {e}")
    
    def _update_table(self):
        """Update orders table"""
        self.orders_table.rows.clear()
        
        for order in self.orders:
            self.orders_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"#{order.get('id', '')}")),
                    ft.DataCell(ft.Text(order.get('customer_name', 'N/A'))),
                    ft.DataCell(ft.Text(order.get('created_at', '')[:10])),
                    ft.DataCell(ft.Text(f"₺{order.get('total', 0)}")),
                    ft.DataCell(ft.Text(order.get('status', ''))),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                icon_color=ft.Colors.BLUE,
                                on_click=lambda e, o=order: self.view_order(o)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.GREEN,
                                on_click=lambda e, o=order: self.edit_order_status(o)
                            )
                        ], spacing=5)
                    )
                ])
            )
        
        self.page.update()
    
    def view_order(self, order):
        """View order details"""
        self.notification_manager.show_info(f"Sipariş detayı: #{order.get('id')}")
    
    def edit_order_status(self, order):
        """Edit order status"""
        self.notification_manager.show_info(f"Sipariş durumu düzenleme: #{order.get('id')}")