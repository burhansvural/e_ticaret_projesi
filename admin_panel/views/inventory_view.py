"""
Inventory Management View
"""

import flet as ft
from admin_panel.services import APIService


class InventoryView:
    """Inventory management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.products = []
        self.products_table = None
    
    def build(self) -> ft.Control:
        """Build inventory UI"""
        # Search and filter controls
        search_field = ft.TextField(
            label="Ürün Ara",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            on_change=self.on_search
        )
        
        filter_dropdown = ft.Dropdown(
            label="Stok Durumu",
            width=200,
            options=[
                ft.dropdown.Option("all", "Tümü"),
                ft.dropdown.Option("low", "Düşük Stok"),
                ft.dropdown.Option("out", "Stokta Yok"),
                ft.dropdown.Option("normal", "Normal"),
            ],
            value="all",
            on_change=self.on_filter_change
        )
        
        # Products table
        self.products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ürün Adı", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("SKU", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Mevcut Stok", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Min. Stok", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        )
        
        return ft.Column([
            ft.Text("Stok Yönetimi", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Row([
                search_field,
                filter_dropdown,
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Stok Güncelle",
                    icon=ft.Icons.UPDATE,
                    on_click=self.show_bulk_update_dialog
                ),
            ], spacing=10),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([
                    self.products_table
                ], scroll=ft.ScrollMode.AUTO),
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load inventory data"""
        try:
            self.products = self.api_service.get_products()
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Veri yükleme hatası: {e}")
    
    def _update_table(self):
        """Update products table"""
        self.products_table.rows.clear()
        
        for product in self.products:
            stock = product.get("stock", 0)
            min_stock = 10  # Default minimum stock
            
            # Determine stock status
            if stock == 0:
                status = ft.Container(
                    content=ft.Text("Stokta Yok", color=ft.Colors.WHITE, size=12),
                    bgcolor=ft.Colors.RED,
                    padding=5,
                    border_radius=5
                )
            elif stock < min_stock:
                status = ft.Container(
                    content=ft.Text("Düşük Stok", color=ft.Colors.WHITE, size=12),
                    bgcolor=ft.Colors.ORANGE,
                    padding=5,
                    border_radius=5
                )
            else:
                status = ft.Container(
                    content=ft.Text("Normal", color=ft.Colors.WHITE, size=12),
                    bgcolor=ft.Colors.GREEN,
                    padding=5,
                    border_radius=5
                )
            
            self.products_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(product.get("name", ""))),
                        ft.DataCell(ft.Text(product.get("id", ""))),
                        ft.DataCell(ft.Text(str(stock))),
                        ft.DataCell(ft.Text(str(min_stock))),
                        ft.DataCell(status),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Stok Düzenle",
                                    on_click=lambda e, p=product: self.edit_stock(p)
                                ),
                            ], spacing=5)
                        ),
                    ]
                )
            )
        
        self.page.update()
    
    def on_search(self, e):
        """Handle search"""
        # Implement search logic
        pass
    
    def on_filter_change(self, e):
        """Handle filter change"""
        # Implement filter logic
        pass
    
    def edit_stock(self, product):
        """Edit product stock"""
        self.notification_manager.show_info(f"Stok düzenleme: {product.get('name')}")
    
    def show_bulk_update_dialog(self, e):
        """Show bulk stock update dialog"""
        self.notification_manager.show_info("Toplu stok güncelleme özelliği yakında eklenecek")