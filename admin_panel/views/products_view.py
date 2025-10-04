"""
Products View - Product list and management
"""

import flet as ft

from admin_panel.services import APIService


class ProductsView:
    """Products management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
        self.products = []
    
    def build(self) -> ft.Control:
        """Build products list UI"""
        # Header with add button
        header = ft.Row([
            ft.Text("Ürün Listesi", size=32, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Yeni Ürün Ekle",
                icon=ft.Icons.ADD,
                on_click=lambda e: self.show_add_product_form(),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Products table
        self.products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Ürün Adı")),
                ft.DataColumn(ft.Text("Kategori")),
                ft.DataColumn(ft.Text("Fiyat")),
                ft.DataColumn(ft.Text("Stok")),
                ft.DataColumn(ft.Text("İşlemler")),
            ],
            rows=[]
        )
        
        table_container = ft.Container(
            content=ft.Column([self.products_table], scroll=ft.ScrollMode.AUTO),
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
    
    def load_products(self):
        """Load products from API"""
        try:
            self.products = self.api_service.get_products()
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Ürünler yüklenemedi: {e}")
    
    def _update_table(self):
        """Update products table"""
        self.products_table.rows.clear()
        
        for product in self.products:
            self.products_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(product.get('id', '')))),
                    ft.DataCell(ft.Text(product.get('name', ''))),
                    ft.DataCell(ft.Text(product.get('category', ''))),
                    ft.DataCell(ft.Text(f"₺{product.get('price', 0)}")),
                    ft.DataCell(ft.Text(str(product.get('stock', 0)))),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=ft.Colors.BLUE,
                                on_click=lambda e, p=product: self.edit_product(p)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, p=product: self.delete_product(p)
                            )
                        ], spacing=5)
                    )
                ])
            )
        
        self.page.update()
    
    def show_add_product_form(self):
        """Show add product form"""
        self.notification_manager.show_info("Ürün ekleme formu yakında eklenecek")
    
    def edit_product(self, product):
        """Edit product"""
        self.notification_manager.show_info(f"Ürün düzenleme: {product.get('name')}")
    
    def delete_product(self, product):
        """Delete product"""
        def confirm_delete(e):
            try:
                self.api_service.delete_product(product['id'])
                self.notification_manager.show_success("Ürün silindi")
                self.load_products()
            except Exception as ex:
                self.notification_manager.show_error(f"Silme hatası: {ex}")
        
        self.modal_manager.show_confirmation(
            f"{product.get('name')} ürününü silmek istediğinizden emin misiniz?",
            confirm_delete
        )