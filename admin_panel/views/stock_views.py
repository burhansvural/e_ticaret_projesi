"""
Stock Management Views
Complete stock management system with movements, suppliers, and purchase invoices
"""

import flet as ft
from datetime import datetime
from typing import Optional
from admin_panel.services import APIService


class StockMovementsView:
    """Stock Movements View - Display all stock entries and exits"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.movements = []
        self.products = []
        self.movements_table = None
        self.filter_product = None
        self.filter_type = None
        self.date_from = None
        self.date_to = None
    
    def build(self) -> ft.Control:
        """Build stock movements view"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.SWAP_HORIZ, size=32, color=ft.Colors.BLUE),
            ft.Text("Stok Hareketleri", size=32, weight=ft.FontWeight.BOLD),
        ], spacing=10)
        
        # Filters
        self.filter_product = ft.Dropdown(
            label="Ürün Filtrele",
            options=[ft.dropdown.Option("", "Tüm Ürünler")],
            value="",
            width=250,
            on_change=lambda e: self._apply_filters()
        )
        
        self.filter_type = ft.Dropdown(
            label="Hareket Tipi",
            options=[
                ft.dropdown.Option("", "Tümü"),
                ft.dropdown.Option("entry", "Giriş"),
                ft.dropdown.Option("exit", "Çıkış"),
            ],
            value="",
            width=200,
            on_change=lambda e: self._apply_filters()
        )
        
        filters_row = ft.Row([
            self.filter_product,
            self.filter_type,
            ft.ElevatedButton(
                "Yenile",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: self.load_data(),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        ], spacing=10)
        
        # Movements table
        self.movements_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tarih", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ürün", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tip", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Miktar", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Açıklama", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Referans", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        )
        
        table_container = ft.Container(
            content=ft.Column([
                self.movements_table
            ], scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            expand=True
        )
        
        # Stats cards
        stats_row = ft.Row([
            self._create_stat_card("Toplam Giriş", "0", ft.Colors.GREEN, ft.Icons.ARROW_DOWNWARD),
            self._create_stat_card("Toplam Çıkış", "0", ft.Colors.RED, ft.Icons.ARROW_UPWARD),
            self._create_stat_card("Net Değişim", "0", ft.Colors.BLUE, ft.Icons.TRENDING_UP),
        ], spacing=15)
        
        return ft.Column([
            header,
            ft.Divider(height=20),
            stats_row,
            ft.Container(height=20),
            filters_row,
            ft.Container(height=10),
            table_container
        ], spacing=10, expand=True)
    
    def _create_stat_card(self, title: str, value: str, color, icon):
        """Create statistics card"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(title, size=14, color=ft.Colors.GREY_700)
                ], spacing=10),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=color)
            ], spacing=5),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            expand=True
        )
    
    def load_data(self):
        """Load stock movements"""
        try:
            # Load movements
            movements_response = self.api_service.get_stock_movements()
            self.movements = movements_response if isinstance(movements_response, list) else []
            
            # Load products for filter
            products_response = self.api_service.get_products()
            self.products = products_response if isinstance(products_response, list) else []
            
            self._update_product_filter()
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Veriler yüklenemedi: {e}")
    
    def _update_product_filter(self):
        """Update product filter dropdown"""
        options = [ft.dropdown.Option("", "Tüm Ürünler")]
        for product in self.products:
            options.append(ft.dropdown.Option(str(product.get('id')), product.get('name')))
        self.filter_product.options = options
        self.page.update()
    
    def _apply_filters(self):
        """Apply filters to movements"""
        self._update_table()
    
    def _update_table(self):
        """Update movements table"""
        filtered_movements = self.movements
        
        # Apply product filter
        if self.filter_product.value:
            filtered_movements = [m for m in filtered_movements 
                                 if str(m.get('product_id')) == self.filter_product.value]
        
        # Apply type filter
        if self.filter_type.value:
            filtered_movements = [m for m in filtered_movements 
                                 if m.get('movement_type') == self.filter_type.value]
        
        # Build table rows
        rows = []
        for movement in filtered_movements:
            movement_type = movement.get('movement_type', '')
            type_color = ft.Colors.GREEN if movement_type == 'entry' else ft.Colors.RED
            type_text = "Giriş" if movement_type == 'entry' else "Çıkış"
            
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(movement.get('created_at', '')[:10])),
                    ft.DataCell(ft.Text(movement.get('product_name', 'N/A'))),
                    ft.DataCell(ft.Container(
                        content=ft.Text(type_text, color=ft.Colors.WHITE, size=12),
                        bgcolor=type_color,
                        padding=5,
                        border_radius=5
                    )),
                    ft.DataCell(ft.Text(str(movement.get('quantity', 0)))),
                    ft.DataCell(ft.Text(movement.get('description', '-'))),
                    ft.DataCell(ft.Text(movement.get('reference', '-'))),
                ]
            ))
        
        self.movements_table.rows = rows
        self.page.update()


class LowStockAlertsView:
    """Low Stock Alerts View - Display products with low stock"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.low_stock_products = []
        self.products_table = None
        self.threshold_field = None
    
    def build(self) -> ft.Control:
        """Build low stock alerts view"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER, size=32, color=ft.Colors.ORANGE),
            ft.Text("Düşük Stok Uyarıları", size=32, weight=ft.FontWeight.BOLD),
        ], spacing=10)
        
        # Threshold control
        self.threshold_field = ft.TextField(
            label="Minimum Stok Seviyesi",
            value="10",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        controls_row = ft.Row([
            self.threshold_field,
            ft.ElevatedButton(
                "Filtrele",
                icon=ft.Icons.FILTER_ALT,
                on_click=lambda e: self.load_data(),
                bgcolor=ft.Colors.ORANGE,
                color=ft.Colors.WHITE
            )
        ], spacing=10)
        
        # Products table
        self.products_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ürün", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Mevcut Stok", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Birim", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlem", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        )
        
        table_container = ft.Container(
            content=ft.Column([
                self.products_table
            ], scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            expand=True
        )
        
        return ft.Column([
            header,
            ft.Divider(height=20),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.ORANGE),
                    ft.Text(
                        "Stok seviyesi belirlenen eşiğin altında olan ürünler listelenir.",
                        color=ft.Colors.GREY_700
                    )
                ], spacing=10),
                bgcolor=ft.Colors.ORANGE_50,
                padding=15,
                border_radius=10
            ),
            ft.Container(height=10),
            controls_row,
            ft.Container(height=10),
            table_container
        ], spacing=10, expand=True)
    
    def load_data(self):
        """Load low stock products"""
        try:
            threshold = int(self.threshold_field.value) if self.threshold_field.value else 10
            response = self.api_service.get_low_stock_products(threshold)
            self.low_stock_products = response if isinstance(response, list) else []
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Veriler yüklenemedi: {e}")
    
    def _update_table(self):
        """Update products table"""
        rows = []
        for product in self.low_stock_products:
            stock = product.get('stock_quantity', 0)
            status_color = ft.Colors.RED if stock == 0 else ft.Colors.ORANGE
            status_text = "Tükendi" if stock == 0 else "Düşük"
            
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(product.get('name', 'N/A'))),
                    ft.DataCell(ft.Text(str(stock), color=status_color, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(product.get('unit', 'adet'))),
                    ft.DataCell(ft.Container(
                        content=ft.Text(status_text, color=ft.Colors.WHITE, size=12),
                        bgcolor=status_color,
                        padding=5,
                        border_radius=5
                    )),
                    ft.DataCell(ft.IconButton(
                        icon=ft.Icons.ADD_SHOPPING_CART,
                        tooltip="Stok Ekle",
                        icon_color=ft.Colors.BLUE,
                        on_click=lambda e, p=product: self._quick_add_stock(p)
                    )),
                ]
            ))
        
        self.products_table.rows = rows
        self.page.update()
    
    def _quick_add_stock(self, product):
        """Quick add stock for product"""
        # This would open a modal to add stock
        self.notification_manager.show_info(f"Stok ekleme: {product.get('name')}")


class ManualStockEntryView:
    """Manual Stock Entry View - Add stock manually"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.products = []
        
        # Form fields
        self.product_field = None
        self.quantity_field = None
        self.description_field = None
        self.reference_field = None
    
    def build(self) -> ft.Control:
        """Build manual stock entry form"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.ADD_BOX, size=32, color=ft.Colors.GREEN),
            ft.Text("Manuel Stok Girişi", size=32, weight=ft.FontWeight.BOLD),
        ], spacing=10)
        
        # Form fields
        self.product_field = ft.Dropdown(
            label="Ürün Seçin *",
            options=[],
            border_color=ft.Colors.BLUE_200,
            autofocus=True
        )
        
        self.quantity_field = ft.TextField(
            label="Miktar *",
            hint_text="0",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.BLUE_200
        )
        
        self.description_field = ft.TextField(
            label="Açıklama",
            hint_text="Stok giriş nedeni",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.BLUE_200
        )
        
        self.reference_field = ft.TextField(
            label="Referans No",
            hint_text="Fatura/İrsaliye No (opsiyonel)",
            border_color=ft.Colors.BLUE_200
        )
        
        # Form container
        form_container = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Stok Bilgileri", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        self.product_field,
                        self.quantity_field,
                        self.description_field,
                        self.reference_field,
                    ], spacing=15),
                    padding=20,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton(
                        "Stok Ekle",
                        icon=ft.Icons.SAVE,
                        on_click=self._add_stock,
                        bgcolor=ft.Colors.GREEN,
                        color=ft.Colors.WHITE,
                        height=45,
                        width=150
                    ),
                    ft.OutlinedButton(
                        "Temizle",
                        icon=ft.Icons.CLEAR,
                        on_click=self._clear_form,
                        height=45,
                        width=150
                    )
                ], alignment=ft.MainAxisAlignment.END, spacing=10)
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True
        )
        
        return form_container
    
    def load_data(self):
        """Load products for dropdown"""
        try:
            response = self.api_service.get_products()
            self.products = response if isinstance(response, list) else []
            self._update_product_dropdown()
        except Exception as e:
            self.notification_manager.show_error(f"Ürünler yüklenemedi: {e}")
    
    def _update_product_dropdown(self):
        """Update product dropdown"""
        options = []
        for product in self.products:
            options.append(ft.dropdown.Option(
                str(product.get('id')), 
                f"{product.get('name')} (Mevcut: {product.get('stock_quantity', 0)} {product.get('unit', 'adet')})"
            ))
        self.product_field.options = options
        self.page.update()
    
    def _add_stock(self, e):
        """Add stock entry"""
        # Validation
        if not self.product_field.value:
            self.notification_manager.show_error("Ürün seçimi gerekli")
            self.product_field.focus()
            return
        
        if not self.quantity_field.value:
            self.notification_manager.show_error("Miktar gerekli")
            self.quantity_field.focus()
            return
        
        try:
            quantity = int(self.quantity_field.value)
            if quantity <= 0:
                self.notification_manager.show_error("Miktar pozitif olmalı")
                self.quantity_field.focus()
                return
        except ValueError:
            self.notification_manager.show_error("Geçersiz miktar")
            self.quantity_field.focus()
            return
        
        # Create stock movement
        try:
            movement_data = {
                "product_id": int(self.product_field.value),
                "movement_type": "entry",
                "quantity": quantity,
                "description": self.description_field.value or "Manuel stok girişi",
                "reference": self.reference_field.value or None
            }
            
            self.api_service.create_stock_movement(movement_data)
            self.notification_manager.show_success("Stok başarıyla eklendi")
            self._clear_form(None)
            self.load_data()  # Refresh product list with updated stock
        except Exception as ex:
            self.notification_manager.show_error(f"Stok eklenemedi: {ex}")
    
    def _clear_form(self, e):
        """Clear form fields"""
        self.product_field.value = ""
        self.quantity_field.value = ""
        self.description_field.value = ""
        self.reference_field.value = ""
        self.page.update()
        self.product_field.focus()


class ManualStockExitView:
    """Manual Stock Exit View - Remove stock manually"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.products = []
        
        # Form fields
        self.product_field = None
        self.quantity_field = None
        self.description_field = None
        self.reference_field = None
    
    def build(self) -> ft.Control:
        """Build manual stock exit form"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.REMOVE_CIRCLE, size=32, color=ft.Colors.RED),
            ft.Text("Manuel Stok Çıkışı", size=32, weight=ft.FontWeight.BOLD),
        ], spacing=10)
        
        # Form fields
        self.product_field = ft.Dropdown(
            label="Ürün Seçin *",
            options=[],
            border_color=ft.Colors.BLUE_200,
            autofocus=True
        )
        
        self.quantity_field = ft.TextField(
            label="Miktar *",
            hint_text="0",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.BLUE_200
        )
        
        self.description_field = ft.TextField(
            label="Açıklama *",
            hint_text="Stok çıkış nedeni (fire, bozulma, vb.)",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.BLUE_200
        )
        
        self.reference_field = ft.TextField(
            label="Referans No",
            hint_text="İlgili belge no (opsiyonel)",
            border_color=ft.Colors.BLUE_200
        )
        
        # Form container
        form_container = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=20),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED),
                        ft.Text(
                            "Dikkat: Bu işlem stok miktarını azaltacaktır. Satış işlemleri otomatik olarak stok düşer.",
                            color=ft.Colors.RED_700
                        )
                    ], spacing=10),
                    bgcolor=ft.Colors.RED_50,
                    padding=15,
                    border_radius=10
                ),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Stok Bilgileri", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_700),
                        self.product_field,
                        self.quantity_field,
                        self.description_field,
                        self.reference_field,
                    ], spacing=15),
                    padding=20,
                    bgcolor=ft.Colors.RED_50,
                    border_radius=10
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton(
                        "Stok Çıkar",
                        icon=ft.Icons.REMOVE,
                        on_click=self._remove_stock,
                        bgcolor=ft.Colors.RED,
                        color=ft.Colors.WHITE,
                        height=45,
                        width=150
                    ),
                    ft.OutlinedButton(
                        "Temizle",
                        icon=ft.Icons.CLEAR,
                        on_click=self._clear_form,
                        height=45,
                        width=150
                    )
                ], alignment=ft.MainAxisAlignment.END, spacing=10)
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True
        )
        
        return form_container
    
    def load_data(self):
        """Load products for dropdown"""
        try:
            response = self.api_service.get_products()
            self.products = response if isinstance(response, list) else []
            self._update_product_dropdown()
        except Exception as e:
            self.notification_manager.show_error(f"Ürünler yüklenemedi: {e}")
    
    def _update_product_dropdown(self):
        """Update product dropdown"""
        options = []
        for product in self.products:
            options.append(ft.dropdown.Option(
                str(product.get('id')), 
                f"{product.get('name')} (Mevcut: {product.get('stock_quantity', 0)} {product.get('unit', 'adet')})"
            ))
        self.product_field.options = options
        self.page.update()
    
    def _remove_stock(self, e):
        """Remove stock"""
        # Validation
        if not self.product_field.value:
            self.notification_manager.show_error("Ürün seçimi gerekli")
            self.product_field.focus()
            return
        
        if not self.quantity_field.value:
            self.notification_manager.show_error("Miktar gerekli")
            self.quantity_field.focus()
            return
        
        if not self.description_field.value:
            self.notification_manager.show_error("Açıklama gerekli")
            self.description_field.focus()
            return
        
        try:
            quantity = int(self.quantity_field.value)
            if quantity <= 0:
                self.notification_manager.show_error("Miktar pozitif olmalı")
                self.quantity_field.focus()
                return
        except ValueError:
            self.notification_manager.show_error("Geçersiz miktar")
            self.quantity_field.focus()
            return
        
        # Check if enough stock available
        product = next((p for p in self.products if str(p.get('id')) == self.product_field.value), None)
        if product and product.get('stock_quantity', 0) < quantity:
            self.notification_manager.show_error(f"Yetersiz stok! Mevcut: {product.get('stock_quantity', 0)}")
            return
        
        # Create stock movement
        try:
            movement_data = {
                "product_id": int(self.product_field.value),
                "movement_type": "exit",
                "quantity": quantity,
                "description": self.description_field.value,
                "reference": self.reference_field.value or None
            }
            
            self.api_service.create_stock_movement(movement_data)
            self.notification_manager.show_success("Stok başarıyla çıkarıldı")
            self._clear_form(None)
            self.load_data()  # Refresh product list with updated stock
        except Exception as ex:
            self.notification_manager.show_error(f"Stok çıkarılamadı: {ex}")
    
    def _clear_form(self, e):
        """Clear form fields"""
        self.product_field.value = ""
        self.quantity_field.value = ""
        self.description_field.value = ""
        self.reference_field.value = ""
        self.page.update()
        self.product_field.focus()