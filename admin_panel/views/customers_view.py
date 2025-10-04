"""
Customers View - Customer list and management
"""

import flet as ft

from admin_panel.services import APIService


class CustomersView:
    """Customers management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.customers = []
    
    def build(self) -> ft.Control:
        """Build customers list UI"""
        header = ft.Text("Müşteri Listesi", size=32, weight=ft.FontWeight.BOLD)
        
        # Customers table
        self.customers_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Ad Soyad")),
                ft.DataColumn(ft.Text("E-posta")),
                ft.DataColumn(ft.Text("Telefon")),
                ft.DataColumn(ft.Text("Kayıt Tarihi")),
            ],
            rows=[]
        )
        
        table_container = ft.Container(
            content=ft.Column([self.customers_table], scroll=ft.ScrollMode.AUTO),
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
    
    def load_customers(self):
        """Load customers from API"""
        try:
            self.customers = self.api_service.get_customers()
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Müşteriler yüklenemedi: {e}")
    
    def _update_table(self):
        """Update customers table"""
        self.customers_table.rows.clear()
        
        for customer in self.customers:
            self.customers_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(customer.get('id', '')))),
                    ft.DataCell(ft.Text(f"{customer.get('first_name', '')} {customer.get('last_name', '')}")),
                    ft.DataCell(ft.Text(customer.get('email', ''))),
                    ft.DataCell(ft.Text(customer.get('phone', 'N/A'))),
                    ft.DataCell(ft.Text(customer.get('created_at', '')[:10])),
                ])
            )
        
        self.page.update()