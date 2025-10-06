"""
Supplier and Purchase Management Views
Complete supplier management and purchase invoice/waybill processing
"""

import flet as ft
from datetime import datetime
from typing import Optional
from admin_panel.services import APIService


class SuppliersListView:
    """Suppliers List View - Display and manage all suppliers"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.suppliers = []
        self.suppliers_table = None
        self.search_field = None
    
    def build(self) -> ft.Control:
        """Build suppliers list view"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.BUSINESS, size=32, color=ft.Colors.BLUE),
            ft.Text("Tedarikçiler", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Yeni Tedarikçi",
                icon=ft.Icons.ADD,
                on_click=self._show_add_supplier_dialog,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        ], spacing=10)
        
        # Search
        self.search_field = ft.TextField(
            hint_text="Tedarikçi ara...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=lambda e: self._filter_suppliers(),
            width=300
        )
        
        # Suppliers table
        self.suppliers_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Firma Adı", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İletişim", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Telefon", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("E-posta", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        )
        
        table_container = ft.Container(
            content=ft.Column([
                self.suppliers_table
            ], scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            expand=True
        )
        
        return ft.Column([
            header,
            ft.Divider(height=20),
            self.search_field,
            ft.Container(height=10),
            table_container
        ], spacing=10, expand=True)
    
    def load_data(self):
        """Load suppliers"""
        try:
            response = self.api_service.get_suppliers()
            self.suppliers = response if isinstance(response, list) else []
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Tedarikçiler yüklenemedi: {e}")
    
    def _filter_suppliers(self):
        """Filter suppliers by search term"""
        self._update_table()
    
    def _update_table(self):
        """Update suppliers table"""
        search_term = self.search_field.value.lower() if self.search_field.value else ""
        filtered_suppliers = [s for s in self.suppliers 
                             if search_term in s.get('company_name', '').lower() or
                                search_term in s.get('contact_person', '').lower()]
        
        rows = []
        for supplier in filtered_suppliers:
            is_active = supplier.get('is_active', True)
            status_color = ft.Colors.GREEN if is_active else ft.Colors.GREY
            status_text = "Aktif" if is_active else "Pasif"
            
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(supplier.get('company_name', 'N/A'), weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(supplier.get('contact_person', '-'))),
                    ft.DataCell(ft.Text(supplier.get('phone', '-'))),
                    ft.DataCell(ft.Text(supplier.get('email', '-'))),
                    ft.DataCell(ft.Container(
                        content=ft.Text(status_text, color=ft.Colors.WHITE, size=12),
                        bgcolor=status_color,
                        padding=5,
                        border_radius=5
                    )),
                    ft.DataCell(ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Düzenle",
                            icon_color=ft.Colors.BLUE,
                            on_click=lambda e, s=supplier: self._show_edit_supplier_dialog(s)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Sil",
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, s=supplier: self._delete_supplier(s)
                        ),
                    ], spacing=0)),
                ]
            ))
        
        self.suppliers_table.rows = rows
        self.page.update()
    
    def _show_add_supplier_dialog(self, e):
        """Show add supplier dialog"""
        self.notification_manager.show_info("Tedarikçi ekleme formu açılacak")
        # This would open a modal dialog
    
    def _show_edit_supplier_dialog(self, supplier):
        """Show edit supplier dialog"""
        self.notification_manager.show_info(f"Düzenleme: {supplier.get('company_name')}")
    
    def _delete_supplier(self, supplier):
        """Delete supplier"""
        # This would show a confirmation dialog
        self.notification_manager.show_info(f"Silme: {supplier.get('company_name')}")


class AddSupplierView:
    """Add Supplier View - Create new supplier"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        
        # Form fields
        self.company_name_field = None
        self.contact_person_field = None
        self.phone_field = None
        self.email_field = None
        self.address_field = None
        self.tax_office_field = None
        self.tax_number_field = None
        self.notes_field = None
        self.is_active_field = None
    
    def build(self) -> ft.Control:
        """Build add supplier form"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.ADD_BUSINESS, size=32, color=ft.Colors.BLUE),
            ft.Text("Yeni Tedarikçi Ekle", size=32, weight=ft.FontWeight.BOLD),
        ], spacing=10)
        
        # Form fields
        self.company_name_field = ft.TextField(
            label="Firma Adı *",
            hint_text="Tedarikçi firma adı",
            autofocus=True,
            border_color=ft.Colors.BLUE_200
        )
        
        self.contact_person_field = ft.TextField(
            label="İletişim Kişisi",
            hint_text="Yetkili kişi adı",
            border_color=ft.Colors.BLUE_200
        )
        
        self.phone_field = ft.TextField(
            label="Telefon *",
            hint_text="+90 5XX XXX XX XX",
            keyboard_type=ft.KeyboardType.PHONE,
            border_color=ft.Colors.BLUE_200
        )
        
        self.email_field = ft.TextField(
            label="E-posta",
            hint_text="ornek@firma.com",
            keyboard_type=ft.KeyboardType.EMAIL,
            border_color=ft.Colors.BLUE_200
        )
        
        self.address_field = ft.TextField(
            label="Adres",
            hint_text="Firma adresi",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color=ft.Colors.BLUE_200
        )
        
        self.tax_office_field = ft.TextField(
            label="Vergi Dairesi",
            hint_text="Vergi dairesi adı",
            border_color=ft.Colors.BLUE_200
        )
        
        self.tax_number_field = ft.TextField(
            label="Vergi Numarası",
            hint_text="XXXXXXXXXX",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=ft.Colors.BLUE_200
        )
        
        self.notes_field = ft.TextField(
            label="Notlar",
            hint_text="Ek bilgiler",
            multiline=True,
            min_lines=2,
            max_lines=4,
            border_color=ft.Colors.BLUE_200
        )
        
        self.is_active_field = ft.Checkbox(
            label="Aktif",
            value=True
        )
        
        # Form layout
        form_container = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=20),
                
                # Basic info
                ft.Container(
                    content=ft.Column([
                        ft.Text("Temel Bilgiler", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                        self.company_name_field,
                        self.contact_person_field,
                        ft.Row([self.phone_field, self.email_field], spacing=10),
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=10
                ),
                
                ft.Container(height=10),
                
                # Address and tax info
                ft.Container(
                    content=ft.Column([
                        ft.Text("Adres ve Vergi Bilgileri", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        self.address_field,
                        ft.Row([self.tax_office_field, self.tax_number_field], spacing=10),
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10
                ),
                
                ft.Container(height=10),
                
                # Additional info
                ft.Container(
                    content=ft.Column([
                        ft.Text("Ek Bilgiler", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                        self.notes_field,
                        self.is_active_field,
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.Colors.ORANGE_50,
                    border_radius=10
                ),
                
                ft.Container(height=20),
                
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        "Kaydet",
                        icon=ft.Icons.SAVE,
                        on_click=self._save_supplier,
                        bgcolor=ft.Colors.BLUE,
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
        """Load data - not needed for add form"""
        pass
    
    def _save_supplier(self, e):
        """Save new supplier"""
        # Validation
        if not self.company_name_field.value:
            self.notification_manager.show_error("Firma adı gerekli")
            self.company_name_field.focus()
            return
        
        if not self.phone_field.value:
            self.notification_manager.show_error("Telefon gerekli")
            self.phone_field.focus()
            return
        
        # Create supplier
        try:
            supplier_data = {
                "company_name": self.company_name_field.value,
                "contact_person": self.contact_person_field.value or None,
                "phone": self.phone_field.value,
                "email": self.email_field.value or None,
                "address": self.address_field.value or None,
                "tax_office": self.tax_office_field.value or None,
                "tax_number": self.tax_number_field.value or None,
                "notes": self.notes_field.value or None,
                "is_active": self.is_active_field.value
            }
            
            self.api_service.create_supplier(supplier_data)
            self.notification_manager.show_success("Tedarikçi başarıyla eklendi")
            self._clear_form(None)
        except Exception as ex:
            self.notification_manager.show_error(f"Tedarikçi eklenemedi: {ex}")
    
    def _clear_form(self, e):
        """Clear form fields"""
        self.company_name_field.value = ""
        self.contact_person_field.value = ""
        self.phone_field.value = ""
        self.email_field.value = ""
        self.address_field.value = ""
        self.tax_office_field.value = ""
        self.tax_number_field.value = ""
        self.notes_field.value = ""
        self.is_active_field.value = True
        self.page.update()
        self.company_name_field.focus()


class PurchaseInvoicesView:
    """Purchase Invoices View - Display all purchase invoices/waybills"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.invoices = []
        self.invoices_table = None
        self.filter_status = None
    
    def build(self) -> ft.Control:
        """Build purchase invoices view"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.RECEIPT, size=32, color=ft.Colors.BLUE),
            ft.Text("Alış Faturaları / İrsaliyeleri", size=32, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Yeni Fatura/İrsaliye",
                icon=ft.Icons.ADD,
                on_click=lambda e: self.notification_manager.show_info("Fatura ekleme sayfasına yönlendirilecek"),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        ], spacing=10)
        
        # Filters
        self.filter_status = ft.Dropdown(
            label="Durum Filtrele",
            options=[
                ft.dropdown.Option("", "Tümü"),
                ft.dropdown.Option("pending", "Beklemede"),
                ft.dropdown.Option("paid", "Ödendi"),
                ft.dropdown.Option("partial", "Kısmi Ödendi"),
            ],
            value="",
            width=200,
            on_change=lambda e: self._apply_filters()
        )
        
        filters_row = ft.Row([
            self.filter_status,
            ft.ElevatedButton(
                "Yenile",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: self.load_data(),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            )
        ], spacing=10)
        
        # Invoices table
        self.invoices_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tarih", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Belge No", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tedarikçi", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Toplam", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Durum", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("İşlemler", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10,
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
        )
        
        table_container = ft.Container(
            content=ft.Column([
                self.invoices_table
            ], scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            expand=True
        )
        
        return ft.Column([
            header,
            ft.Divider(height=20),
            filters_row,
            ft.Container(height=10),
            table_container
        ], spacing=10, expand=True)
    
    def load_data(self):
        """Load purchase invoices"""
        try:
            response = self.api_service.get_purchase_invoices()
            self.invoices = response if isinstance(response, list) else []
            self._update_table()
        except Exception as e:
            self.notification_manager.show_error(f"Faturalar yüklenemedi: {e}")
    
    def _apply_filters(self):
        """Apply filters"""
        self._update_table()
    
    def _update_table(self):
        """Update invoices table"""
        filtered_invoices = self.invoices
        
        # Apply status filter
        if self.filter_status.value:
            filtered_invoices = [i for i in filtered_invoices 
                                if i.get('payment_status') == self.filter_status.value]
        
        rows = []
        for invoice in filtered_invoices:
            status = invoice.get('payment_status', 'pending')
            status_colors = {
                'pending': ft.Colors.ORANGE,
                'paid': ft.Colors.GREEN,
                'partial': ft.Colors.BLUE
            }
            status_texts = {
                'pending': 'Beklemede',
                'paid': 'Ödendi',
                'partial': 'Kısmi'
            }
            
            rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(invoice.get('invoice_date', '')[:10])),
                    ft.DataCell(ft.Text(invoice.get('invoice_number', 'N/A'))),
                    ft.DataCell(ft.Text(invoice.get('supplier_name', 'N/A'))),
                    ft.DataCell(ft.Text(f"₺{invoice.get('total_amount', 0):.2f}", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(status_texts.get(status, status), color=ft.Colors.WHITE, size=12),
                        bgcolor=status_colors.get(status, ft.Colors.GREY),
                        padding=5,
                        border_radius=5
                    )),
                    ft.DataCell(ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.VISIBILITY,
                            tooltip="Görüntüle",
                            icon_color=ft.Colors.BLUE,
                            on_click=lambda e, inv=invoice: self._view_invoice(inv)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Sil",
                            icon_color=ft.Colors.RED,
                            on_click=lambda e, inv=invoice: self._delete_invoice(inv)
                        ),
                    ], spacing=0)),
                ]
            ))
        
        self.invoices_table.rows = rows
        self.page.update()
    
    def _view_invoice(self, invoice):
        """View invoice details"""
        self.notification_manager.show_info(f"Fatura görüntüleme: {invoice.get('invoice_number')}")
    
    def _delete_invoice(self, invoice):
        """Delete invoice"""
        self.notification_manager.show_info(f"Fatura silme: {invoice.get('invoice_number')}")


class AddPurchaseInvoiceView:
    """Add Purchase Invoice View - Create new purchase invoice/waybill"""
    
    def __init__(self, page: ft.Page, api_service: APIService, notification_manager):
        self.page = page
        self.api_service = api_service
        self.notification_manager = notification_manager
        self.suppliers = []
        self.products = []
        self.invoice_items = []
        
        # Form fields
        self.supplier_field = None
        self.invoice_number_field = None
        self.invoice_date_field = None
        self.document_type_field = None
        self.payment_status_field = None
        self.notes_field = None
        self.items_list = None
        self.total_text = None
        self.file_picker = None
        self.document_url = None
        
        # Add item fields
        self.product_field = None
        self.quantity_field = None
        self.unit_price_field = None
        self.tax_rate_field = None
    
    def build(self) -> ft.Control:
        """Build add purchase invoice form"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.ADD_SHOPPING_CART, size=32, color=ft.Colors.BLUE),
            ft.Text("Yeni Alış Faturası / İrsaliyesi", size=32, weight=ft.FontWeight.BOLD),
        ], spacing=10)
        
        # Invoice info fields
        self.supplier_field = ft.Dropdown(
            label="Tedarikçi *",
            options=[],
            border_color=ft.Colors.BLUE_200,
            autofocus=True
        )
        
        self.invoice_number_field = ft.TextField(
            label="Fatura/İrsaliye No *",
            hint_text="FT-2024-001",
            border_color=ft.Colors.BLUE_200
        )
        
        self.invoice_date_field = ft.TextField(
            label="Tarih *",
            hint_text="YYYY-MM-DD",
            value=datetime.now().strftime("%Y-%m-%d"),
            border_color=ft.Colors.BLUE_200
        )
        
        self.document_type_field = ft.Dropdown(
            label="Belge Tipi *",
            options=[
                ft.dropdown.Option("invoice", "Fatura"),
                ft.dropdown.Option("waybill", "İrsaliye"),
            ],
            value="invoice",
            border_color=ft.Colors.BLUE_200
        )
        
        self.payment_status_field = ft.Dropdown(
            label="Ödeme Durumu *",
            options=[
                ft.dropdown.Option("pending", "Beklemede"),
                ft.dropdown.Option("paid", "Ödendi"),
                ft.dropdown.Option("partial", "Kısmi Ödendi"),
            ],
            value="pending",
            border_color=ft.Colors.BLUE_200
        )
        
        self.notes_field = ft.TextField(
            label="Notlar",
            hint_text="Ek bilgiler",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color=ft.Colors.BLUE_200
        )
        
        # File picker for document
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.page.overlay.append(self.file_picker)
        
        # Product selection for items
        self.product_field = ft.Dropdown(
            label="Ürün",
            options=[],
            width=250
        )
        
        self.quantity_field = ft.TextField(
            label="Miktar",
            hint_text="0",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=100
        )
        
        self.unit_price_field = ft.TextField(
            label="Birim Fiyat",
            hint_text="0.00",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=120
        )
        
        self.tax_rate_field = ft.Dropdown(
            label="KDV %",
            options=[
                ft.dropdown.Option("0", "0%"),
                ft.dropdown.Option("1", "1%"),
                ft.dropdown.Option("8", "8%"),
                ft.dropdown.Option("18", "18%"),
                ft.dropdown.Option("20", "20%"),
            ],
            value="18",
            width=100
        )
        
        # Items list
        self.items_list = ft.Column([], spacing=5)
        
        self.total_text = ft.Text(
            "Toplam: ₺0.00",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE
        )
        
        # Form layout
        form_container = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(height=20),
                
                # Invoice info
                ft.Container(
                    content=ft.Column([
                        ft.Text("Fatura Bilgileri", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                        self.supplier_field,
                        ft.Row([self.invoice_number_field, self.invoice_date_field], spacing=10),
                        ft.Row([self.document_type_field, self.payment_status_field], spacing=10),
                        self.notes_field,
                        ft.ElevatedButton(
                            "Belge Yükle (PDF/Resim)",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=lambda e: self.file_picker.pick_files(
                                allowed_extensions=["pdf", "jpg", "jpeg", "png"],
                                dialog_title="Fatura/İrsaliye Belgesi Seç"
                            ),
                            bgcolor=ft.Colors.ORANGE,
                            color=ft.Colors.WHITE
                        ),
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=10
                ),
                
                ft.Container(height=10),
                
                # Add items
                ft.Container(
                    content=ft.Column([
                        ft.Text("Ürün Ekle", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ft.Row([
                            self.product_field,
                            self.quantity_field,
                            self.unit_price_field,
                            self.tax_rate_field,
                            ft.ElevatedButton(
                                "Ekle",
                                icon=ft.Icons.ADD,
                                on_click=self._add_item,
                                bgcolor=ft.Colors.GREEN,
                                color=ft.Colors.WHITE
                            )
                        ], spacing=10),
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10
                ),
                
                ft.Container(height=10),
                
                # Items list
                ft.Container(
                    content=ft.Column([
                        ft.Text("Eklenen Ürünler", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                        self.items_list,
                        ft.Divider(),
                        self.total_text,
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.Colors.ORANGE_50,
                    border_radius=10
                ),
                
                ft.Container(height=20),
                
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        "Kaydet ve Stok Ekle",
                        icon=ft.Icons.SAVE,
                        on_click=self._save_invoice,
                        bgcolor=ft.Colors.BLUE,
                        color=ft.Colors.WHITE,
                        height=45,
                        width=200
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
        """Load suppliers and products"""
        try:
            # Load suppliers
            suppliers_response = self.api_service.get_suppliers()
            self.suppliers = suppliers_response if isinstance(suppliers_response, list) else []
            
            # Load products
            products_response = self.api_service.get_products()
            self.products = products_response if isinstance(products_response, list) else []
            
            self._update_dropdowns()
        except Exception as e:
            self.notification_manager.show_error(f"Veriler yüklenemedi: {e}")
    
    def _update_dropdowns(self):
        """Update supplier and product dropdowns"""
        # Suppliers
        supplier_options = []
        for supplier in self.suppliers:
            supplier_options.append(ft.dropdown.Option(
                str(supplier.get('id')),
                supplier.get('company_name')
            ))
        self.supplier_field.options = supplier_options
        
        # Products
        product_options = []
        for product in self.products:
            product_options.append(ft.dropdown.Option(
                str(product.get('id')),
                product.get('name')
            ))
        self.product_field.options = product_options
        
        self.page.update()
    
    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        """Handle file picker result"""
        if e.files and len(e.files) > 0:
            try:
                with open(e.files[0].path, 'rb') as f:
                    result = self.api_service.upload_purchase_document(f)
                    self.document_url = result.get('url')
                    self.notification_manager.show_success("Belge başarıyla yüklendi")
            except Exception as ex:
                self.notification_manager.show_error(f"Belge yüklenemedi: {ex}")
    
    def _add_item(self, e):
        """Add item to invoice"""
        if not self.product_field.value:
            self.notification_manager.show_error("Ürün seçin")
            return
        
        if not self.quantity_field.value or not self.unit_price_field.value:
            self.notification_manager.show_error("Miktar ve fiyat gerekli")
            return
        
        try:
            product_id = int(self.product_field.value)
            product = next((p for p in self.products if p.get('id') == product_id), None)
            quantity = int(self.quantity_field.value)
            unit_price = float(self.unit_price_field.value)
            tax_rate = int(self.tax_rate_field.value)
            
            subtotal = quantity * unit_price
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount
            
            item = {
                'product_id': product_id,
                'product_name': product.get('name') if product else 'N/A',
                'quantity': quantity,
                'unit_price': unit_price,
                'tax_rate': tax_rate,
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'total': total
            }
            
            self.invoice_items.append(item)
            self._update_items_list()
            
            # Clear fields
            self.product_field.value = ""
            self.quantity_field.value = ""
            self.unit_price_field.value = ""
            self.page.update()
            
        except ValueError:
            self.notification_manager.show_error("Geçersiz değer")
    
    def _update_items_list(self):
        """Update items list display"""
        self.items_list.controls.clear()
        
        grand_total = 0
        for idx, item in enumerate(self.invoice_items):
            grand_total += item['total']
            
            item_row = ft.Container(
                content=ft.Row([
                    ft.Text(f"{item['product_name']}", expand=True),
                    ft.Text(f"{item['quantity']} x ₺{item['unit_price']:.2f}"),
                    ft.Text(f"KDV: %{item['tax_rate']}"),
                    ft.Text(f"₺{item['total']:.2f}", weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        on_click=lambda e, i=idx: self._remove_item(i)
                    )
                ], spacing=10),
                bgcolor=ft.Colors.WHITE,
                padding=10,
                border_radius=5,
                border=ft.border.all(1, ft.Colors.GREY_300)
            )
            self.items_list.controls.append(item_row)
        
        self.total_text.value = f"Toplam: ₺{grand_total:.2f}"
        self.page.update()
    
    def _remove_item(self, index):
        """Remove item from list"""
        if 0 <= index < len(self.invoice_items):
            self.invoice_items.pop(index)
            self._update_items_list()
    
    def _save_invoice(self, e):
        """Save purchase invoice"""
        # Validation
        if not self.supplier_field.value:
            self.notification_manager.show_error("Tedarikçi seçimi gerekli")
            return
        
        if not self.invoice_number_field.value:
            self.notification_manager.show_error("Fatura numarası gerekli")
            return
        
        if not self.invoice_items:
            self.notification_manager.show_error("En az bir ürün ekleyin")
            return
        
        try:
            # Calculate totals
            subtotal = sum(item['subtotal'] for item in self.invoice_items)
            tax_total = sum(item['tax_amount'] for item in self.invoice_items)
            grand_total = sum(item['total'] for item in self.invoice_items)
            
            invoice_data = {
                "supplier_id": int(self.supplier_field.value),
                "invoice_number": self.invoice_number_field.value,
                "invoice_date": self.invoice_date_field.value,
                "document_type": self.document_type_field.value,
                "payment_status": self.payment_status_field.value,
                "subtotal": subtotal,
                "tax_total": tax_total,
                "total_amount": grand_total,
                "notes": self.notes_field.value or None,
                "document_url": self.document_url,
                "items": [
                    {
                        "product_id": item['product_id'],
                        "quantity": item['quantity'],
                        "unit_price": item['unit_price'],
                        "tax_rate": item['tax_rate']
                    }
                    for item in self.invoice_items
                ]
            }
            
            self.api_service.create_purchase_invoice(invoice_data)
            self.notification_manager.show_success("Fatura kaydedildi ve stok güncellendi")
            self._clear_form(None)
        except Exception as ex:
            self.notification_manager.show_error(f"Fatura kaydedilemedi: {ex}")
    
    def _clear_form(self, e):
        """Clear form"""
        self.supplier_field.value = ""
        self.invoice_number_field.value = ""
        self.invoice_date_field.value = datetime.now().strftime("%Y-%m-%d")
        self.document_type_field.value = "invoice"
        self.payment_status_field.value = "pending"
        self.notes_field.value = ""
        self.product_field.value = ""
        self.quantity_field.value = ""
        self.unit_price_field.value = ""
        self.tax_rate_field.value = "18"
        self.invoice_items.clear()
        self.document_url = None
        self._update_items_list()
        self.page.update()
        self.supplier_field.focus()