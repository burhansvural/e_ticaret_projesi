"""
Finance and Accounting Views
"""

import flet as ft
from admin_panel.services import APIService


class IncomeReportView:
    """Income report view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build income report UI"""
        # Summary cards
        summary_cards = ft.Row([
            self._create_summary_card("Toplam Gelir", "₺0", ft.Colors.GREEN),
            self._create_summary_card("Bu Ay", "₺0", ft.Colors.BLUE),
            self._create_summary_card("Bu Hafta", "₺0", ft.Colors.ORANGE),
            self._create_summary_card("Bugün", "₺0", ft.Colors.PURPLE),
        ], spacing=20, wrap=True)
        
        # Income table
        income_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tarih", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Sipariş No", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Müşteri", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tutar", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ödeme Yöntemi", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Text("Gelir Raporu", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            summary_cards,
            ft.Container(height=20),
            ft.Row([
                ft.TextField(label="Başlangıç Tarihi", width=200),
                ft.TextField(label="Bitiş Tarihi", width=200),
                ft.ElevatedButton("Filtrele", icon=ft.Icons.FILTER_LIST),
                ft.Container(expand=True),
                ft.ElevatedButton("Dışa Aktar", icon=ft.Icons.DOWNLOAD),
            ], spacing=10),
            ft.Container(height=20),
            ft.Container(
                content=income_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_summary_card(self, title: str, value: str, color) -> ft.Container:
        """Create summary card"""
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
        """Load income data"""
        pass


class ExpensesView:
    """Expenses management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build expenses UI"""
        # Expenses table
        expenses_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tarih", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Kategori", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Açıklama", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tutar", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ödeme Yöntemi", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Gider Yönetimi", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Gider",
                    icon=ft.Icons.ADD,
                    on_click=self.add_expense
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=expenses_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load expenses data"""
        pass
    
    def add_expense(self, e):
        """Add new expense"""
        self.notification_manager.show_info("Gider ekleme özelliği yakında eklenecek")


class InvoicesView:
    """Invoices management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
    
    def build(self) -> ft.Control:
        """Build invoices UI"""
        # Invoices table
        invoices_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Fatura No", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Müşteri", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tarih", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tutar", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Faturalar", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Fatura",
                    icon=ft.Icons.ADD,
                    on_click=self.create_invoice
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=invoices_table,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_data(self):
        """Load invoices data"""
        pass
    
    def create_invoice(self, e):
        """Create new invoice"""
        self.notification_manager.show_info("Fatura oluşturma özelliği yakında eklenecek")


class PaymentMethodsView:
    """Payment methods management view"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager, modal_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.modal_manager = modal_manager
    
    def build(self) -> ft.Control:
        """Build payment methods UI"""
        # Payment methods list
        methods_list = ft.ListView(
            spacing=10,
            controls=[
                self._create_method_card("Kredi Kartı", "Aktif", ft.Icons.CREDIT_CARD),
                self._create_method_card("Banka Transferi", "Aktif", ft.Icons.ACCOUNT_BALANCE),
                self._create_method_card("Kapıda Ödeme", "Aktif", ft.Icons.MONEY),
                self._create_method_card("Havale/EFT", "Pasif", ft.Icons.PAYMENT),
            ]
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Ödeme Yöntemleri", size=32, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Yeni Yöntem",
                    icon=ft.Icons.ADD,
                    on_click=self.add_method
                ),
            ]),
            ft.Container(height=20),
            ft.Container(
                content=methods_list,
                bgcolor=ft.Colors.WHITE,
                padding=20,
                border_radius=10,
                expand=True
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def _create_method_card(self, name: str, status: str, icon) -> ft.Container:
        """Create payment method card"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=40, color=ft.Colors.BLUE),
                ft.Column([
                    ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(status, size=12, color=ft.Colors.GREY_600),
                ], spacing=5),
                ft.Container(expand=True),
                ft.Switch(value=status == "Aktif"),
                ft.IconButton(icon=ft.Icons.SETTINGS, tooltip="Ayarlar"),
            ]),
            padding=15,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
        )
    
    def load_data(self):
        """Load payment methods data"""
        pass
    
    def add_method(self, e):
        """Add new payment method"""
        self.notification_manager.show_info("Ödeme yöntemi ekleme özelliği yakında eklenecek")